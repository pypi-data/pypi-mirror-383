# ============================
# storage_backend.py (updated)
# ============================
from __future__ import annotations

import os
import json
import pickle
import sqlite3
from abc import ABC, abstractmethod
from typing import Any, Dict, Iterable, Iterator, List, Optional, Sequence, Union, Tuple

import h5py
import numpy as np

StorageType = Union[List[Any], Dict[int, Any]]

class StorageBackend(ABC):
    """
    Abstract interface for container storage backends.

    Notes
    -----
    - `add` accepts an optional `metadata` mapping. Backends that do not use metadata
      may ignore it.
    - `get(obj_id=None)` may return a *lazy sequence* view (rather than a concrete list)
      when `obj_id` is None, to avoid loading everything into RAM. Code that needs a real
      list can call `list(...)` on that view.
    """

    @abstractmethod
    def add(self, obj: Any, metadata: Optional[Dict[str, Any]] = None) -> int:
        """Store object and return its integer ID."""
        raise NotImplementedError

    @abstractmethod
    def get(self, obj_id: Optional[int] = None):
        """
        Retrieve object by ID. If `obj_id` is None, return a *lazy* container view
        over all objects (implementing `__len__`, `__iter__`, and `__getitem__`).
        """
        raise NotImplementedError

    @abstractmethod
    def remove(self, obj_id: int) -> None:
        """Delete object by ID (no-op if already deleted)."""
        raise NotImplementedError

    @abstractmethod
    def list_ids(self) -> List[int]:
        """Return list of all object IDs (ascending)."""
        raise NotImplementedError

    @abstractmethod
    def count(self) -> int:
        """Return total number of stored objects."""
        raise NotImplementedError

    @abstractmethod
    def clear(self) -> None:
        """Remove all objects from the store."""
        raise NotImplementedError

    # ---------- Optional (metadata-aware) API ----------
    def get_meta(self, obj_id: int) -> Dict[str, Any]:  # pragma: no cover (optional)
        raise NotImplementedError

    def set_meta(self, obj_id: int, meta: Dict[str, Any]) -> None:  # pragma: no cover
        raise NotImplementedError

    def query_ids(self, where: str, params: Sequence[Any] = ()) -> List[int]:  # pragma: no cover
        """SQL-like query support (if available)."""
        raise NotImplementedError

    # ---------- Convenience iteration (can be overridden) ----------
    def iter_ids(self, batch_size: Optional[int] = None) -> Iterator[int]:
        for cid in self.list_ids():
            yield cid

    def iter_objects(self, batch_size: Optional[int] = None) -> Iterator[tuple[int, Any]]:
        for cid in self.iter_ids(batch_size):
            yield cid, self.get(cid)


# -----------------------------
# In-memory (list/dict) backend
# -----------------------------
class MemoryStorage(StorageBackend):
    """
    Generic in-memory storage.

    The container can be either a list (sequential storage) or a dict that maps
    integer IDs to objects. IDs are always integers.
    """

    def __init__(self, initial: StorageType | None = None) -> None:
        self._data: StorageType = initial if initial is not None else []
        self._meta: Dict[int, Dict[str, Any]] = {}

    def add(self, obj: Any, metadata: Optional[Dict[str, Any]] = None) -> int:
        if isinstance(self._data, list):
            self._data.append(obj)
            idx = len(self._data) - 1
        else:
            idx = max(self._data.keys(), default=-1) + 1
            self._data[idx] = obj
        if metadata is not None:
            self._meta[idx] = metadata
        return idx

    def set(self, container: StorageType) -> int:
        if not isinstance(container, (list, dict)):
            raise TypeError("container must be a list or a dict[int, Any]")
        self._data = container
        self._meta.clear()
        return len(self._data) - 1 if isinstance(self._data, list) else (max(self._data.keys(), default=-1))

    def remove(self, obj_id: int) -> None:
        try:
            del self._data[obj_id]
        except (IndexError, KeyError):
            raise KeyError(f"No object found with id {obj_id}") from None
        self._meta.pop(obj_id, None)

    def get(self, obj_id: Optional[int] = None):
        if obj_id is None:
            return self._data
        try:
            return self._data[obj_id]
        except (IndexError, KeyError):
            raise KeyError(f"No object found with id {obj_id}") from None

    def list_ids(self) -> List[int]:
        return list(range(len(self._data))) if isinstance(self._data, list) else list(self._data.keys())

    def count(self) -> int:
        return len(self._data)

    def clear(self) -> None:
        if isinstance(self._data, list):
            self._data.clear()
        else:
            self._data = {}
        self._meta.clear()

    # Optional metadata helpers
    def get_meta(self, obj_id: int) -> Dict[str, Any]:
        return dict(self._meta.get(obj_id, {}))

    def set_meta(self, obj_id: int, meta: Dict[str, Any]) -> None:
        self._meta[obj_id] = dict(meta)

