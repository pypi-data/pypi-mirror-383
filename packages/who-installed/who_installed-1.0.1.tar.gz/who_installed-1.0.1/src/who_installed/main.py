from pathlib import Path
import os
import typer
import rich
from subprocess import CalledProcessError, check_output
import attrs
import more_itertools
import re
from enum import Enum

app = typer.Typer()


@attrs.frozen(kw_only=True)
class Package:
    name: str
    version: str


@attrs.frozen(kw_only=True)
class Executable:
    name: str
    package: Package


class Installer(Enum):
    uv = "uv"
    cargo = "cargo"
    pipx = "pipx"
    scoop = "scoop"
    winget = "winget"
    choco = "choco"
    bun = "bun"
    npm = "npm"
    pnpm = "pnpm"
    go = "go"


ANSI_ESCAPE_PAT = re.compile(
    rb"(?:\x1B[@-Z\\-_]|[\x80-\x9A\x9C-\x9F]|(?:\x1B\[|\x9B)[0-?]*[ -/]*[@-~])"
)


def _strip_ansi_colors(b: bytes) -> bytes:
    """Based on https://stackoverflow.com/a/14693789/3337893"""
    # 7-bit and 8-bit C1 ANSI sequences
    return ANSI_ESCAPE_PAT.sub(b"", b)


def list_installed_uv() -> list[Executable]:
    result = str(check_output(["uv", "tool", "list"]), encoding="utf8")
    lines = result.splitlines()
    executables: list[Executable] = []
    for package_lines in more_itertools.split_before(
        lines, lambda line: not line.startswith("-")
    ):
        package_name, package_version = package_lines[0].split(" ")
        package = Package(name=package_name, version=package_version)
        for line in package_lines[1:]:
            exe = Executable(package=package, name=line[2:])
            executables.append(exe)
    return executables


def list_installed_cargo() -> list[Executable]:
    result = str(check_output(["cargo", "install", "--list"]), encoding="utf8")
    lines = result.splitlines()
    executables: list[Executable] = []
    for package_lines in more_itertools.split_before(
        lines, lambda line: not line.startswith(" ")
    ):
        package_name, package_version, *_ = package_lines[0].split(" ")
        package = Package(name=package_name, version=package_version)
        for line in package_lines[1:]:
            exe = Executable(package=package, name=line.strip())
            executables.append(exe)
    return executables


def list_installed_pipx() -> list[Executable]:
    result = str(check_output(["pipx", "list"]), encoding="utf8")
    lines = result.splitlines()[2:]
    executables: list[Executable] = []
    for package_lines in more_itertools.split_before(
        lines, lambda line: line.strip().startswith("package")
    ):
        # `   package black 23.12.0, installed using Python 3.11.1`
        package_name, package_version = package_lines[0].split(",")[0].split(" ")[-2:]
        package = Package(name=package_name, version=package_version)
        for line in package_lines[1:]:
            exe = Executable(package=package, name=line.split("- ")[-1])
            executables.append(exe)
    return executables


def _scoop_list_packages():
    result = str(
        _strip_ansi_colors(check_output(["scoop", "list"], shell=True)), encoding="utf8"
    )
    lines = result.splitlines()[4:]
    packages: list[Package] = []
    for line in lines:
        if not line:
            continue
        name, version, *_ = line.split()
        packages.append(Package(name=name, version=version))
    return packages


def _scoop_list_binaries(package: Package):
    output = check_output(["scoop", "info", package.name], shell=True)
    stripped = _strip_ansi_colors(output)
    result = str(stripped, encoding="utf8", errors="replace")
    lines = result.splitlines()
    executables: list[Executable] = []
    for line in lines:
        if not line.startswith("Binaries"):
            continue
        # `Binaries    : 7z.exe | 7zFM.exe | 7zG.exe`
        # `Binaries    : bin\gswin64.exe | bin\gswin64c.exe | gs.exe
        for binary in line.partition(":")[-1].strip().split(" | "):
            binary = binary.rpartition("\\")[-1]
            executables.append(Executable(name=binary, package=package))
    return executables


