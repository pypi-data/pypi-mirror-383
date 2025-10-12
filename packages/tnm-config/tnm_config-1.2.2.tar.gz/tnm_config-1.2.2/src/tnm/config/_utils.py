import re
from pathlib import Path
from typing import Any, Callable
from urllib.parse import urlparse

from . import get_config
from ._typeguard import typechecked
from .errors import EnvVarNotSetError, InvalidURLError, ConfigError

_TOKEN_RE = re.compile(r"(%\s*(?P<t1>[A-Za-z_]+)\s*%|\{\{\s*(?P<t2>[A-Za-z_]+)\s*\}\})")


def _apply_preserved_tokens(
    s: str, project_root_callback: Callable[[], Path | str] | None
) -> str:
    """
    Replace preserved tokens in a string with actual paths.
    :raises: ConfigError
    """

    def _replace(m: re.Match) -> str:
        token = (m.group("t1") or m.group("t2") or "").strip().lower()
        if token in ("project_root", "project_dir", "project"):
            if project_root_callback is None:
                raise ConfigError(
                    f"Token '{token}' requires project_root_callback to be provided."
                )
            root = project_root_callback()
            if not isinstance(root, Path):
                root = Path(root)
            return str(root)
        if token in ("home", "user_home"):
            return str(Path.home())
        if token in ("user", "username"):
            # return home (most useful). If you want username text only, expand here.
            return str(Path.home())
        raise ConfigError(f"Unknown preserved token: '{token}'")

    return _TOKEN_RE.sub(_replace, s)


def _cast_env_value(var_name: str, type_hint: str, default: Any) -> Any:
    """
    Cast environment variable using type_hint.
    Supported hints: url, str, int, float, bool, list:str, list:url
    :raises EnvVarNotSetError: if missing and default is None.
    :raises InvalidURLError: on invalid input.
    :raises ValueError: on invalid input.
    """
    val: str | None = get_config(key=var_name, default=None)
    if val is None:
        if default is not None:
            return _match_type_hint(type_hint, default)
        raise EnvVarNotSetError(f"Environment variable '{var_name}' not set")

    return _match_type_hint(type_hint=type_hint, val=val)


def _match_type_hint(type_hint: str, val: Any):
    match type_hint:
        case "url":
            parsed = urlparse(val)
            if not parsed.scheme or not parsed.netloc:
                raise InvalidURLError(f"Provided URL '{val}' is invalid.")
            return val
        case "str":
            return val
        case "int":
            return int(val)
        case "float":
            return float(val)
        case "bool":
            v = val.lower()
            if v in ("1", "true", "yes", "y", "on"):
                return True
            if v in ("0", "false", "no", "n", "off"):
                return False
            raise ValueError(f"Cannot cast '{val}' to bool")
        case hint if hint.startswith("list:str"):
            return [item.strip() for item in val.split(",") if item.strip()]
        case hint if hint.startswith("list:url"):
            valid = []
            for item in val.split(","):
                parsed = urlparse(item.strip())
                if not parsed.scheme or not parsed.netloc:
                    raise InvalidURLError(
                        f"The provided URL {item!r} in list {val!r} is invalid."
                    )
                valid.append(item.strip())
            return valid
        case _:
            raise ValueError(f"Unsupported env type hint: {type_hint!r}")


@typechecked
def _get_project_root_from_callable(
    project_root_callback: Callable[[], Path | str] | None,
) -> Path:
    """Return a resolved Path from the provided callable."""
    if not project_root_callback:
        raise ConfigError(
            "'project_root_callback' is required for !path with project_relative=True"
        )

    try:
        p = project_root_callback()
    except Exception as exc:
        raise ConfigError(
            f"'project_root_callback' raised an exception: {str(exc)}"
        ) from exc
    if not isinstance(p, Path):
        p = Path(p)

    p = p.resolve()

    if not p.is_dir():
        raise ConfigError(f"'project_root_callback' is not a directory: {p}")

    return p