# -----------------------------
# SQLite (pickle BLOB) backend
# -----------------------------
class SQLiteStorage(StorageBackend):
    """SQLite-based storage, pickling objects into a BLOB."""

    def __init__(self, db_path: str):
        dir_path = os.path.dirname(db_path)
        if dir_path:
            os.makedirs(dir_path, exist_ok=True)
        self.conn = sqlite3.connect(db_path, check_same_thread=False)
        self._init_schema()

    def _init_schema(self) -> None:
        cur = self.conn.cursor()
        cur.execute(
            """
            CREATE TABLE IF NOT EXISTS containers (
                id   INTEGER PRIMARY KEY AUTOINCREMENT,
                data BLOB NOT NULL
            );
            """
        )
        self.conn.commit()

    def add(self, obj: Any, metadata: Optional[Dict[str, Any]] = None) -> int:
        blob = pickle.dumps(obj)
        cur = self.conn.cursor()
        cur.execute("INSERT INTO containers (data) VALUES (?);", (blob,))
        self.conn.commit()
        return int(cur.lastrowid)

    def get(self, obj_id: Optional[int] = None):
        if obj_id is None:
            # Return a lightweight proxy of all objects (loads on iteration)
            return _LazySQLiteView(self)
        cur = self.conn.cursor()
        cur.execute("SELECT data FROM containers WHERE id = ?;", (obj_id,))
        row = cur.fetchone()
        if row is None:
            raise KeyError(f"No container with id {obj_id}")
        return pickle.loads(row[0])

    def remove(self, obj_id: int) -> None:
        cur = self.conn.cursor()
        cur.execute("DELETE FROM containers WHERE id = ?;", (obj_id,))
        if cur.rowcount == 0:
            raise KeyError(f"No container with id {obj_id}")
        self.conn.commit()

    def list_ids(self) -> List[int]:
        cur = self.conn.cursor()
        cur.execute("SELECT id FROM containers ORDER BY id ASC;")
        return [int(row[0]) for row in cur.fetchall()]

    def count(self) -> int:
        cur = self.conn.cursor()
        cur.execute("SELECT COUNT(*) FROM containers;")
        return int(cur.fetchone()[0])

    def clear(self) -> None:
        cur = self.conn.cursor()
        cur.execute("DELETE FROM containers;")
        self.conn.commit()

    def iter_ids(self, batch_size: Optional[int] = 1000) -> Iterator[int]:
        cur = self.conn.cursor()
        last = 0
        while True:
            if batch_size:
                cur.execute(
                    "SELECT id FROM containers WHERE id > ? ORDER BY id ASC LIMIT ?;",
                    (last, batch_size),
                )
            else:
                cur.execute(
                    "SELECT id FROM containers WHERE id > ? ORDER BY id ASC;",
                    (last,),
                )
            rows = cur.fetchall()
            if not rows:
                break
            for (cid,) in rows:
                yield int(cid)
            last = int(rows[-1][0])

class _LazySQLiteView:
    """Lazy sequence-like view over all objects in SQLiteStorage."""

    def __init__(self, store: SQLiteStorage):
        self._s = store

    def __len__(self) -> int:
        return self._s.count()

    def __iter__(self):
        for cid in self._s.iter_ids():
            yield self._s.get(cid)

    def __getitem__(self, i):
        if isinstance(i, slice):
            ids = self._s.list_ids()[i]
            return [self._s.get(cid) for cid in ids]
        else:
            cid = self._s.list_ids()[i]
            return self._s.get(cid)


