from __future__ import annotations

import logging
import os
import platform
import shlex
import shutil
import subprocess
import tarfile
import tempfile
import hashlib
import json
import re
import urllib.request
from dataclasses import dataclass
from pathlib import Path

try:
    import fcntl
except ImportError:  # pragma: no cover - Windows
    fcntl = None

logger = logging.getLogger(__name__)

_MIN_NODE_VERSION = (22, 12, 0)
_DEFAULT_NODE_VERSION = "22.22.1"
_DEFAULT_OPENCLAW_VERSION = "2026.3.23-2"
_DEFAULT_NODE_OPTIONS = "--max-old-space-size=768"


def ensure_openclaw_runtime() -> None:
    if not _read_bool_env("OPENCLAW_AUTOSTART", default=True):
        return

    existing_gateway_command = _read_valid_gateway_command()
    if existing_gateway_command:
        os.environ["OPENCLAW_GATEWAY_COMMAND"] = existing_gateway_command
        return

    installed_gateway_command = _build_installed_gateway_command()
    if installed_gateway_command:
        home_dir = _resolve_bootstrap_home_dir()
        os.environ["OPENCLAW_GATEWAY_COMMAND"] = installed_gateway_command
        _ensure_minimal_config_file(home_dir)
        logger.info("Using installed OpenClaw runtime at %s", shlex.split(installed_gateway_command)[0])
        return

    required_node_version = _read_runtime_version("OPENCLAW_NODE_VERSION", _DEFAULT_NODE_VERSION)
    required_openclaw_version = _read_runtime_version("OPENCLAW_VERSION", _DEFAULT_OPENCLAW_VERSION)
    home_dir = _resolve_bootstrap_home_dir()

    try:
        bootstrapped_runtime = _bootstrap_runtime(home_dir, required_node_version, required_openclaw_version)
    except Exception as exc:
        raise RuntimeError(
            "OpenClaw runtime bootstrap failed. "
            "For local runs, install the pinned OpenClaw CLI or use Docker. "
            "For deployed runs, ensure network access and persistent storage are enabled."
        ) from exc
    _export_runtime(bootstrapped_runtime)
    _ensure_minimal_config_file(home_dir)
    logger.info("Bootstrapped OpenClaw runtime at %s", bootstrapped_runtime.openclaw_bin)


@dataclass(frozen=True)
class _OpenClawRuntimePaths:
    node_bin: Path
    npm_bin: Path | None
    openclaw_bin: Path


def _read_valid_gateway_command() -> str | None:
    raw_command = os.getenv("OPENCLAW_GATEWAY_COMMAND")
    if raw_command is None:
        return None

    normalized_command = raw_command.strip()
    if not normalized_command:
        return None

    try:
        command_parts = shlex.split(normalized_command)
    except ValueError:
        logger.warning("Ignoring invalid OPENCLAW_GATEWAY_COMMAND=%r", raw_command)
        os.environ.pop("OPENCLAW_GATEWAY_COMMAND", None)
        return None

    normalized_parts = _normalize_gateway_command_parts(command_parts)
    return shlex.join(normalized_parts)


def _normalize_gateway_command_parts(command_parts: list[str]) -> list[str]:
    if len(command_parts) >= 2 and command_parts[1] == "gateway":
        if len(command_parts) == 2 or command_parts[2].startswith("-"):
            return [command_parts[0], "gateway", "run", *command_parts[2:]]
    return command_parts


def _build_installed_gateway_command() -> str | None:
    openclaw_bin = shutil.which("openclaw")
    if not openclaw_bin:
        return None
    return f"{shlex.quote(openclaw_bin)} gateway run"


def _read_bool_env(name: str, *, default: bool) -> bool:
    value = os.getenv(name)
    if value is None:
        return default
    return value.strip().lower() in {"1", "true", "yes", "on"}


def _read_runtime_version(name: str, default: str) -> str:
    return _normalize_runtime_value(os.getenv(name), default)


def _normalize_runtime_value(value: str | None, default: str) -> str:
    if value is None:
        return default

    normalized = value.strip()
    if not normalized or re.search(r"\s", normalized):
        return default

    return normalized