def _resolve_project_path(
    value: Any,
    project_root_callback: Callable[[], Path | str] | None = None,
    project_relative: bool | str = True,
) -> Any:
    """
    Resolve project-relative paths.

    value:
      - str: a path string — supports tokens like %project_root% or {{ home }}
      - list: resolved recursively
      - dict: supports mapping form:
          {"value": "data/...", "relative_to": "project_root"|"home"|"user"}
          If dict only has "path" / "project_relative" keys (backwards compat),
          they'll be honored too.

    project_relative:
      - True (default): relative strings without tokens are resolved relative to project_root
      - False: do not prefix project root; tokens are still expanded
      - or one of "project_root"|"home"|"user" to force a specific base

    Returns:
      str for paths (absolute, resolved), or the original value for non-paths,
      or lists/dicts with resolved paths.
    """

    if isinstance(value, list):
        return [
            _resolve_project_path(
                item,
                project_root_callback=project_root_callback,
                project_relative=project_relative,
            )
            for item in value
        ]

    # dict mapping form: {"value": "...", "relative_to": "..."}
    if isinstance(value, dict):
        # Backwards compatibility: accept {"path": ..., "project_relative": ...}
        if "value" in value and "relative_to" in value:
            v = value["value"]
            base = value["relative_to"]
            base_l = str(base).lower() if base is not None else None
            if base_l in ("project_root", "project_dir", "project"):
                root = _get_project_root_from_callable(project_root_callback)
                return str((root / str(v)).resolve())
            if base_l in ("home", "user", "username", "user_home"):
                return str((Path.home() / str(v)).resolve())
            raise ConfigError(
                f"Unsupported relative_to value: {base!r}. Supported: project_root, home, user"
            )

        # Older form: {"path": <...>, "project_relative": True/False}
        if "path" in value and "project_relative" in value:
            return _resolve_project_path(
                value["path"],
                project_root_callback=project_root_callback,
                project_relative=bool(value.get("project_relative", True)),
            )

        return {
            k: _resolve_project_path(
                v,
                project_root_callback=project_root_callback,
                project_relative=project_relative,
            )
            for k, v in value.items()
        }

    if isinstance(value, str):

        if _TOKEN_RE.search(value):
            replaced = _apply_preserved_tokens(value, project_root_callback)
            p = Path(replaced)
            if p.is_absolute():
                return str(p.resolve())
            if isinstance(project_relative, str):
                base_l = project_relative.lower()
                if base_l in ("project_root", "project_dir", "project"):
                    root = _get_project_root_from_callable(project_root_callback)
                    return str((root / replaced).resolve())
                if base_l in ("home", "user", "username"):
                    return str((Path.home() / replaced).resolve())
            if project_relative is False:
                return str(Path(replaced).resolve())
            root = _get_project_root_from_callable(project_root_callback)
            return str((root / replaced).resolve())

        p = Path(value)
        if p.is_absolute():
            return str(p.resolve())
        if isinstance(project_relative, str):
            base_l = project_relative.lower()
            if base_l in ("project_root", "project_dir", "project"):
                root = _get_project_root_from_callable(project_root_callback)
                return str((root / value).resolve())
            if base_l in ("home", "user", "username"):
                return str((Path.home() / value).resolve())
        if project_relative is False:
            return str(p.resolve())

        root = _get_project_root_from_callable(project_root_callback)
        return str((root / value).resolve())

    return value


def _resolve_node(
    node: Any, project_root_callback: Callable[[], Path | str] | None = None
) -> Any:
    """
    Recursively resolve special markers:
      - YAML: handled by constructors (if PyYAML used)
      - For JSON: special marker objects:
          {"__env__": ["VAR", "type", default?]}
          {"__path__": {"value": "...", "project_relative": true/false}}
      - For XML (xmltodict): tags:
          <env var="VAR" type="list:url" default="..."/>
          <path value="..." project_relative="true"/>
    """
    if isinstance(node, list):
        return [
            _resolve_node(item, project_root_callback=project_root_callback)
            for item in node
        ]

    if not isinstance(node, dict):
        return node

    return {
        k: _resolve_node(v, project_root_callback=project_root_callback)
        for k, v in node.items()
    }
