import os
import zipfile
import shutil
from pathlib import Path
from PIL import Image


BASE_DIR = Path.cwd()
TEMP_EXTRACT_DIR = BASE_DIR / "_apk_extracted"

IMAGE_OUTPUT_DIR = BASE_DIR / "output_images"
BUGDROID_OUTPUT_DIR = BASE_DIR / "output_bugdroid_images"
MEDIA_OUTPUT_DIR = BASE_DIR / "output_media"

IMAGE_EXTENSIONS = {".png", ".jpg", ".jpeg"}
MEDIA_EXTENSIONS = {
    ".ogg", ".mp3", ".wav", ".flac", ".aac", ".m4a",
    ".mp4", ".3gp", ".mkv", ".avi", ".webm"
}

BUGDROID_KEYWORDS = {"robot", "encroid", "droid"}

processed_files: set[Path] = set()

def is_inside_extracted(path: Path) -> bool:
    try:
        path.resolve().relative_to(TEMP_EXTRACT_DIR.resolve())
        return True
    except ValueError:
        return False

def find_apks(root: Path) -> list[Path]:
    return [
        p for p in root.rglob("*.apk")
        if p.is_file()
        and not p.is_symlink()
        and not is_inside_extracted(p.parent)
    ]

def extract_apk(apk_path: Path) -> Path | None:
    target_dir = TEMP_EXTRACT_DIR / apk_path.stem
    try:
        with zipfile.ZipFile(apk_path) as z:
            z.extractall(target_dir)
        return target_dir
    except zipfile.BadZipFile:
        print(f"Warning: Invalid APK '{apk_path}'")
    except Exception as e:
        print(f"Error extracting '{apk_path}': {e}")
    return None

def handle_file(file_path: Path, source_label: str):
    try:
        real_path = file_path.resolve()
    except Exception:
        return

    if real_path in processed_files:
        return
    processed_files.add(real_path)

    ext = file_path.suffix.lower()
    if ext not in IMAGE_EXTENSIONS and ext not in MEDIA_EXTENSIONS:
        return

    path_lower = str(file_path).lower()
    is_bugdroid = any(k in path_lower for k in BUGDROID_KEYWORDS)

    if ext in IMAGE_EXTENSIONS:
        try:
            with Image.open(file_path) as img:
                res = f"{img.width}x{img.height}"
        except Exception:
            res = "unknown"

        out_dir = BUGDROID_OUTPUT_DIR if is_bugdroid else IMAGE_OUTPUT_DIR
        dest = out_dir / f"{source_label}_{res}_{file_path.name}"
        shutil.copy2(file_path, dest)

    elif ext in MEDIA_EXTENSIONS:
        dest = MEDIA_OUTPUT_DIR / f"{source_label}_{file_path.name}"
        shutil.copy2(file_path, dest)

def scan_directory(root: Path, source_label: str, allow_extracted: bool):
    for path in root.rglob("*"):
        if path.is_file():
            if not allow_extracted and is_inside_extracted(path.parent):
                continue
            handle_file(path, source_label)

def main():
    TEMP_EXTRACT_DIR.mkdir(exist_ok=True)
    IMAGE_OUTPUT_DIR.mkdir(exist_ok=True)
    BUGDROID_OUTPUT_DIR.mkdir(exist_ok=True)
    MEDIA_OUTPUT_DIR.mkdir(exist_ok=True)

    print("Scanning loose images and media...")
    scan_directory(BASE_DIR, "loose", allow_extracted=False)

    apks = find_apks(BASE_DIR)
    print(f"Found {len(apks)} APK(s)")

    for apk in apks:
        print(f"Extracting: {apk}")
        extracted = extract_apk(apk)
        if extracted:
            scan_directory(extracted, extracted.name, allow_extracted=True)

    print("\nDone.")
    print(f"Images: {IMAGE_OUTPUT_DIR}")
    print(f"Bugdroid images: {BUGDROID_OUTPUT_DIR}")
    print(f"Media files: {MEDIA_OUTPUT_DIR}")

if __name__ == "__main__":
    main()
