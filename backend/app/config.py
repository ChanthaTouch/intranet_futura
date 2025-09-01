import os
_TOML_BIN = False
try:
    import tomllib as _toml_reader  # Python 3.11+
    _TOML_BIN = True
except Exception:
    try:
        import tomli as _toml_reader  # Backport for Python <=3.10
        _TOML_BIN = True
    except Exception:
        import toml as _toml_reader   # Fallback (expects text file handle)
        _TOML_BIN = False

from dataclasses import dataclass, field
from typing import List

@dataclass
class AppConfig:
    name: str = "Futura Intranet"
    debug: bool = True
    base_url: str = "http://localhost:8000"

@dataclass
class SecurityConfig:
    jwt_secret: str = "CHANGE_ME_SUPER_SECRET"
    access_token_exp_minutes: int = 60

@dataclass
class DBConfig:
    # MariaDB root connection
    dsn: str = "mysql+asyncmy://root:Chantha123!@localhost:3306/intranet_futura"

@dataclass
class StorageConfig:
    files_dir: str = "./var/files"
    public_base: str = "http://localhost:8000/public"

@dataclass
class CORSConfig:
    allow_origins: List[str] = field(default_factory=lambda: [
        "http://localhost:5173",
        "http://127.0.0.1:5173"
    ])

@dataclass
class Config:
    app: AppConfig = field(default_factory=AppConfig)
    security: SecurityConfig = field(default_factory=SecurityConfig)
    database: DBConfig = field(default_factory=DBConfig)
    storage: StorageConfig = field(default_factory=StorageConfig)
    cors: CORSConfig = field(default_factory=CORSConfig)

def _load_toml(path: str) -> dict:
    mode = "rb" if _TOML_BIN else "r"
    with open(path, mode) as f:
        return _toml_reader.load(f)

def load_config() -> Config:
    cfg = Config()
    here = os.path.dirname(__file__)
    for fname in ("../config.toml", "../config.local.toml"):
        path = os.path.join(here, fname)
        if os.path.exists(path):
            data = _load_toml(path)
            for sect, vals in data.items():
                if hasattr(cfg, sect):
                    sec_obj = getattr(cfg, sect)
                    for k, v in vals.items():
                        if hasattr(sec_obj, k):
                            setattr(sec_obj, k, v)
    os.makedirs(cfg.storage.files_dir, exist_ok=True)
    return cfg

config = load_config()