def list_installed_scoop() -> list[Executable]:
    packages = _scoop_list_packages()
    executables: list[Executable] = []
    for package in packages:
        executables.extend(_scoop_list_binaries(package))
    return executables


def posh_get_command(name: str) -> list[Path]:
    result = str(
        check_output(["powershell.exe", "-c", f"(get-command -All {name}).source"]),
        encoding="utf8",
    )
    return [Path(line) for line in result.splitlines()]


def cmd_where(name: str) -> list[Path]:
    result = str(check_output(["cmd.exe", "/c", "where", name]), encoding="utf8")
    return [Path(line) for line in result.splitlines()]


def get_paths(name: str) -> list[Path]:
    try:
        posh = posh_get_command(name)
    except CalledProcessError:
        print("get-command yielded no results.")
        posh = []

    try:
        cmd = cmd_where(name)
    except CalledProcessError:
        print("where yielded no results.")
        cmd = []

    return list(set(posh + cmd))


LOCAL_APP_DATA = os.environ.get("LOCALAPPDATA")
assert LOCAL_APP_DATA
APP_DATA = os.environ.get("APPDATA")
assert APP_DATA

WINGET_PACKAGES_PATH = Path(LOCAL_APP_DATA) / "Microsoft" / "WinGet" / "Packages"

SCOOP_SHIMS_PATH = Path.home() / "scoop" / "shims"

CHOCOLATY_BIN_PATH = Path(r"C:\ProgramData\chocolatey\bin")
BUN_BIN_PATH = Path().home() / ".bun" / "bin"

NPM_BIN_PATH1 = Path(APP_DATA) / "npm"
NPM_BIN_PATH2 = Path(LOCAL_APP_DATA) / "npm"
PNPM_BIN_PATH1 = Path(APP_DATA) / "pnpm"
PNPM_BIN_PATH2 = Path(LOCAL_APP_DATA) / "pnpm"

GO_PATH = os.environ.get("GOPATH")
GO_BIN_PATH = Path(GO_PATH) / "bin" if GO_PATH else Path.home() / "go" / "bin"


def get_installer_by_path(path: Path) -> Installer | None:
    if path.is_relative_to(WINGET_PACKAGES_PATH):
        return Installer.winget
    elif path.is_relative_to(SCOOP_SHIMS_PATH):
        return Installer.scoop
    elif path.is_relative_to(CHOCOLATY_BIN_PATH):
        return Installer.choco
    elif path.is_relative_to(BUN_BIN_PATH):
        return Installer.bun
    elif path.is_relative_to(GO_BIN_PATH):
        return Installer.go
    elif path.is_relative_to(NPM_BIN_PATH1) or path.is_relative_to(NPM_BIN_PATH2):
        return Installer.npm
    elif path.is_relative_to(PNPM_BIN_PATH1) or path.is_relative_to(PNPM_BIN_PATH2):
        return Installer.pnpm

    return None


def clean_name(name: str) -> str:
    return str(Path(name).with_suffix("")).casefold()


@app.command()
def who_installed(name: str, show_paths: bool = False):
    installers: set[Installer] = set()
    paths = get_paths(name)
    if show_paths:
        rich.print(paths)
    for path in paths:
        if installer := get_installer_by_path(path):
            installers.add(installer)

    for installer, get_exes in (
        (Installer.uv, list_installed_uv),
        (Installer.cargo, list_installed_cargo),
        (Installer.pipx, list_installed_pipx),
    ):
        try:
            exes = get_exes()
        except CalledProcessError:
            print(f"Failed checking for {installer.value}")
            continue

        for exe in exes:
            if clean_name(name) == clean_name(exe.name):
                installers.add(installer)

    rich.print(installers)


if __name__ == "__main__":
    app()
