"""Entry for make.fun news-image-20261125 (dudukuyz).

Copies the repository-held editorial image (entry.png) to the output
directory as entry.png. No network, no randomness: every run writes
the same bytes. The image is a JPEG in an entry.png name, which the
gate accepts (it tells PNG from JPEG by the first bytes).
"""

import os
import shutil
from pathlib import Path

HERE = Path(__file__).resolve().parent
OUT_DIR = Path(os.environ.get("MAKEFUN_OUTPUT_DIR", "/output"))


def main() -> None:
    src = HERE / "entry.png"
    if not src.is_file():
        raise SystemExit(f"missing entry image: {src}")
    if src.stat().st_size > 1_048_576:
        raise SystemExit("entry image exceeds the 1 MiB gate cap")
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(src, OUT_DIR / "entry.png")


if __name__ == "__main__":
    main()
