"""Entry for make.fun news-image-20261125 (dudukuyz).

Copies the repository-held editorial image (entry.png) to the output
directory as entry.png. No network, no randomness: every run writes
the same bytes. The image is a JPEG in an entry.png name, which the
gate accepts (it tells PNG from JPEG by the first bytes).

Before copying, the image is checked against the gate's own rules:
format by magic bytes, dimensions at most 1024x1024 (parsed from the
PNG IHDR or the JPEG frame header), a complete JPEG (ends with the
EOI marker), and size at most 1 MiB. A bad image fails loudly here
instead of reaching the gate as a Valid 0.
"""

import os
import shutil
import struct
from pathlib import Path

HERE = Path(__file__).resolve().parent
OUT_DIR = Path(os.environ.get("MAKEFUN_OUTPUT_DIR", "/output"))
MAX_BYTES = 1_048_576
MAX_DIM = 1024

PNG_MAGIC = b"\x89PNG\r\n\x1a\n"
JPEG_MAGIC = b"\xff\xd8\xff"


def png_dimensions(data: bytes) -> tuple[int, int]:
    # IHDR: 8-byte magic, 4-byte length, 4-byte "IHDR", then width, height.
    if len(data) < 24 or data[12:16] != b"IHDR":
        raise SystemExit("malformed PNG: missing IHDR")
    width, height = struct.unpack(">II", data[16:24])
    return width, height


def jpeg_dimensions(data: bytes) -> tuple[int, int]:
    # Walk JPEG segments until a Start Of Frame marker gives dimensions.
    i = 2
    while i + 9 <= len(data):
        if data[i] != 0xFF:
            raise SystemExit("malformed JPEG: bad segment marker")
        marker = data[i + 1]
        if marker in (0xD8, 0xD9) or 0xD0 <= marker <= 0xD7:
            i += 2
            continue
        if i + 4 > len(data):
            raise SystemExit("malformed JPEG: truncated segment")
        seg_len = struct.unpack(">H", data[i + 2:i + 4])[0]
        if seg_len < 2 or i + 2 + seg_len > len(data):
            raise SystemExit("malformed JPEG: truncated segment")
        if marker in (0xC0, 0xC1, 0xC2):  # SOF0/1/2: precision, height, width
            height, width = struct.unpack(">HH", data[i + 5:i + 9])
            return width, height
        i += 2 + seg_len
    raise SystemExit("malformed JPEG: no frame header found")


def main() -> None:
    src = HERE / "entry.png"
    if not src.is_file():
        raise SystemExit(f"missing entry image: {src}")
    data = src.read_bytes()
    if len(data) > MAX_BYTES:
        raise SystemExit("entry image exceeds the 1 MiB gate cap")
    if data.startswith(PNG_MAGIC):
        width, height = png_dimensions(data)
    elif data.startswith(JPEG_MAGIC):
        width, height = jpeg_dimensions(data)
        if not data.endswith(b"\xff\xd9"):
            raise SystemExit("malformed JPEG: missing end marker")
    else:
        raise SystemExit("entry image is neither PNG nor JPEG")
    if width > MAX_DIM or height > MAX_DIM:
        raise SystemExit(f"entry image {width}x{height} exceeds 1024x1024")
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(src, OUT_DIR / "entry.png")


if __name__ == "__main__":
    main()