def _bootstrap_runtime(home_dir: Path, node_version: str, openclaw_version: str) -> _OpenClawRuntimePaths:
    runtime_root = home_dir / ".runtime"
    runtime_root.mkdir(parents=True, exist_ok=True)

    node_platform = _node_platform_name()
    node_dir = runtime_root / f"node-v{node_version}-{node_platform}"
    prefix_dir = runtime_root / f"openclaw-{openclaw_version}"
    marker_path = prefix_dir / ".bootstrap-state.json"
    lock_path = runtime_root / ".bootstrap.lock"
    node_bin = node_dir / "bin" / "node"
    npm_bin = node_dir / "bin" / "npm"
    openclaw_bin = prefix_dir / "bin" / "openclaw"

    with lock_path.open("w", encoding="utf-8") as lock_file:
        _lock_file(lock_file)

        if not _has_usable_node_install(node_bin, npm_bin):
            shutil.rmtree(node_dir, ignore_errors=True)
            _install_node(node_version, node_platform, runtime_root)

        marker = _read_marker(marker_path)
        expected_marker = {
            "node_version": node_version,
            "openclaw_version": openclaw_version,
            "platform": node_platform,
        }
        if marker != expected_marker or not openclaw_bin.exists() or _read_openclaw_version(openclaw_bin, node_bin) != openclaw_version:
            shutil.rmtree(prefix_dir, ignore_errors=True)
            _install_openclaw_package(npm_bin, node_bin, prefix_dir, openclaw_version)
            marker_path.write_text(json.dumps(expected_marker, indent=2), encoding="utf-8")

    return _OpenClawRuntimePaths(node_bin=node_bin, npm_bin=npm_bin, openclaw_bin=openclaw_bin)


def _lock_file(lock_file) -> None:
    if fcntl is not None:
        fcntl.flock(lock_file.fileno(), fcntl.LOCK_EX)


def _resolve_bootstrap_home_dir() -> Path:
    explicit_home = os.getenv("OPENCLAW_HOME")
    if explicit_home:
        home_dir = Path(explicit_home.strip()).expanduser().resolve()
        _export_home_paths(home_dir)
        return home_dir

    default_home = Path("/app/mnt/openclaw").expanduser().resolve()
    if _can_write_home(default_home):
        _export_home_paths(default_home)
        return default_home

    fallback_home = Path.cwd().resolve() / ".data" / "openclaw"
    _export_home_paths(fallback_home)
    logger.info("Falling back to local OpenClaw home at %s", fallback_home)
    return fallback_home


def _node_platform_name() -> str:
    system = platform.system().lower()
    machine = platform.machine().lower()
    if system == "linux":
        if machine in {"x86_64", "amd64"}:
            return "linux-x64"
        if machine in {"arm64", "aarch64"}:
            return "linux-arm64"
    if system == "darwin":
        if machine in {"x86_64", "amd64"}:
            return "darwin-x64"
        if machine in {"arm64", "aarch64"}:
            return "darwin-arm64"
    raise RuntimeError(f"Unsupported OpenClaw runtime platform: system={system} arch={machine}")


def _can_write_home(home_dir: Path) -> bool:
    try:
        home_dir.mkdir(parents=True, exist_ok=True)
        probe_path = home_dir / ".write-probe"
        probe_path.write_text("ok", encoding="utf-8")
        probe_path.unlink()
        return True
    except OSError:
        return False


def _install_node(node_version: str, node_platform: str, runtime_root: Path) -> None:
    node_version = _normalize_runtime_value(node_version, _DEFAULT_NODE_VERSION)
    node_platform = re.sub(r"\s+", "", node_platform.strip())
    if node_platform not in {"linux-x64", "linux-arm64", "darwin-x64", "darwin-arm64"}:
        raise RuntimeError(f"Unsupported normalized OpenClaw runtime platform: {node_platform!r}")

    archive_name = f"node-v{node_version}-{node_platform}.tar.xz"
    download_url = f"https://nodejs.org/dist/v{node_version}/{archive_name}"
    checksums_url = f"https://nodejs.org/dist/v{node_version}/SHASUMS256.txt"
    if re.search(r"\s", download_url):
        raise RuntimeError(f"Node runtime URL contains whitespace after normalization: {download_url!r}")
    logger.info("Downloading Node runtime from %s", download_url)

    with tempfile.TemporaryDirectory(prefix="openclaw-node-") as temp_dir:
        archive_path = Path(temp_dir) / archive_name
        with urllib.request.urlopen(download_url, timeout=60) as response, archive_path.open("wb") as output_file:
            shutil.copyfileobj(response, output_file)
        expected_sha256 = _read_expected_sha256(checksums_url, archive_name)
        actual_sha256 = _sha256_file(archive_path)
        if actual_sha256 != expected_sha256:
            raise RuntimeError(
                f"Node runtime checksum mismatch for {archive_name}. "
                f"expected={expected_sha256} actual={actual_sha256}"
            )

        with tarfile.open(archive_path, mode="r:*") as archive:
            try:
                archive.extractall(runtime_root, filter="data")
            except TypeError:
                archive.extractall(runtime_root)


