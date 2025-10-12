# tnm-config

Lightweight, well-typed config loader for Python projects with support for environment-based valuexample_config.
Designed to be DI-friendly, testable, and easy to integrate into real apps (FastAPI, CLI tools, workers, etc.).
---

## Features

* Can be extended to load other file formats (INI, .conf, TOML, ...)
* Resolve environment-backed values:
    * YAML: `!env [VAR, type, default?]`
    * JSON: `{"__env__": ["VAR", "type", default?]}`
    * XML: `<env var="VAR" type="type" default="..." />`
* Supported env casts: `str`, `int`, `float`, `bool`, `url`, `list:str`, `list:url`.
* Resolve project-relative paths:

    * YAML: `!path [value, project_relative]`
    * JSON: `{"__path__": {"value": "...", "project_relative": true}}`
    * XML: `<path value="..." project_relative="true" />`
    *
* Optional typed return: pass `schema_type` to `load(...)` to receive a validated instance (Pydantic `BaseModel` or a
  `dataclass`).
* Loader registry & plugin support:

    * built-in loaders auto-register for `.yaml/.yml`, `.json`, `.xml`,
    * register custom loaders at runtime with `tnm.config.loaders.register_loader(...)`,
    * optional entry-point discovery group: `tnm_config.loaders` (so other packages can register loaders via packaging
      metadata).
* Minimal base deps; optional extras: `yaml`, `xml`, `pydantic`.

---

## Quick install

Base (JSON + `.env` support):

```bash
pip install tnm-config
```

Optional extras:

```bash
# YAML support
pip install "tnm-config[yaml]"

# XML support
pip install "tnm-config[xml]"

# Both + pydantic
pip install "tnm-config[all]"
```

If you intend to use `schema_type` with Pydantic models:

```bash
pip install pydantic
```

---

## Quick API

Importing (the package publishes into the `tnm` namespace):

```py
from pathlib import Path
from tnm.config import ConfigLoader, ConfigError
# or
from tnm.config.loader import ConfigLoader
```

Basic usage:

```py
loader = ConfigLoader(Path("config/example_config.yaml"))

# Basic: returns raw resolved structure (dict/list/scalar)
cfg = loader.load("elasticsearch", project_root_callback=lambda: Path.cwd())

# With schema (pydantic model or dataclass), returns typed instance:
inst = loader.load("elasticsearch", project_root_callback=lambda: Path.cwd(), schema_type=MyPydanticModel)
```

**Type hints**: `load` is annotated with overloads so static type-checkers infer:

* no `schema_type` → return is `dict | list | str | int | ...`
* with `schema_type: Type[T]` → return is statically `T`

---

## File format examples

### YAML (`example_config.yaml`)

```yaml
elasticsearch:
  hosts: !env [ ES_HOSTS, list:url, http://127.0.0.1:9200 ]
  username: !env [ ES_USERNAME, str, demo_user ]
  password: !env [ ES_PASSWORD, str, demo_pass ]
  templates_dir: !path [ extras/templates, true ]
```

### JSON (`example_config.json`)

```json
{
  "elasticsearch": {
    "hosts": {
      "__env__": [
        "ES_HOSTS",
        "list:url",
        "http://127.0.0.1:9200"
      ]
    },
    "username": {
      "__env__": [
        "ES_USERNAME",
        "str",
        "demo_user"
      ]
    },
    "password": {
      "__env__": [
        "ES_PASSWORD",
        "str",
        "demo_pass"
      ]
    },
    "templates_dir": {
      "__path__": {
        "value": "extras/templates",
        "project_relative": true
      }
    }
  }
}
```

### XML (`example_config.xml`)

