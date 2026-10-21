"""Build the pinned compression extension locally without a system C++ install.

Uses Zig 0.13.0 from the project's venv. Nothing is downloaded or executed from
an unpinned branch; git submodules are resolved from the pinned parent commit.
The resulting wheel stays in .venv/build and is for this local installation.
"""
from pathlib import Path
import platform
import subprocess
import sys
from wheel.wheelfile import WheelFile

ROOT = Path(__file__).resolve().parents[1]
COMMIT = "302e43668d98f5228249b523d0376a93d2c156f8"
BUILD = ROOT / ".venv" / "build" / "pyooz"
WHEEL = BUILD.parent / "pyooz-0.1.0-cp38-abi3-win_amd64.whl"


def run(*args, cwd=ROOT):
    subprocess.run(args, cwd=cwd, check=True)


def main():
    if sys.platform != "win32" or platform.machine().lower() not in {"amd64", "x86_64"}:
        raise SystemExit("This helper supports Windows x64 only.")
    BUILD.parent.mkdir(parents=True, exist_ok=True)
    if not BUILD.exists():
        run("git", "clone", "--no-checkout", "https://github.com/KrisCris/pyooz.git", str(BUILD))
    run("git", "checkout", "--detach", COMMIT, cwd=BUILD)
    run("git", "submodule", "update", "--init", "--recursive", cwd=BUILD)
    sources = ["ooz/ooz_bindings.cpp"] + ["ooz/dep/ooz/" + name + ".cpp" for name in (
        "bitknit", "kraken", "lzna", "compress", "compr_kraken", "compr_leviathan",
        "compr_mermaid", "compr_entropy", "compr_match_finder", "compr_multiarray", "compr_tans",
    )]
    python_base = Path(sys.base_prefix)
    binary = BUILD / "ooz.pyd"
    run(sys.executable, "-m", "ziglang", "c++", "-target", "x86_64-windows-gnu",
        "-std=c++17", "-shared", "-O2", "-Wno-macro-redefined",
        "-DPy_LIMITED_API=0x03080000", "-DOOZ_BUILD_DLL=1",
        f"-I{python_base / 'include'}", "-Iooz/dep/ooz/simde", *sources,
        str(python_base / "libs" / "python3.lib"), "-o", str(binary), cwd=BUILD)
    info = "pyooz-0.1.0.dist-info"
    with WheelFile(str(WHEEL), "w") as wheel:
        wheel.write(str(binary), "ooz.pyd")
        wheel.writestr(f"{info}/METADATA", "Metadata-Version: 2.1\nName: pyooz\nVersion: 0.1.0\nRequires-Python: >=3.8\n")
        wheel.writestr(f"{info}/WHEEL", "Wheel-Version: 1.0\nGenerator: local-pinned-source-build\nRoot-Is-Purelib: false\nTag: cp38-abi3-win_amd64\n")
        wheel.writestr(f"{info}/SOURCE.txt", f"https://github.com/KrisCris/pyooz/tree/{COMMIT}\nBuilt locally; see this source and its submodules for license terms.\n")
    print(WHEEL)


if __name__ == "__main__":
    main()
