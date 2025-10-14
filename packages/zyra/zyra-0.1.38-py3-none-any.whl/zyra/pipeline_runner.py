# SPDX-License-Identifier: Apache-2.0
from __future__ import annotations

import argparse
import io
import json
import logging
import os
from pathlib import Path
from typing import Any

from zyra.utils.env import env, env_bool


def _load_yaml_or_json_generic(path: str) -> dict[str, Any]:
    """Load YAML/JSON for lightweight schema probing (workflow vs pipeline)."""
    try:
        text = Path(path).read_text(encoding="utf-8")
    except FileNotFoundError as exc:
        raise SystemExit(
            f"Config file not found: {path}. Use an absolute path or run from the project root."
        ) from exc
    try:
        import yaml  # type: ignore

        return yaml.safe_load(text)  # type: ignore[no-any-return]
    except ModuleNotFoundError:
        return json.loads(text)
    except Exception:
        return json.loads(text)


def _load_config(path: str) -> dict[str, Any]:
    """Load a pipeline config from YAML or JSON file.

    Prefer YAML when available; provide a helpful error if a YAML file is used
    but PyYAML is not installed.
    """
    try:
        text = Path(path).read_text(encoding="utf-8")
    except FileNotFoundError as exc:
        raise SystemExit(
            f"Config file not found: {path}. Use an absolute path or run from the project root."
        ) from exc
    # Try YAML first
    try:
        import yaml  # type: ignore
    except ModuleNotFoundError:
        # If the file looks like YAML, raise a friendly message
        if path.lower().endswith((".yml", ".yaml")):
            raise SystemExit(
                "PyYAML is not installed. Install it or use a JSON config (e.g., samples/pipelines/*.json)."
            ) from None
    else:
        try:
            return yaml.safe_load(text)  # type: ignore[no-any-return]
        except yaml.YAMLError as e:  # Be explicit about YAML parse failures
            logging.debug(
                "YAML parse failed for %s: %s. Falling back to JSON.", path, e
            )
    # Fall back to JSON
    return json.loads(text)


def _expand_env(obj: Any, *, strict: bool = False) -> Any:
    """Recursively expand environment placeholders within nested structures.

    - Expands ``$VAR`` and ``${VAR}`` using the current environment.
    - Supports shell-style defaults via ``${VAR:-default}``.
    - When ``strict`` is True, raises ``SystemExit`` if a plain ``${VAR}``
      appears without a corresponding environment value. Defaults specified via
      ``${VAR:-default}`` are not considered errors in strict mode.
    """
    import os
    import re

    if isinstance(obj, dict):
        return {k: _expand_env(v, strict=strict) for k, v in obj.items()}
    if isinstance(obj, list):
        return [_expand_env(x, strict=strict) for x in obj]
    if isinstance(obj, str):
        # Strict: fail on ${VAR} with no default when missing
        if strict:
            for m in re.finditer(r"\$\{([A-Za-z_][A-Za-z0-9_]*)\}", obj):
                # Ignore defaulted form ${VAR:-default}
                # We check only plain ${VAR}
                var = m.group(1)
                if (
                    f"${{{var}:-" in obj
                ):  # a default exists elsewhere; skip this occurrence
                    continue
                if var not in os.environ:
                    raise SystemExit(f"Environment variable not set: {var}")
        # First expand standard $VAR and ${VAR}
        s = os.path.expandvars(obj)

        # Then handle shell-style defaults ${VAR:-default}
        def _sub_default(mm: re.Match[str]) -> str:
            var, default = mm.group(1), mm.group(2)
            val = os.environ.get(var)
            return val if val not in (None, "") else default

        s = re.sub(r"\$\{([A-Za-z_][A-Za-z0-9_]*)\:-([^}]*)\}", _sub_default, s)
        return s
    return obj