```xml
<?xml version="1.0" encoding="utf-8"?>
<elasticsearch>
    <hosts>
        <env var="ES_HOSTS" type="list:url" default="http://127.0.0.1:9200"/>
    </hosts>
    <username>
        <env var="ES_USERNAME" type="str" default="demo_user"/>
    </username>
    <password>
        <env var="ES_PASSWORD" type="str" default="demo_pass"/>
    </password>
    <templates_dir>
        <path value="extras/templates" project_relative="true"/>
    </templates_dir>
</elasticsearch>
```

All three examples are semantically equivalent for the loader.

---

## `project_root_callback` (recommended)

The loader expects a **zero-argument callable** that returns a `Path` or `str`. This callable is called whenever the
config contains a `project_relative` path that needs resolution.

```py
from pathlib import Path


def my_project_root() -> Path:
    # compute lazily, read an env var, or return a known path
    return Path("/home/my-client-app")


cfg = loader.load("elasticsearch", project_root_callback=my_project_root)
```

---

## Loader registry & plugins

`tnm-config` includes a small loader registry to make adding new formats easy:

* Get a loader for a suffix:

```py
from tnm.config.loaders import get_loader_for_suffix

loader = get_loader_for_suffix(".ini")
if loader is not None:
    data = loader.load(Path("config.ini"), project_root_callback=lambda: Path.cwd())
```

* Register a loader at runtime:

```py
from tnm.config.loaders import register_loader

register_loader(".ini", lambda: MyIniLoader())
```

* Entry-point discovery (optional): packages may register loaders via the `tnm_config.loaders` entry-point group.
  Example in `pyproject.toml` of a plugin:

```toml
[project.entry-points."tnm_config.loaders"]
".ini" = "mypkg.loaders:IniLoader"
```

This lets other distributions add loaders without editing `tnm-config` itself.

---

## Using typed schemas

### Pydantic model

```py
from pydantic import BaseModel
from tnm.config import ConfigLoader


class ElasticCfg(BaseModel):
    hosts: list[str]
    username: str | None = None
    password: str | None = None
    templates_dir: str | None = None


loader = ConfigLoader(Path("config/example_config.yaml"))
cfg_obj = loader.load("elasticsearch", project_root_callback=lambda: Path.cwd(), schema_type=ElasticCfg)
# cfg_obj is a Pydantic model instance (validated)
```

If validation fails, `tnm.config.errors.ConfigError` is raised (with the underlying validation error set as`__cause__`).

### Dataclass

```py
from dataclasses import dataclass
from tnm.config import ConfigLoader


@dataclass
class DCfg:
    name: str
    port: int


loader = ConfigLoader(Path("config.json"))
obj = loader.load("service", project_root_callback=lambda: Path.cwd(), schema_type=DCfg)
```

Dataclass instantiation is direct (if you want richer dataclass conversion, consider adding `dacite` as an optional
extra).

---

## Errors & exceptions

All package-specific exceptions are subclasses of `tnm.config.errors.ConfigError`:

* `EnvVarNotSetError` — an env var referenced by `!env` / `__env__` / `<env/>` is not set and no default was provided.
* `InvalidURLError` — an env var marked `url` is invalid.
* `ConfigError` — generic parse/resolve/validation errors, including schema instantiation failures.

Handle them like:

```py
from tnm.config import ConfigLoader, ConfigError

try:
    cfg = ConfigLoader(Path("example_config.yaml")).load("elasticsearch", project_root_callback=lambda: Path.cwd())
except ConfigError as exc:
    # exc.__cause__ holds the original error (if any)
    print("Config failed:", exc)
```

---

## Security & safety

* **Do not** process untrusted YAML content.
* Avoid printing or logging secrets from config valuexample_config. `ConfigError` preserves underlying exceptions as
  `__cause__` —
  inspect with care.

---

## Contributing & roadmap

Possible next steps / features you might request:

* Add `dacite` support to robustly instantiate nested dataclasses (optional extra).
* Provide a CLI tool `tnm-config-validate` to validate a config file against a schema.
* Add caching of parsed config filexample_config.

## License

MIT
