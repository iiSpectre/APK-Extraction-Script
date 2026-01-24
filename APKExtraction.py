import os
import sys
import zipfile
import shutil
from pathlib import Path
from PIL import Image
import hashlib
from concurrent.futures import ThreadPoolExecutor, as_completed
import threading

USE_HARDLINKS = True
PARTIAL_HASH_SIZE = 64 * 1024       # 64 KB
FULL_HASH_LIMIT = 20 * 1024 * 1024  # 20 MB
MAX_EXTRACT_THREADS = min(8, os.cpu_count() or 4)
MAX_FILE_THREADS = min(8, os.cpu_count() or 4)

BASE_DIR = Path(__file__).parent.resolve()
TEMP_EXTRACT_DIR = BASE_DIR / "_apk_extracted"
IMAGE_OUTPUT_DIR = BASE_DIR / "output_images"
BUGDROID_OUTPUT_DIR = BASE_DIR / "output_bugdroid_images"
MEDIA_OUTPUT_DIR = BASE_DIR / "output_media"

IMAGE_EXTENSIONS = {".png", ".jpg", ".jpeg"}
MEDIA_EXTENSIONS = {".ogg", ".mp3", ".wav", ".flac", ".aac", ".m4a",
                    ".mp4", ".3gp", ".mkv", ".avi", ".webm"}
BUGDROID_KEYWORDS = {"robot", "encroid", "droid"}

seen_hashes: dict[str, set[str]] = {}
hash_lock = threading.Lock()
print_lock = threading.Lock()

def quick_file_hash(path: Path) -> str:
    try:
        size = path.stat().st_size
        h = hashlib.sha1()
        with path.open("rb") as f:
            h.update(f.read(PARTIAL_HASH_SIZE))
        if size > FULL_HASH_LIMIT:
            with path.open("rb") as f:
                f.seek(max(0, size - PARTIAL_HASH_SIZE))
                h.update(f.read(PARTIAL_HASH_SIZE))
        return f"{size}:{h.hexdigest()}"
    except Exception:
        return ""

def full_file_hash(path: Path) -> str:
    h = hashlib.sha256()
    try:
        with path.open("rb") as f:
            while chunk := f.read(8192):
                h.update(chunk)
        return h.hexdigest()
    except Exception:
        return ""

def handle_file(file_path: Path, source_label: str):
    ext = file_path.suffix.lower()
    if ext not in IMAGE_EXTENSIONS and ext not in MEDIA_EXTENSIONS:
        return

    try:
        real_path = file_path.resolve()
        size = real_path.stat().st_size
    except Exception:
        return

    qh = quick_file_hash(real_path)
    if not qh:
        return

    is_duplicate = False
    fh = None

    with hash_lock:
        if qh not in seen_hashes:
            seen_hashes[qh] = set()
        else:
            fh = full_file_hash(real_path)
            if fh in seen_hashes[qh]:
                is_duplicate = True

    if is_duplicate:
        return

    if fh is None:
        if size <= FULL_HASH_LIMIT:
            fh = full_file_hash(real_path)
        else:
            fh = "LARGE"

    with hash_lock:
        seen_hashes[qh].add(fh)

    name_lower = file_path.name.lower()
    is_bugdroid = any(k in name_lower for k in BUGDROID_KEYWORDS)
    if ext in IMAGE_EXTENSIONS:
        out_dir = BUGDROID_OUTPUT_DIR if is_bugdroid else IMAGE_OUTPUT_DIR
        try:
            with Image.open(file_path) as img:
                res = f"{img.width}x{img.height}"
        except Exception:
            res = "unknown"
        out_dir.mkdir(exist_ok=True)
        dest = out_dir / f"{source_label}_{res}_{file_path.name}"
    else:
        out_dir = MEDIA_OUTPUT_DIR
        out_dir.mkdir(exist_ok=True)
        dest = out_dir / f"{source_label}_{file_path.name}"

    try:
        if USE_HARDLINKS and not dest.exists():
            os.link(real_path, dest)
        else:
            shutil.copy2(real_path, dest)
    except Exception:
        shutil.copy2(real_path, dest)

def scan_directory(root: Path, source_label: str, use_threads=True):
    files = [p for p in root.rglob("*") if p.is_file()]
    if use_threads and files:
        with ThreadPoolExecutor(max_workers=MAX_FILE_THREADS) as executor:
            executor.map(lambda f: handle_file(f, source_label), files)
    else:
        for f in files:
            handle_file(f, source_label)

def find_apks(root: Path) -> list[Path]:
    return [p for p in root.rglob("*.apk") if p.is_file()]

def extract_apk(apk_path: Path) -> Path | None:
    with print_lock:
        print(f"Extracting: {apk_path}")
    target_dir = TEMP_EXTRACT_DIR / apk_path.stem
    try:
        with zipfile.ZipFile(apk_path) as z:
            z.extractall(target_dir)
        return target_dir
    except Exception as e:
        with print_lock:
            print(f"Error extracting '{apk_path}': {e}")
        return None

def main():
    TEMP_EXTRACT_DIR.mkdir(exist_ok=True)
    IMAGE_OUTPUT_DIR.mkdir(exist_ok=True)
    BUGDROID_OUTPUT_DIR.mkdir(exist_ok=True)
    MEDIA_OUTPUT_DIR.mkdir(exist_ok=True)

    print("Scanning loose images and media...")
    scan_directory(BASE_DIR, "loose")

    apks = find_apks(BASE_DIR)
    print(f"Found {len(apks)} APK(s)")
    print(f"Extracting using {MAX_EXTRACT_THREADS} threads...\n")

    extracted_dirs = []
    with ThreadPoolExecutor(max_workers=MAX_EXTRACT_THREADS) as executor:
        futures = [executor.submit(extract_apk, apk) for apk in apks]
        for future in as_completed(futures):
            extracted = future.result()
            if extracted:
                extracted_dirs.append(extracted)

    for extracted in extracted_dirs:
        scan_directory(extracted, extracted.name)

    if TEMP_EXTRACT_DIR.exists():
        shutil.rmtree(TEMP_EXTRACT_DIR)
        print("\nTemporary APK extraction folder deleted.")

    print("\nDone.")
    print(f"Images: {IMAGE_OUTPUT_DIR}")
    print(f"Bugdroid images: {BUGDROID_OUTPUT_DIR}")
    print(f"Media files: {MEDIA_OUTPUT_DIR}")

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"Error: {e}")

    print("\nScript finished. Press Enter to exit.")
    input()