def _apply_overrides(
    cfg: dict[str, Any], overrides: list[tuple[str, str]] | None
) -> None:
    """Apply --set overrides to a config in-place.

    Supports forms:
    - ``N.key=value`` (1-based stage index)
    - ``stageName.key=value`` (stage alias name)
    - ``key=value`` (global; applied where key exists)
    """
    if not overrides:
        return
    # Simple rule: apply key=value into every stage's args where key matches
    stages = cfg.get("stages") or []
    import re

    for raw_k, v in overrides:
        # 1) 1-based index override: N.key=value
        m = re.match(r"^(\d+)\.(.+)$", raw_k)
        if m:
            idx = int(m.group(1)) - 1
            key = m.group(2)
            if 0 <= idx < len(stages):
                args = stages[idx].get("args") or {}
                args[key] = v
                stages[idx]["args"] = args
            continue

        # 2) Stage-name override: stage.key=value (supports aliases)
        m2 = re.match(r"^([A-Za-z_\-]+)\.(.+)$", raw_k)
        if m2:
            stage_name = m2.group(1).lower()
            key = m2.group(2)
            # Normalize requested stage name
            desired = _stage_group_alias(stage_name)
            for st in stages:
                current = _stage_group_alias(str(st.get("stage", "")))
                if current == desired:
                    args = st.get("args") or {}
                    args[key] = v
                    st["args"] = args
            continue

        # 3) Global override: apply where key exists
        for st in stages:
            args = st.get("args") or {}
            if raw_k in args:
                args[raw_k] = v
                st["args"] = args


def _stage_group_alias(name: str) -> str:
    """Normalize a stage name/alias to one of: acquire/process/visualize/decimate.

    Preferred user-facing terms are ``export``/``disseminate`` for egress and
    ``process`` (rather than ``transform``). For backward compatibility, we
    currently normalize ``export``/``disseminate``/``decimation`` to the
    internal canonical ``decimate``. Aliases include:

    - import/ingest → acquire
    - render → visualize
    - disseminate/export/decimation → decimate (canonical for now)
    - transform → process (combined under process)
    - optimize → decide

    TODO: Consider flipping the internal canonical to ``disseminate`` once
    downstream code/tests and ecosystem usage have fully migrated.
    """
    name = name.lower().strip()
    return {
        "acquisition": "acquire",
        "ingest": "acquire",
        "import": "acquire",
        "processing": "process",
        "visualization": "visualize",
        "render": "visualize",
        "decimation": "decimate",
        "disseminate": "decimate",
        "export": "decimate",
        "transform": "process",
        "optimize": "decide",
    }.get(name, name)


def _build_argv_for_stage(stage: dict[str, Any]) -> list[str]:
    """Translate a stage mapping into a zyra argv vector."""
    group = _stage_group_alias(stage.get("stage", ""))
    cmd = stage.get("command")
    if not group or not cmd:
        raise SystemExit("Each stage requires 'stage' and 'command'")
    args = stage.get("args") or {}
    # Back-compat mapping: allow 'file_pattern' in configs to map to '--pattern'
    if "file_pattern" in args and "pattern" not in args:
        args["pattern"] = args.pop("file_pattern")
    # Compute since from ISO period if provided and --since not set
    if "since" not in args and "since_period" in args and args["since_period"]:
        try:
            from zyra.utils.date_manager import DateManager

            start, _ = DateManager().get_date_range_iso(str(args["since_period"]))
            args["since"] = start.isoformat()
        except Exception:
            pass
    # Compute since from non-ISO period (e.g., 1Y, 6M, 7D, 24H) if provided
    if "since" not in args and "period" in args and args["period"]:
        try:
            from zyra.utils.date_manager import DateManager

            start, _ = DateManager().get_date_range(str(args["period"]))
            args["since"] = start.isoformat()
        except Exception:
            pass

    # Special-case: acquisition 'acquire' with backend -> translate to subcommand
    args = stage.get("args") or {}
    if group == "acquire" and (cmd in (None, "acquire")) and "backend" in args:
        cmd = str(args.pop("backend")).lower()

    # Special-case: decimate 'decimate' with backend -> translate to subcommand
    if group == "decimate" and (cmd in (None, "decimate")) and "backend" in args:
        cmd = str(args.pop("backend")).lower()

    argv: list[str] = [group, str(cmd)]

    # Known positionals for selected commands
    positionals: list[str] = []
    if group == "process" and cmd == "convert-format":
        positionals = ["file_or_url", "format"]
    elif group == "process" and cmd == "decode-grib2":
        positionals = ["file_or_url"]
    elif group == "process" and cmd == "extract-variable":
        positionals = ["file_or_url", "pattern"]
    elif group == "acquire" and cmd == "http":
        positionals = ["url"]
    elif (group == "acquire" and cmd == "ftp") or (
        group == "decimate" and cmd in {"local", "ftp"}
    ):
        positionals = ["path"]
    elif group == "decimate" and cmd == "post":
        positionals = ["url"]
    # For other commands, default to flags-only mapping

    # Add positionals in order if present
    for key in positionals:
        if key in args:
            argv.append(str(args.pop(key)))
        else:
            # Leave it to the CLI to error on missing required positionals
            pass

    # Add remaining as flags: --kebab-case
    def to_flag(k: str) -> str:
        return "--" + k.replace("_", "-")

    for k, v in list(args.items()):
        if isinstance(v, bool):
            if v:
                argv.append(to_flag(k))
        elif v is None:
            continue
        else:
            argv.extend([to_flag(k), str(v)])

    return argv


