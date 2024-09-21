from __future__ import annotations

from pathlib import Path

from dynaconf import Dynaconf

# NOTE: initialize dynaconf custom casting tokens
# https://www.dynaconf.com/envvars/#adding-a-custom-casting-token
from .dynaconf_casts import *  # noqa
from .dynaconf_validators import validators

BASE_DIR = Path(__file__).parent.parent.parent.resolve(strict=True).as_posix()


# NOTE: https://github.com/dynaconf/dynaconf/issues/867
settings = Dynaconf(
    auto_cast=True,
    core_loaders=["TOML", "PY"],
    root_path=BASE_DIR,
    settings_files=[
        "settings.toml",
        "src.setting",  # to auto-load the `src.setting.dynaconf_hooks` module
    ],
    secrets=".secrets.toml",
    # system environment variable configuration
    load_dotenv=False,
    envvar_prefix=False,
    ignore_unknown_envvars=True,
    # app environment configuration
    environments=True,
    env_switcher="ENVIRONMENT",
    default_env="default",
    env="development",
    # validations configuration
    validators=validators,
    validate_only_current_env=True,
)
