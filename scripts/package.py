from pathlib import Path
import shutil

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT.parent / f"{ROOT.name}.zip"

exclude_names = {".pytest_cache", "__pycache__", "dist", "build"}
exclude_suffixes = {".pyc"}

if OUT.exists():
    OUT.unlink()

for path in list(ROOT.rglob("*")):
    if path.name in exclude_names and path.is_dir():
        shutil.rmtree(path)
    elif path.suffix in exclude_suffixes and path.exists():
        path.unlink()

shutil.make_archive(str(OUT.with_suffix("")), "zip", ROOT.parent, ROOT.name)
print(OUT)
