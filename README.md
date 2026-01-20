# APK-Extraction-Script
Recursively scans extracted Android ROMS/Firmware for APK files, extracts their contents, and collects embedded image assets (.png, .jpg, .jpeg). Images are labeled as Bugdroid-related or general based on filename keywords, along with video/audio files, and are then copied to separate output directories with collision-safe, resolution-prefixed filenames.

# Instructions:
Install the latest Python from the [Microsoft Store](https://apps.microsoft.com/detail/9pnrbtzxmb4z).

Open Command Prompt and execute `pip install pillow`.

Place APKExtraction.py into the folder you'd like for it to scan, and double click to run.

The script will display:
* How many APK's have been detected
* Which APK is currently being extracted
* When the script is finished, and where the output directories to the created folders are

Note: this script has been tested successfully with Samsung, HTC, Pixel, and Xiaomi Firmware, and may work with most firmware from other Android devices.

https://github.com/user-attachments/assets/3afa5e42-1d17-46e5-947e-9ffc458a7717

