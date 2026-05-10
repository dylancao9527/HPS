from dataclasses import dataclass
from pathlib import Path
import pickle
import shutil


def serialize_prophet_model(model) -> bytes:
    """Pickle a fitted Prophet model to bytes."""
    return pickle.dumps(model, protocol=pickle.HIGHEST_PROTOCOL)


def deserialize_prophet_model(blob: bytes):
    """Restore a Prophet model from pickled bytes."""
    return pickle.loads(blob)


@dataclass(frozen=True)
class StoredProphetBundle:
    storage_key: str
    sys_model_blob: bytes
    dia_model_blob: bytes


def is_legacy_prophet_storage_key(storage_key: str) -> bool:
    parts = str(storage_key or "").replace("\\", "/").split("/")
    return len(parts) >= 2 and parts[1].startswith("fd_")


class LocalProphetModelStore:
    def __init__(self, root):
        self.root = Path(root)
        self._resolved_root = self.root.resolve()

    def build_storage_key(self, *, user_id, model_version, data_signature):
        return f"user_{user_id}/{model_version}/{data_signature}"

    def _bundle_dir(self, storage_key: str) -> Path:
        raw_key = str(storage_key or "").strip()
        parts = raw_key.replace("\\", "/").split("/")
        if (
            not raw_key
            or Path(raw_key).is_absolute()
            or any(part in {"", ".", ".."} or ":" in part for part in parts)
        ):
            raise ValueError("Invalid Prophet storage key")

        bundle_dir = (self._resolved_root / Path(*parts)).resolve()
        if not bundle_dir.is_relative_to(self._resolved_root):
            raise ValueError("Invalid Prophet storage key")
        return bundle_dir

    def write_bundle(self, storage_key: str, sys_model_blob: bytes, dia_model_blob: bytes) -> StoredProphetBundle:
        bundle_dir = self._bundle_dir(storage_key)
        bundle_dir.mkdir(parents=True, exist_ok=True)
        (bundle_dir / "sys_model.pkl").write_bytes(sys_model_blob)
        (bundle_dir / "dia_model.pkl").write_bytes(dia_model_blob)
        return StoredProphetBundle(
            storage_key=storage_key,
            sys_model_blob=sys_model_blob,
            dia_model_blob=dia_model_blob,
        )

    def read_bundle(self, storage_key: str) -> StoredProphetBundle:
        bundle_dir = self._bundle_dir(storage_key)
        return StoredProphetBundle(
            storage_key=storage_key,
            sys_model_blob=(bundle_dir / "sys_model.pkl").read_bytes(),
            dia_model_blob=(bundle_dir / "dia_model.pkl").read_bytes(),
        )

    def exists(self, storage_key: str) -> bool:
        bundle_dir = self._bundle_dir(storage_key)
        return (bundle_dir / "sys_model.pkl").exists() and (bundle_dir / "dia_model.pkl").exists()

    def delete_bundle(self, storage_key: str) -> None:
        bundle_dir = self._bundle_dir(storage_key)
        if bundle_dir.exists():
            shutil.rmtree(bundle_dir)

    def list_storage_keys(self) -> list[str]:
        if not self.root.exists():
            return []
        keys: set[str] = set()
        for path in self.root.glob("user_*/*/*"):
            if not path.is_dir():
                continue
            relative = path.relative_to(self.root)
            parts = relative.parts
            if len(parts) == 3 and not parts[1].startswith("fd_"):
                keys.add(str(relative).replace("\\", "/"))
        return sorted(keys)

    def list_legacy_storage_keys(self) -> list[str]:
        if not self.root.exists():
            return []
        return sorted(
            str(path.relative_to(self.root)).replace("\\", "/")
            for path in self.root.glob("user_*/fd_*/*/*")
            if path.is_dir()
        )
