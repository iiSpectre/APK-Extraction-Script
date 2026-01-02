import os
import zipfile
import shutil
from PIL import Image

BASE_DIR = os.getcwd()
TEMP_EXTRACT_DIR = os.path.join(BASE_DIR, "_apk_extracted")
OUTPUT_DIR = os.path.join(BASE_DIR, "output_images")
BUGDROID_OUTPUT_DIR = os.path.join(BASE_DIR, "output_bugdroid_images")

IMAGE_EXTENSIONS = (".png", ".jpg", ".jpeg")

BUGDROID_KEYWORDS = (
    "bugdroid",
    "android_robot",
    "droidman",
    "android_mascot",
)

def find_apks(root):
    apks = []
    for dirpath, _, filenames in os.walk(root, followlinks=False):
        for file in filenames:
            if file.lower().endswith(".apk"):
                full_path = os.path.join(dirpath, file)

                if os.path.islink(full_path):
                    continue
                if not os.path.isfile(full_path):
                    continue

                apks.append(full_path)
    return apks

def extract_apk(apk_path, extract_to):
    apk_name = os.path.splitext(os.path.basename(apk_path))[0]
    target_dir = os.path.join(extract_to, apk_name)

    try:
        with zipfile.ZipFile(apk_path, 'r') as zip_ref:
            zip_ref.extractall(target_dir)
        return target_dir
    except zipfile.BadZipFile:
        print(f"Warning: '{apk_path}' is not a valid APK. Skipping...")
        return None
    except Exception as e:
        print(f"Error extracting '{apk_path}': {e}")
        return None

def process_images(extracted_dir):
    for dirpath, _, filenames in os.walk(extracted_dir):
        for file in filenames:
            if file.lower().endswith(IMAGE_EXTENSIONS):
                image_path = os.path.join(dirpath, file)

                searchable_text = f"{dirpath}/{file}".lower()
                is_bugdroid_related = any(
                    keyword in searchable_text for keyword in BUGDROID_KEYWORDS
                )

                try:
                    with Image.open(image_path) as img:
                        width, height = img.size
                        res = f"{width}x{height}"

                        output_dir = (
                            BUGDROID_OUTPUT_DIR
                            if is_bugdroid_related
                            else OUTPUT_DIR
                        )
                        os.makedirs(output_dir, exist_ok=True)

                        dest_file = os.path.join(
                            output_dir,
                            f"{os.path.basename(extracted_dir)}_{res}_{file}"
                        )

                        shutil.copy2(image_path, dest_file)

                except Exception as e:
                    print(f"Skipping image: {image_path} ({e})")

def main():
    os.makedirs(TEMP_EXTRACT_DIR, exist_ok=True)
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    os.makedirs(BUGDROID_OUTPUT_DIR, exist_ok=True)

    apks = find_apks(BASE_DIR)
    print(f"Found {len(apks)} APK(s)")

    for apk in apks:
        print(f"Extracting: {apk}")
        extracted = extract_apk(apk, TEMP_EXTRACT_DIR)
        if extracted:
            process_images(extracted)

    print("Done.")
    print(f"General images saved to: {OUTPUT_DIR}")
    print(f"Bugdroid-related images saved to: {BUGDROID_OUTPUT_DIR}")

if __name__ == "__main__":
    main()