# -----------------------------
# Hybrid (HDF5 + SQLite) backend
# -----------------------------
"""IO/storage_backend.py

Hybrid storage backend combining SQLite (index + metadata) and HDF5 (object
payloads) for efficient, scalable persistence of Python objects related to
atomistic simulations.

This module provides the :class:`HybridStorage` class, which stores a pickled
payload per object in an HDF5 dataset and mirrors essential metadata (energy,
atom count, composition, empirical formula) in a lightweight SQLite schema to
enable fast queries without loading full objects.

Design goals:
    * **Performance**: metadata queries are served from SQLite indices; payloads
      are compressed with gzip inside HDF5 for efficient disk usage.
    * **Convenience**: automatic extraction of energy and species labels from
      common attribute names (e.g., ``obj.E`` or
      ``obj.AtomPositionManager.atomLabelsList``).
    * **Stability**: robust to arrays or scalars for energies and labels.

Notes:
    - The composition table uses an Entity–Attribute–Value (EAV) layout to
      efficiently query per-species counts across objects.
    - Formulas are rendered with alphabetical element ordering for simplicity.

Example:
    >>> store = HybridStorage("./hybrid_store")
    >>> obj_id = store.add(obj)  # obj carries .E and AtomPositionManager
    >>> meta = store.get_meta(obj_id)
    >>> payload = store.get(obj_id)

"""
class HybridStorage:
    """
    Hybrid backend:
      - SQLite: index + metadata (species registry, compositions, scalars)
      - HDF5:   payload pickled & compressed
    Guarantees:
      - Stable species-to-column mapping via `species.rank` (first-seen order).
      - Sparse compositions, dense export on request.
      - Generic scalar store (E, E1, E2, ...).
    """


    """Hybrid SQLite + HDF5 object store.

    The storage model separates **metadata** (SQLite) from **payloads** (HDF5):

    - *SQLite* stores: ``id``, ``energy``, ``natoms``, ``formula``, and a JSON
      blob ``meta_json`` (currently including the composition map). A second
      table, ``compositions(object_id, species, count)``, holds an EAV view of
      per-species counts to enable selective queries.
    - *HDF5* stores: one dataset per object under the group ``/objs`` named as
      zero-padded IDs (``00000001``, ...). Each dataset contains the raw pickled
      bytes and carries attributes for quick inspection (``id``, ``energy`` when
      available).

    Attributes:
        root_dir: Absolute path to the storage root directory.
        h5_path: File path to the HDF5 file (``objects.h5``).
        sqlite_path: File path to the SQLite index (``index.sqlite``).

    Forward-looking:
        The schema leaves room for additional indices (e.g., ranges over energy
        or natoms) and user-defined metadata; ``meta_json`` can be extended
        without schema migration.
    """
    # scalar keys we auto-pick if present as numeric attrs in SingleRun/APM
    _SCALAR_PREFIXES = ("E", "energy", "Etot", "Ef", "free_energy")

    def __init__(self, root_dir: str = "./hybrid_store", access: str = "rw"):
        """
        access: 'rw' (default) or 'ro'
        """
        if access not in ("rw", "ro"):
            raise ValueError("access must be 'rw' or 'ro'")
        self.read_only = (access == "ro")

        self.root_dir = os.path.abspath(root_dir)
        os.makedirs(self.root_dir, exist_ok=True)

        self.h5_path = os.path.join(self.root_dir, "objects.h5")
        self.sqlite_path = os.path.join(self.root_dir, "index.sqlite")

        # --- SQLite ---
        if self.read_only:
            # Read-only URI; do not mutate schema
            self._conn = sqlite3.connect(f"file:{self.sqlite_path}?mode=ro",
                                         uri=True, check_same_thread=False)
            self._conn.execute("PRAGMA foreign_keys = ON;")
        else:
            self._conn = sqlite3.connect(self.sqlite_path, check_same_thread=False)
            self._conn.execute("PRAGMA foreign_keys = ON;")
            self._init_schema()

        # --- HDF5 ---
        h5_mode = "r" if self.read_only else "a"
        self._h5 = h5py.File(self.h5_path, h5_mode)
        # Ensure the group exists in RW; in RO, require it to be present
        if self.read_only:
            if "objs" not in self._h5:
                raise RuntimeError("Read-only open requires existing 'objs' group in HDF5.")
            self._grp = self._h5["objs"]
        else:
            self._grp = self._h5.require_group("objs")

    # Guard for any mutating method
    def _assert_writable(self):
        if self.read_only:
            raise RuntimeError("HybridStorage is read-only; writing is not allowed.")

    # ---------------- Schema ----------------
    def _init_schema(self):
        cur = self._conn.cursor()
        cur.execute("""
            CREATE TABLE IF NOT EXISTS species (
                species_id INTEGER PRIMARY KEY AUTOINCREMENT,
                symbol     TEXT UNIQUE NOT NULL,
                rank       INTEGER NOT NULL
            );
        """)
        cur.execute("""
            CREATE TABLE IF NOT EXISTS objects (
                id        INTEGER PRIMARY KEY AUTOINCREMENT,
                energy    REAL,
                natoms    INTEGER,
                formula   TEXT,
                meta_json TEXT
            );
        """)
        cur.execute("""
            CREATE TABLE IF NOT EXISTS compositions (
                object_id INTEGER NOT NULL,
                species_id INTEGER NOT NULL,
                count     REAL NOT NULL,
                PRIMARY KEY (object_id, species_id),
                FOREIGN KEY (object_id) REFERENCES objects(id) ON DELETE CASCADE,
                FOREIGN KEY (species_id) REFERENCES species(species_id) ON DELETE RESTRICT
            );
        """)
        cur.execute("""
            CREATE TABLE IF NOT EXISTS scalars (
                object_id INTEGER NOT NULL,
                key       TEXT    NOT NULL,
                value     REAL,
                PRIMARY KEY (object_id, key),
                FOREIGN KEY (object_id) REFERENCES objects(id) ON DELETE CASCADE
            );
        """)
        cur.execute("CREATE INDEX IF NOT EXISTS idx_objects_energy ON objects(energy);")
        cur.execute("CREATE INDEX IF NOT EXISTS idx_comp_sp ON compositions(species_id);")
        cur.execute("CREATE INDEX IF NOT EXISTS idx_scalars_key ON scalars(key);")
        self._conn.commit()

    # ---------------- Helpers ----------------
    @staticmethod
    def _to_float_or_none(x) -> Optional[float]:
        try:
            import numpy as _np
            if isinstance(x, _np.ndarray):
                if x.size == 0:
                    return None
                return float(x.reshape(-1)[0])
            if isinstance(x, (_np.floating, _np.integer)):
                return float(x)
        except Exception:
            pass
        if isinstance(x, (int, float)):
            return float(x)
        return None

    @staticmethod
    def _is_scalar(x) -> bool:
        try:
            import numpy as _np
            if isinstance(x, (int, float, _np.integer, _np.floating)):
                return True
            if isinstance(x, _np.ndarray) and x.ndim == 0:
                return True
        except Exception:
            pass
        return False

    @classmethod
    def _extract_scalars(cls, obj: Any) -> Dict[str, float]:
        """Collect numeric scalar attrs from obj and obj.AtomPositionManager whose names
        start with allowed prefixes. Returns a {key: float} dict."""
        out: Dict[str, float] = {}
        def _harvest(ns: Dict[str, Any]):
            for k, v in ns.items():
                k_lower = k.lower()
                if not any(k_lower.startswith(p.lower()) for p in cls._SCALAR_PREFIXES):
                    continue
                val = v
                try:
                    import numpy as _np
                    if isinstance(v, _np.ndarray):
                        if v.size == 0: 
                            continue
                        if v.ndim == 0:
                            val = float(v.item())
                        else:
                            # prefer first element convention
                            val = float(v.ravel()[0])
                    else:
                        if cls._is_scalar(v):
                            val = float(v)
                        else:
                            continue
                except Exception:
                    continue
                out[str(k)] = float(val)

        try:
            _harvest(getattr(obj, "__dict__", {}))
        except Exception:
            pass
        apm = getattr(obj, "AtomPositionManager", None)
        if apm is not None:
            try:
                _harvest(getattr(apm, "__dict__", {}))
            except Exception:
                pass
        return out

    @staticmethod
    def _extract_labels(obj: Any) -> List[str]:
        apm = getattr(obj, "AtomPositionManager", None)
        if apm is None:
            return []
        labels = getattr(apm, "atomLabelsList", None)
        if labels is None:
            labels = getattr(apm, "_atomLabelsList", None)
        if labels is None:
            return []
        try:
            import numpy as _np
            if isinstance(labels, _np.ndarray):
                return [str(x) for x in labels.tolist()]
        except Exception:
            pass
        return [str(x) for x in labels]

    @staticmethod
    def _extract_energy(obj: Any) -> Optional[float]:
        apm = getattr(obj, "AtomPositionManager", None)
        if apm is None:
            return None
        for name in ("energy", "_energy", "E", "_E"):
            val = getattr(apm, name, None)
            f = HybridStorage._to_float_or_none(val)
            if f is not None:
                return f
        return None

    @staticmethod
    def _extract_free_energy(obj: Any) -> Optional[float]:
        apm = getattr(obj, "AtomPositionManager", None)
        if apm is None:
            return None
        metadata = getattr(apm, "metadata", None)
        if isinstance(metadata, dict) and "F" in metadata:
            return HybridStorage._to_float_or_none(metadata["F"])
        return None


    def _ensure_species(self, symbol: str) -> int:
        cur = self._conn.cursor()
        # try fast path
        cur.execute("SELECT species_id FROM species WHERE symbol=?;", (symbol,))
        row = cur.fetchone()
        if row:
            return int(row[0])
        # assign next rank = max(rank)+1
        cur.execute("SELECT COALESCE(MAX(rank), -1) + 1 FROM species;")
        next_rank = int(cur.fetchone()[0])
        cur.execute("INSERT INTO species(symbol, rank) VALUES(?,?);", (symbol, next_rank))
        self._conn.commit()
        return int(cur.lastrowid)

    @staticmethod
    def _formula_from_counts(counts: Dict[str, float]) -> str:
        # ordered by symbol alphabetically for normalized display (mapping is separate)
        parts = []
        for sp in sorted(counts):
            c = counts[sp]
            c = int(round(c)) if abs(c - round(c)) < 1e-8 else c
            parts.append(f"{sp}{'' if c == 1 else c}")
        return "".join(parts)

    def _save_payload_h5(self, obj_id: int, obj: Any):
        blob = pickle.dumps(obj, protocol=pickle.HIGHEST_PROTOCOL)
        arr = np.frombuffer(blob, dtype=np.uint8)
        dname = f"{obj_id:08d}"
        if dname in self._grp:
            del self._grp[dname]
        self._grp.create_dataset(dname, data=arr, compression="gzip", shuffle=True)
        ds = self._grp[dname]
        # convenience attrs
        scal = self._extract_scalars(obj)
        if "E" in scal:
            ds.attrs["E"] = float(scal["E"])
        ds.attrs["id"] = int(obj_id)

    def _load_payload_h5(self, obj_id: int) -> Any:
        dname = f"{obj_id:08d}"
        if dname not in self._grp:
            raise KeyError(f"HDF5 dataset not found for id {obj_id}")
        arr = np.array(self._grp[dname][...], dtype=np.uint8)
        return pickle.loads(arr.tobytes())

    # ---------------- Public API ----------------
    def add(self, obj: Any) -> int:
        self._assert_writable()

        labels = self._extract_labels(obj)
        natoms = len(labels) if labels else None

        counts: Dict[str, float] = {}
        for s in labels:
            counts[s] = counts.get(s, 0.0) + 1.0
        formula = self._formula_from_counts(counts) if counts else None

        scalars = self._extract_scalars(obj)
        energy = self._extract_energy(obj)
        free_energy = self._extract_free_energy(obj)

        meta_payload = {"composition": counts}
        if free_energy is not None:
            meta_payload["free_energy"] = free_energy

        cur = self._conn.cursor()
        cur.execute(
            "INSERT INTO objects (energy, natoms, formula, meta_json) VALUES (?,?,?,?);",
            (energy, natoms, formula, json.dumps(meta_payload))
        )
        obj_id = int(cur.lastrowid)

        if counts:
            rows = []
            for sym, ct in counts.items():
                spid = self._ensure_species(sym)
                rows.append((obj_id, spid, float(ct)))
            cur.executemany(
                "INSERT INTO compositions(object_id, species_id, count) VALUES (?,?,?);",
                rows
            )

        if scalars:
            cur.executemany(
                "INSERT INTO scalars(object_id, key, value) VALUES (?,?,?);",
                [(obj_id, k, float(v)) for k, v in scalars.items()]
            )

        self._conn.commit()
        self._save_payload_h5(obj_id, obj)
        self._h5.flush()
        return obj_id

    def get(self, obj_id: int):
        return self._load_payload_h5(int(obj_id))

    def remove(self, obj_id: int) -> None:
        self._assert_writable()

        obj_id = int(obj_id)
        # HDF5
        dname = f"{obj_id:08d}"
        if dname in self._grp:
            del self._grp[dname]
        # SQL
        cur = self._conn.cursor()
        cur.execute("DELETE FROM objects WHERE id=?;", (obj_id,))
        self._conn.commit()

    def list_ids(self) -> List[int]:
        cur = self._conn.cursor()
        cur.execute("SELECT id FROM objects ORDER BY id ASC;")
        return [int(r[0]) for r in cur.fetchall()]

    def count(self) -> int:
        cur = self._conn.cursor()
        cur.execute("SELECT COUNT(*) FROM objects;")
        return int(cur.fetchone()[0])

    def clear(self) -> None:
        self._assert_writable()

        # SQL
        cur = self._conn.cursor()
        cur.execute("DELETE FROM compositions;")
        cur.execute("DELETE FROM scalars;")
        cur.execute("DELETE FROM objects;")
        self._conn.commit()
        # HDF5
        for k in list(self._grp.keys()):
            del self._grp[k]
        self._h5.flush()

    def iter_ids(self, batch_size: Optional[int] = 1000):
        cur = self._conn.cursor()
        last = 0
        while True:
            if batch_size:
                cur.execute(
                    "SELECT id FROM objects WHERE id > ? ORDER BY id ASC LIMIT ?;",
                    (last, batch_size)
                )
            else:
                cur.execute(
                    "SELECT id FROM objects WHERE id > ? ORDER BY id ASC;",
                    (last,)
                )
            rows = cur.fetchall()
            if not rows:
                break
            for (cid,) in rows:
                yield int(cid)
            last = int(rows[-1][0])

    def iter_objects(self, batch_size: Optional[int] = 1000):
        for cid in self.iter_ids(batch_size=batch_size):
            yield cid, self.get(cid)

    # ---------------- Fast metadata access ----------------
    def get_species_universe(self, order: str = "stored") -> List[str]:
        """All species present. order='stored' (first-seen) or 'alphabetical'."""
        cur = self._conn.cursor()
        if order == "alphabetical":
            cur.execute("SELECT symbol FROM species ORDER BY symbol ASC;")
        else:
            cur.execute("SELECT symbol FROM species ORDER BY rank ASC;")
        return [r[0] for r in cur.fetchall()]

    def get_species_mapping(self, order: str = "stored") -> Dict[str, int]:
        """Symbol → column index mapping for dense composition matrices."""
        syms = self.get_species_universe(order=order)
        return {s: i for i, s in enumerate(syms)}

    def get_all_compositions(
        self,
        species_order: Optional[Sequence[str]] = None,
        return_species: bool = False,
        order: str = "stored",
    ):
        """
        Dense (n_samples, n_species) composition matrix in the requested species order.
        If species_order is None, uses order='stored' (first-seen stable).
        """
        cur = self._conn.cursor()
        # list of object ids, stable order
        cur.execute("SELECT id FROM objects ORDER BY id ASC;")
        ids = [int(r[0]) for r in cur.fetchall()]
        n = len(ids)
        if n == 0:
            res = np.zeros((0, 0), dtype=float)
            return (res, []) if return_species else res

        if species_order is None:
            species_order = self.get_species_universe(order=order)
        species_order = list(species_order)
        m = len(species_order)
        id_to_row = {oid: i for i, oid in enumerate(ids)}
        sp_to_col = {sp: j for j, sp in enumerate(species_order)}

        # join compositions with species symbols
        cur.execute("""
            SELECT c.object_id, s.symbol, c.count
            FROM compositions c
            JOIN species s ON s.species_id = c.species_id;
        """)
        M = np.zeros((n, m), dtype=float)
        for oid, sym, ct in cur.fetchall():
            i = id_to_row.get(int(oid))
            j = sp_to_col.get(sym)
            if i is not None and j is not None:
                try:
                    M[i, j] = float(ct)
                except Exception:
                    pass

        return (M, species_order) if return_species else M

    def get_scalar_keys_universe(self) -> List[str]:
        cur = self._conn.cursor()
        cur.execute("SELECT DISTINCT key FROM scalars ORDER BY key ASC;")
        return [r[0] for r in cur.fetchall()]

    def get_all_scalars(
        self,
        keys: Optional[Sequence[str]] = None,
        return_keys: bool = False
    ):
        """
        Dense (n_samples, n_keys) matrix of numeric scalar properties.
        Missing values are np.nan. Rows follow objects.id ascending.
        """
        cur = self._conn.cursor()
        cur.execute("SELECT id FROM objects ORDER BY id ASC;")
        ids = [int(r[0]) for r in cur.fetchall()]
        n = len(ids)
        if n == 0:
            res = np.zeros((0, 0), dtype=float)
            return (res, []) if return_keys else res

        if keys is None:
            keys = self.get_scalar_keys_universe()
        keys = list(keys)
        k = len(keys)
        id_to_row = {oid: i for i, oid in enumerate(ids)}
        key_to_col = {key: j for j, key in enumerate(keys)}

        A = np.full((n, k), np.nan, dtype=float)
        # fill from scalars
        cur.execute("SELECT object_id, key, value FROM scalars;")
        for oid, key, val in cur.fetchall():
            i = id_to_row.get(int(oid))
            j = key_to_col.get(key)
            if i is not None and j is not None and val is not None:
                A[i, j] = float(val)

        return (A, keys) if return_keys else A

    def get_all_energies(self) -> np.ndarray:
        """Convenience: objects.energy column; if empty, fallback to scalar 'E'."""
        cur = self._conn.cursor()
        cur.execute("SELECT energy FROM objects ORDER BY id ASC;")
        vals = [r[0] for r in cur.fetchall()]
        arr = np.array([v for v in vals if v is not None], dtype=float)
        if arr.size > 0:
            return arr
        # fallback
        A, keys = self.get_all_scalars(keys=["E"], return_keys=True)
        return A[:, 0] if A.size else np.array([], dtype=float)

    # Debug/meta
    def get_meta(self, obj_id: int) -> Dict[str, Any]:
        cur = self._conn.cursor()
        cur.execute("SELECT energy, natoms, formula, meta_json FROM objects WHERE id=?;", (int(obj_id),))
        row = cur.fetchone()
        if row is None:
            raise KeyError(f"No object with id {obj_id}")
        energy, natoms, formula, meta_json = row
        meta = json.loads(meta_json) if meta_json else {}
        meta.update(dict(energy=energy, natoms=natoms, formula=formula))
        return meta

    def close(self):
        try:
            self._h5.flush(); self._h5.close()
        except Exception:
            pass
        try:
            self._conn.close()
        except Exception:
            pass

    # ---- maintenance ----
    def compact_hdf5(self, new_path: Optional[str] = None) -> str:
        self._assert_writable()
        self._h5.flush()
        src = self.h5_path
        dst = new_path or (self.h5_path + ".compact")
        with h5py.File(dst, "w") as out:
            out.copy(self._grp, "objs")
        if new_path is None:
            self._h5.close()
            os.replace(dst, src)
            self._h5 = h5py.File(src, "a")
            self._grp = self._h5["objs"]
            return src
        return dst