def _install_openclaw_package(npm_bin: Path, node_bin: Path, prefix_dir: Path, openclaw_version: str) -> None:
    prefix_dir.mkdir(parents=True, exist_ok=True)
    npm_cache_dir = prefix_dir / ".npm-cache"
    npm_cache_dir.mkdir(parents=True, exist_ok=True)
    npm_cli = node_bin.parent.parent / "lib" / "node_modules" / "npm" / "bin" / "npm-cli.js"
    if not npm_cli.exists():
        raise RuntimeError(f"Bootstrapped npm CLI is missing at {npm_cli}")

    env = os.environ.copy()
    env["PATH"] = f"{node_bin.parent}{os.pathsep}{env.get('PATH', '')}".rstrip(os.pathsep)
    env["HOME"] = env.get("HOME") or str(prefix_dir)
    env["npm_config_cache"] = str(npm_cache_dir)
    env["NPM_CONFIG_CACHE"] = str(npm_cache_dir)
    env["npm_config_loglevel"] = "verbose"
    env["npm_config_optional"] = "false"
    env["npm_config_update_notifier"] = "false"

    command = [
        str(node_bin),
        str(npm_cli),
        "install",
        "--global",
        "--prefix",
        str(prefix_dir),
        "--no-update-notifier",
        "--no-fund",
        "--no-audit",
        f"openclaw@{openclaw_version}",
    ]
    completed = subprocess.run(command, capture_output=True, text=True, env=env, timeout=300, check=False)
    if completed.returncode != 0:
        raise RuntimeError(
            "Failed to install pinned OpenClaw runtime. "
            f"returncode={completed.returncode} "
            f"stdout={completed.stdout[-1000:]} stderr={completed.stderr[-1000:]}"
        )

    _install_davey_binding(node_bin, prefix_dir, env)


def _install_davey_binding(node_bin: Path, prefix_dir: Path, env: dict[str, str]) -> None:
    davey_package = prefix_dir / "node_modules" / "@snazzah" / "davey" / "package.json"
    if not davey_package.exists():
        return

    binding_name = _resolve_davey_binding_name()
    davey_metadata = json.loads(davey_package.read_text(encoding="utf-8"))
    optional_dependencies = davey_metadata.get("optionalDependencies", {})
    binding_version = optional_dependencies.get(binding_name)
    if not binding_version:
        raise RuntimeError(f"Could not resolve Davey binding version for {binding_name}")

    npm_cli = node_bin.parent.parent / "lib" / "node_modules" / "npm" / "bin" / "npm-cli.js"
    command = [
        str(node_bin),
        str(npm_cli),
        "--prefix",
        str(prefix_dir),
        "install",
        "--no-save",
        "--ignore-scripts",
        f"{binding_name}@{binding_version}",
    ]
    completed = subprocess.run(command, capture_output=True, text=True, env=env, timeout=180, check=False)
    if completed.returncode != 0:
        raise RuntimeError(
            "Failed to install Davey native binding. "
            f"returncode={completed.returncode} "
            f"stdout={completed.stdout[-1000:]} stderr={completed.stderr[-1000:]}"
        )


def _resolve_davey_binding_name() -> str:
    system = platform.system().lower()
    machine = platform.machine().lower()
    libc_name, _ = platform.libc_ver()
    is_musl = "musl" in libc_name.lower()

    if system == "linux":
        if machine in {"x86_64", "amd64"}:
            return "@snazzah/davey-linux-x64-musl" if is_musl else "@snazzah/davey-linux-x64-gnu"
        if machine in {"arm64", "aarch64"}:
            return "@snazzah/davey-linux-arm64-musl" if is_musl else "@snazzah/davey-linux-arm64-gnu"
    if system == "darwin":
        if machine in {"x86_64", "amd64"}:
            return "@snazzah/davey-darwin-x64"
        if machine in {"arm64", "aarch64"}:
            return "@snazzah/davey-darwin-arm64"

    raise RuntimeError(f"Unsupported Davey native binding platform: system={system} arch={machine} libc={libc_name}")