def _run_cli(argv: list[str], input_bytes: bytes | None) -> tuple[int, bytes, str]:
    """Execute a CLI stage in-process, passing stdin bytes and capturing stdout."""
    import sys

    from zyra.cli import main as cli_main

    # Lightweight fast-paths to avoid importing heavy dependencies when possible
    try:
        if (
            len(argv) >= 4
            and argv[0] == "process"
            and argv[1] == "convert-format"
            and "--stdout" in argv
            and argv[3].lower() == "netcdf"
            and argv[2] == "-"
            and input_bytes
            and (input_bytes.startswith(b"CDF") or input_bytes.startswith(b"\x89HDF"))
        ):
            return 0, input_bytes, ""
        # Fast-path: decimate local with '-' input; write bytes directly
        if (
            len(argv) >= 3
            and argv[0] == "decimate"
            and argv[1] == "local"
            and input_bytes is not None
        ):
            # Positional path is argv[2]; also allow flags order-insensitive
            dest_path = argv[2]
            # If --input provided and not '-', we cannot fast-path
            if "--input" in argv:
                try:
                    i = argv.index("--input")
                    if i + 1 < len(argv) and argv[i + 1] not in ("-", "--"):
                        raise ValueError
                except ValueError:
                    # Fallback to normal CLI path
                    pass
                else:
                    try:
                        from pathlib import Path

                        p = Path(dest_path)
                        if p.parent:
                            p.parent.mkdir(parents=True, exist_ok=True)
                        with p.open("wb") as f:
                            f.write(input_bytes)
                        return 0, b"", ""
                    except OSError as exc:
                        return 2, b"", str(exc)
            else:
                # No explicit --input; assume stdin
                try:
                    from pathlib import Path

                    p = Path(dest_path)
                    if p.parent:
                        p.parent.mkdir(parents=True, exist_ok=True)
                    with p.open("wb") as f:
                        f.write(input_bytes)
                    return 0, b"", ""
                except OSError as exc:
                    return 2, b"", str(exc)
    except (ValueError, IndexError, OSError, AttributeError, TypeError):
        # Fall back to normal path on any detection error
        pass

    # Preserve and swap stdin/stdout
    old_stdin = sys.stdin
    old_stdout = sys.stdout
    buf_in = io.BytesIO(input_bytes or b"")
    buf_out = io.BytesIO()
    sys.stdin = type("S", (), {"buffer": buf_in})()  # type: ignore
    sys.stdout = type(
        "S",
        (),
        {
            "buffer": buf_out,
            "write": lambda self, s: None,
            "flush": lambda self: None,
        },
    )()  # type: ignore
    try:
        rc = cli_main(argv)
        try:
            out = buf_out.getvalue()
        except Exception:
            # Some commands may close sys.stdout.buffer; treat as empty output
            logging.getLogger(__name__).warning(
                "stdout buffer was closed by command; no bytes captured"
            )
            out = b""
        return int(rc), out, ""
    except SystemExit as exc:
        return int(getattr(exc, "code", 2) or 2), b"", str(exc)
    except Exception as exc:  # pragma: no cover - unexpected
        return 2, b"", str(exc)
    finally:
        sys.stdin = old_stdin
        sys.stdout = old_stdout