class _LazyHybridView:
    """Lazy sequence-like view over all objects in HybridStorage."""

    def __init__(self, store: HybridStorage):
        self._s = store

    def __len__(self) -> int:
        return self._s.count()

    def __iter__(self):
        for cid in self._s.iter_ids():
            yield self._s.get(cid)

    def __getitem__(self, i):
        if isinstance(i, slice):
            ids = self._s.list_ids()[i]
            return [self._s.get(cid) for cid in ids]
        else:
            cid = self._s.list_ids()[i]
            return self._s.get(cid)

def merge_hybrid_stores(main_root: str, agent_roots: Sequence[str]) -> None:
    """
    One-shot consolidation of multiple HybridStorage roots into a single main root.
    - Copies rows in SQLite tables (objects, compositions, scalars).
    - Rewrites species references using the symbol (robust to different species_id mappings).
    - Copies HDF5 payloads (pickled objects) to new autoincremented IDs in main.
    - Commits per agent; safe to run once after all agents finish.

    Parameters
    ----------
    main_root : str
        Target HybridStorage root directory to consolidate into (must be writable).
    agent_roots : Sequence[str]
        List of source HybridStorage root directories produced by agents.

    Notes
    -----
    * This function does NOT deduplicate payloads. If you need de-dup, add a
      content hash (e.g., SHA-256 of the payload) to meta_json and skip repeats.
    * Do not run concurrently from multiple processes.
    """
    main_root_abs = os.path.abspath(main_root)
    main = HybridStorage(main_root_abs)  # opens RW in your current implementation
    try:
        cur_main = main._conn.cursor()

        for agent_root in agent_roots:
            if agent_root is None:
                continue
            agent_root_abs = os.path.abspath(agent_root)
            # Skip accidental self-merge
            if agent_root_abs == main_root_abs:
                continue
            # Skip non-existent or empty roots gracefully
            if not os.path.isdir(agent_root_abs):
                continue

            agent = None
            try:
                agent = HybridStorage(agent_root_abs)  # opens RW in current code; we'll only read
                cur_agent = agent._conn.cursor()

                # Iterate agent objects in stable order
                cur_agent.execute(
                    "SELECT id, energy, natoms, formula, meta_json "
                    "FROM objects ORDER BY id ASC;"
                )
                rows = cur_agent.fetchall()
                if not rows:
                    continue

                # Single transaction per agent for speed and atomicity
                cur_main.execute("BEGIN;")

                for oid, energy, natoms, formula, meta_json in rows:
                    # 1) Insert into main.objects
                    cur_main.execute(
                        "INSERT INTO objects (energy, natoms, formula, meta_json) VALUES (?,?,?,?);",
                        (energy, natoms, formula, meta_json),
                    )
                    new_id = int(cur_main.lastrowid)

                    # 2) compositions: remap by symbol → species_id in main
                    cur_agent.execute(
                        """
                        SELECT s.symbol, c.count
                        FROM compositions c
                        JOIN species s ON s.species_id = c.species_id
                        WHERE c.object_id = ?;
                        """,
                        (int(oid),),
                    )
                    comp_rows = cur_agent.fetchall()
                    if comp_rows:
                        rows_to_insert = []
                        for sym, ct in comp_rows:
                            spid = main._ensure_species(sym)  # creates if missing
                            rows_to_insert.append((new_id, spid, float(ct)))
                        cur_main.executemany(
                            "INSERT INTO compositions(object_id, species_id, count) VALUES (?,?,?);",
                            rows_to_insert,
                        )

                    # 3) scalars: straight copy
                    cur_agent.execute(
                        "SELECT key, value FROM scalars WHERE object_id = ?;",
                        (int(oid),),
                    )
                    scal_rows = cur_agent.fetchall()
                    if scal_rows:
                        cur_main.executemany(
                            "INSERT INTO scalars(object_id, key, value) VALUES (?,?,?);",
                            [(new_id, k, v) for (k, v) in scal_rows],
                        )

                    # 4) payload: load from agent HDF5, store in main HDF5
                    obj = agent.get(int(oid))
                    main._save_payload_h5(new_id, obj)

                # Commit per agent and flush datasets
                main._conn.commit()
                main._h5.flush()

            finally:
                if agent is not None:
                    agent.close()

    finally:
        main.close()