def _ensure_minimal_config_file(home_dir: Path) -> None:
    _export_home_paths(home_dir)
    state_dir = Path(os.environ["OPENCLAW_STATE_DIR"]).expanduser().resolve()
    config_path = Path(os.environ["OPENCLAW_CONFIG_PATH"]).expanduser().resolve()
    log_path = Path(os.environ["OPENCLAW_LOG_PATH"]).expanduser().resolve()

    home_dir.mkdir(parents=True, exist_ok=True)
    state_dir.mkdir(parents=True, exist_ok=True)
    config_path.parent.mkdir(parents=True, exist_ok=True)
    log_path.parent.mkdir(parents=True, exist_ok=True)

    if config_path.exists():
        return

    gateway_token = (os.getenv("OPENCLAW_GATEWAY_TOKEN") or os.getenv("APP_TOKEN") or "openclaw-local-token").strip()
    os.environ.setdefault("OPENCLAW_GATEWAY_TOKEN", gateway_token)
    provider_model = (os.getenv("OPENCLAW_PROVIDER_MODEL") or "openai/gpt-5.4").strip()

    payload = {
        "gateway": {
            "mode": "local",
            "bind": "loopback",
            "port": int(os.getenv("OPENCLAW_PORT", "18789")),
            "auth": {"mode": "token", "token": gateway_token},
            "http": {"endpoints": {"responses": {"enabled": True}}},
        },
        "agents": {"defaults": {"model": {"primary": provider_model}}},
    }

    fd = os.open(config_path, os.O_WRONLY | os.O_CREAT | os.O_TRUNC, 0o600)
    with os.fdopen(fd, "w", encoding="utf-8") as config_file:
        json.dump(payload, config_file, indent=2)
    try:
        config_path.chmod(0o600)
    except OSError:
        logger.debug("Unable to set restrictive permissions on OpenClaw config path", exc_info=True)


def _export_runtime(runtime: _OpenClawRuntimePaths) -> None:
    os.environ["OPENCLAW_NODE_BIN"] = str(runtime.node_bin)
    os.environ.setdefault("NODE_OPTIONS", _DEFAULT_NODE_OPTIONS)
    gateway_bin = shlex.quote(str(runtime.openclaw_bin))
    os.environ["OPENCLAW_GATEWAY_COMMAND"] = f"{gateway_bin} gateway run"


def _export_home_paths(home_dir: Path) -> None:
    resolved_home = str(home_dir.expanduser().resolve())
    os.environ["OPENCLAW_HOME"] = resolved_home
    os.environ["OPENCLAW_STATE_DIR"] = str((home_dir / "state").expanduser().resolve())
    os.environ["OPENCLAW_CONFIG_PATH"] = str((home_dir / "openclaw.json").expanduser().resolve())
    os.environ["OPENCLAW_LOG_PATH"] = str((home_dir / "logs" / "openclaw-gateway.log").expanduser().resolve())


def _has_usable_node_install(node_bin: Path, npm_bin: Path) -> bool:
    if not node_bin.exists() or not npm_bin.exists():
        return False
    detected_version = _read_semver([str(node_bin), "--version"])
    if detected_version is None or detected_version < _MIN_NODE_VERSION:
        return False
    return _read_semver([str(npm_bin), "--version"]) is not None


def _read_semver(command: list[str]) -> tuple[int, int, int] | None:
    try:
        completed = subprocess.run(command, capture_output=True, text=True, check=False)
    except OSError:
        return None
    if completed.returncode != 0:
        return None
    raw = (completed.stdout.strip() or completed.stderr.strip()).lstrip("v")
    parts = raw.split(".")
    if len(parts) < 3:
        return None
    try:
        return int(parts[0]), int(parts[1]), int(parts[2])
    except ValueError:
        return None


def _read_openclaw_version(openclaw_bin: Path, node_bin: Path) -> str | None:
    env = os.environ.copy()
    env["PATH"] = f"{node_bin.parent}{os.pathsep}{env.get('PATH', '')}".rstrip(os.pathsep)
    completed = subprocess.run(
        [str(openclaw_bin), "--version"],
        capture_output=True,
        text=True,
        env=env,
        timeout=30,
        check=False,
    )
    if completed.returncode != 0:
        return None
    raw = completed.stdout.strip() or completed.stderr.strip()
    if not raw:
        return None
    match = re.search(r"\b(\d+\.\d+\.\d+)\b", raw)
    if match is None:
        return None
    return match.group(1)


def _read_expected_sha256(checksums_url: str, archive_name: str) -> str:
    with urllib.request.urlopen(checksums_url, timeout=30) as response:
        checksums_text = response.read().decode("utf-8")
    for line in checksums_text.splitlines():
        parts = line.strip().split()
        if len(parts) == 2 and parts[1] == archive_name:
            return parts[0]
    raise RuntimeError(f"Could not find checksum for {archive_name} in {checksums_url}")


def _sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as file_handle:
        for chunk in iter(lambda: file_handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _read_marker(path: Path) -> dict[str, str] | None:
    if not path.exists():
        return None
    try:
        raw = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return None
    return raw if isinstance(raw, dict) else None