def run_pipeline(
    config_path: str,
    overrides: list[tuple[str, str]] | None = None,
    *,
    print_argv: bool = False,
    dry_run: bool = False,
    continue_on_error: bool = False,
    print_format: str = "text",
    start: int | None = None,
    end: int | None = None,
    only: str | None = None,
    trace: bool = False,
) -> int:
    """Execute a pipeline from YAML/JSON with optional filtering and dry-run.

    - Applies env interpolation and ``--set`` overrides
    - Supports ``--start/--end`` (1-based) and ``--only`` stage alias
    - When ``print_argv`` or ``dry_run`` is True, prints stage argv vectors
      in text or JSON format instead of executing
    """
    cfg = _load_config(config_path)
    _apply_overrides(cfg, overrides)
    # Env var interpolation (apply before extracting stages)
    strict_env = env_bool("STRICT_ENV", False)
    cfg = _expand_env(cfg, strict=strict_env)
    stages = cfg.get("stages") or []
    if not isinstance(stages, list) or not stages:
        raise SystemExit("Pipeline config missing 'stages' list")

    # Lightweight validation
    for i, st in enumerate(stages, start=1):
        if not isinstance(st, dict):
            raise SystemExit(f"Stage {i} is not a mapping")
        if "stage" not in st or "command" not in st:
            raise SystemExit(f"Stage {i} missing 'stage' or 'command'")
        if "args" in st and not isinstance(st["args"], dict):
            raise SystemExit(f"Stage {i} 'args' must be a mapping when provided")

    # Stage filtering: start/end (1-based) and only stage alias
    total = len(stages)
    s_idx = max(1, int(start)) if start else 1
    e_idx = min(total, int(end)) if end else total
    if s_idx > e_idx:
        raise SystemExit("--start must be <= --end")

    # Prepare filtered list
    selected: list[dict[str, Any]] = []
    desired_name = _stage_group_alias(only) if only else None
    for idx, st in enumerate(stages, start=1):
        if not (s_idx <= idx <= e_idx):
            continue
        if (
            desired_name
            and _stage_group_alias(str(st.get("stage", ""))) != desired_name
        ):
            continue
        selected.append(st)

    # Stream bytes between stages.
    # Seed first stage with stdin bytes when available (non-tty), enabling '-' driven pipelines.
    import sys

    try:
        current_stdin = None if sys.stdin.isatty() else sys.stdin.buffer.read()
    except Exception:
        current_stdin = None
    current: bytes | None = current_stdin if current_stdin else None

    # Optional seeding from env for CI or non-piped contexts.
    # If the first selected stage expects '-' as an input and stdin is empty,
    # use ZYRA_DEFAULT_STDIN (or legacy DATAVIZHUB_DEFAULT_STDIN) to provide bytes.
    if current is None:
        try:
            default_stdin_path = env("DEFAULT_STDIN")
            if default_stdin_path and selected:
                first = selected[0]
                if isinstance(first, dict):
                    args0 = first.get("args") or {}
                    if any(v == "-" for v in args0.values()):
                        from pathlib import Path

                        current = Path(default_stdin_path).read_bytes()
        except Exception:
            # Ignore seeding failures silently; normal error handling will apply later
            pass

    # Printed structures for --print-argv-format=json
    printed_objects: list[dict[str, Any]] = []
    any_error: int | None = None
    # Set verbosity env for stages
    verbosity = env("VERBOSITY", "info")

    for idx, st in enumerate(selected):
        argv = _build_argv_for_stage(st)
        # If tracing, echo the command that will run
        if trace and not (print_argv or dry_run):
            try:
                import logging as _log

                from zyra.utils.cli_helpers import sanitize_for_log

                _log.info("+ cwd='%s'", str(Path.cwd()))
                _log.info("+ %s", sanitize_for_log(" ".join(["zyra", *argv])))
            except Exception:
                pass
        if print_argv or dry_run:
            if print_format == "json":
                printed_objects.append(
                    {
                        "stage": idx + 1,
                        "name": _stage_group_alias(str(st.get("stage", ""))),
                        "id": st.get("id"),
                        "argv": ["zyra", *argv],
                    }
                )
            else:
                line = " ".join(["zyra", *argv])
                if verbosity == "debug":
                    sys.stdout.write(
                        f"Stage {idx+1} [{_stage_group_alias(str(st.get('stage','')))}]:\n"
                    )
                sys.stdout.write(line + "\n")
        if dry_run:
            continue
        # Propagate shell tracing to in-process stages when requested
        if trace:
            os.environ["ZYRA_SHELL_TRACE"] = "1"
        rc, out, _ = _run_cli(argv, current)
        # If the very first stage failed and it appears to require stdin ('-') but none was provided,
        # emit a helpful hint to stderr for CI logs.
        if rc != 0 and idx == 0 and current is None:
            try:
                if (
                    len(argv) >= 4
                    and argv[0] == "process"
                    and argv[1] == "convert-format"
                    and argv[2] == "-"
                    and "--stdout" in argv
                ):
                    msg = (
                        "No stdin provided for first stage requiring '-' input (process convert-format --stdout).\n"
                        "Hint: pipe input bytes or set ZYRA_DEFAULT_STDIN=/path/to/file (legacy DATAVIZHUB_DEFAULT_STDIN).\n"
                    )
                    sys.stderr.write(msg)
                    from contextlib import suppress

                    with suppress(Exception):
                        logging.getLogger(__name__).error(msg.strip())
            except Exception:
                pass
        if rc != 0:
            any_error = any_error or rc
            try:
                # Print a helpful failure summary with the exact argv that failed
                stage_name = _stage_group_alias(str(st.get("stage", "")))
                cmdline = " ".join(["zyra", *argv])
                msg = (
                    f"Stage {idx+1} [{stage_name}] failed with exit code {rc}.\n"
                    f"Command: {cmdline}\n"
                    "Hint: re-run with --dry-run or --print-argv for mapping details, "
                    "or set ZYRA_VERBOSITY=debug (legacy DATAVIZHUB_VERBOSITY) for stage headings.\n"
                )
                sys.stderr.write(msg)
                from contextlib import suppress

                with suppress(Exception):
                    logging.getLogger(__name__).error(msg.strip())
            except Exception:
                pass
            if not continue_on_error:
                return rc
            # On error, clear current bytes to avoid accidental pass-through
            current = None
            continue
        # Next stage receives out on stdin
        current = out

    # Emit printed argv in JSON format if requested
    if (print_argv or dry_run) and print_format == "json":
        sys.stdout.write(json.dumps(printed_objects) + "\n")

    # Write final bytes to stdout only when actually executing stages (not dry-run)
    if current is not None and not dry_run:
        try:
            sys.stdout.buffer.write(current)
        except Exception:
            # Fallback to text write if buffer not available
            sys.stdout.write(current.decode("utf-8", errors="ignore"))
    return any_error or 0


def register_cli_run(subparsers: Any) -> None:
    """Register the ``run`` subcommand on a parser."""
    p = subparsers.add_parser("run", help="Run a pipeline from YAML/JSON config")
    p.add_argument("config")
    p.add_argument(
        "--set",
        action="append",
        default=[],
        dest="overrides",
        help="Override key=value in args across stages",
    )
    p.add_argument(
        "--print-argv", action="store_true", help="Print argv per stage before running"
    )
    p.add_argument("--print-argv-format", choices=["text", "json"], default="text")
    p.add_argument(
        "--dry-run", action="store_true", help="Only print argv; do not execute stages"
    )
    p.add_argument(
        "--trace",
        action="store_true",
        help="Shell-style trace: print '+ <command>' and working directory per stage",
    )
    p.add_argument(
        "--continue-on-error",
        action="store_true",
        help="Continue executing remaining stages even if one fails",
    )
    p.add_argument("--start", type=int, help="1-based index of first stage to run")
    p.add_argument("--end", type=int, help="1-based index of last stage to run")
    p.add_argument(
        "--only",
        help=(
            "Run only stages matching this alias "
            "(import/acquire/process/transform/visualize/render/simulate/decide/optimize/"
            "narrate/verify/export/disseminate/decimate)"
        ),
    )
    # Env & verbosity controls
    vgrp = p.add_mutually_exclusive_group()
    vgrp.add_argument(
        "-v",
        "--verbose",
        action="store_true",
        help="Verbose runner output (prints stage headings)",
    )
    vgrp.add_argument(
        "--quiet", action="store_true", help="Suppress runner messages when possible"
    )
    p.add_argument(
        "--strict-env",
        action="store_true",
        help="Fail if ${VAR} placeholders are not set in environment",
    )
    p.add_argument(
        "--max-workers",
        type=int,
        help="When config is a workflow.yml, run up to N jobs in parallel",
    )
    # Workflow compatibility options (when config is a workflow.yml)
    p.add_argument(
        "--watch",
        action="store_true",
        help="When config is a workflow.yml, evaluate triggers and run if active",
    )
    p.add_argument(
        "--export-cron",
        action="store_true",
        help="When config is a workflow.yml, print crontab lines for schedule triggers",
    )
    p.add_argument("--state-file", help="State file for --watch (workflow.yml)")
    p.add_argument(
        "--run-on-first",
        action="store_true",
        help="Trigger a run when no prior state exists (workflow.yml watch)",
    )
    p.add_argument(
        "--watch-interval",
        type=float,
        help="When --watch is set, poll every N seconds (default: single poll)",
    )
    p.add_argument(
        "--watch-count",
        type=int,
        help="When --watch is set with --watch-interval, stop after N iterations",
    )
    # Logging destination: either a file or a directory (defaults to workflow.log)
    lg = p.add_mutually_exclusive_group()
    lg.add_argument(
        "--log-file",
        dest="log_file",
        help="Write runner and stage logs to the given file",
    )
    lg.add_argument(
        "--log-dir",
        dest="log_dir",
        help="Write logs under this directory as workflow.log",
    )
    p.add_argument(
        "--log-file-mode",
        choices=["append", "overwrite"],
        default="append",
        help="Log file write mode (default: append)",
    )

    def _cmd(ns: argparse.Namespace) -> int:
        # Best-effort: load environment variables from a local .env if present
        try:
            import logging as _logging

            from dotenv import find_dotenv, load_dotenv  # type: ignore

            _ENV_PATH = find_dotenv(usecwd=True)
            if _ENV_PATH:
                load_dotenv(_ENV_PATH, override=False)
                _logging.getLogger(__name__).debug(
                    "Loaded environment from .env at %s", _ENV_PATH
                )
            else:
                _logging.getLogger(__name__).debug(
                    "No .env file found; skipping dotenv load."
                )
        except Exception:
            # Ignore if python-dotenv is unavailable; environment vars still work
            pass

        pairs: list[tuple[str, str]] = []
        for item in ns.overrides:
            if "=" not in item:
                raise SystemExit("--set requires key=value")
            k, v = item.split("=", 1)
            pairs.append((k, v))
        # Set verbosity/strict env via process env (visible to in-process stages)
        if ns.verbose:
            # Prefer new ZYRA_* envs first; set legacy for back-compat next
            os.environ["ZYRA_VERBOSITY"] = "debug"
            os.environ["DATAVIZHUB_VERBOSITY"] = "debug"
        elif ns.quiet:
            os.environ["ZYRA_VERBOSITY"] = "quiet"
            os.environ["DATAVIZHUB_VERBOSITY"] = "quiet"
        else:
            os.environ.setdefault("ZYRA_VERBOSITY", "info")
            os.environ.setdefault("DATAVIZHUB_VERBOSITY", "info")
        if ns.strict_env:
            os.environ["ZYRA_STRICT_ENV"] = "1"
            os.environ["DATAVIZHUB_STRICT_ENV"] = "1"

        # Optional file logging for the runner and in-process stages
        # Resolve log file from --log-file or --log-dir
        log_target = None
        if getattr(ns, "log_file", None):
            log_target = ns.log_file
        elif getattr(ns, "log_dir", None):
            from pathlib import Path

            log_target = str(Path(ns.log_dir) / "workflow.log")

        if log_target:
            try:
                from pathlib import Path

                mode = "a" if ns.log_file_mode != "overwrite" else "w"
                pth = Path(log_target)
                if pth.parent:
                    pth.parent.mkdir(parents=True, exist_ok=True)
                fh = logging.FileHandler(pth, mode=mode, encoding="utf-8")
                fh.setFormatter(logging.Formatter("%(levelname)s: %(message)s"))
                root = logging.getLogger()
                # Avoid adding duplicate file handlers for the same path
                # Avoid duplicate file handlers: compare resolved paths
                try:
                    target = pth.resolve()
                except Exception:
                    target = pth
                exists = False
                for h in root.handlers:
                    bf = getattr(h, "baseFilename", None)
                    if not bf:
                        continue
                    try:
                        from pathlib import Path as _P

                        if _P(bf).resolve() == target:
                            exists = True
                            break
                    except Exception:
                        # Fall back to string compare if resolve fails
                        if str(bf) == str(target):
                            exists = True
                            break
                if not exists:
                    root.addHandler(fh)
                # Set root level based on env verbosity
                lvl_map = {
                    "debug": logging.DEBUG,
                    "info": logging.INFO,
                    "quiet": logging.ERROR,
                }
                verb = os.environ.get("ZYRA_VERBOSITY", "info").lower()
                root.setLevel(lvl_map.get(verb, logging.INFO))
            except Exception:
                # Non-fatal if log file cannot be configured
                pass

        # Detect if this is a workflow.yml (has 'jobs' or 'on' sections)
        try:
            doc = _load_yaml_or_json_generic(ns.config)
        except Exception:
            doc = {}
        is_workflow = isinstance(doc, dict) and ("jobs" in doc or "on" in doc)
        if not is_workflow:
            # Heuristic detection when YAML is unavailable: scan raw text for keys
            try:
                txt = Path(ns.config).read_text(encoding="utf-8")
                if any(
                    token in txt
                    for token in ("\njobs:", "\non:", "\r\njobs:", "\r\non:")
                ):
                    is_workflow = True
            except Exception:
                pass
        if is_workflow:
            # Route to workflow runner
            # Imported here to avoid unnecessary imports for classic pipelines
            try:  # noqa: WPS501
                from zyra.workflow import cmd_export_cron as wf_export
                from zyra.workflow import cmd_run as wf_run
                from zyra.workflow import cmd_watch as wf_watch
            except Exception as exc:
                raise SystemExit(f"Workflow runner unavailable: {exc}") from exc
            if ns.export_cron:
                wfns = argparse.Namespace(workflow=ns.config)
                return wf_export(wfns)
            if ns.watch:
                wfns = argparse.Namespace(
                    workflow=ns.config,
                    state_file=ns.state_file,
                    run_on_first=ns.run_on_first,
                    watch_interval=ns.watch_interval,
                    watch_count=ns.watch_count,
                    dry_run=ns.dry_run,
                )
                return wf_watch(wfns)
            wfns = argparse.Namespace(
                workflow=ns.config,
                continue_on_error=ns.continue_on_error,
                max_workers=ns.max_workers,
                dry_run=ns.dry_run,
            )
            return wf_run(wfns)
        # Default: classic pipeline runner
        return run_pipeline(
            ns.config,
            pairs,
            print_argv=ns.print_argv or ns.dry_run,
            dry_run=ns.dry_run,
            continue_on_error=ns.continue_on_error,
            print_format=ns.print_argv_format,
            start=ns.start,
            end=ns.end,
            only=ns.only,
            trace=ns.trace,
        )

    p.set_defaults(func=_cmd)
