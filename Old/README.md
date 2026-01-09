# APK-Extraction-Script
Recursively scans Android ROMS/Firmware files for APK files, extracts their contents, and collects embedded image assets (PNG, JPG, JPEG). Images are labeled as Bugdroid-related or general based on filename keywords, then copied to separate output directories with collision-safe, resolution-prefixed filenames.

# Instructions:
Install the latest Python from the [Microsoft Store](https://apps.microsoft.com/detail/9pnrbtzxmb4z).

Open Command Prompt and execute `pip install pillow`.

Place APKExtraction.py into the folder you'd like for it to scan.
> _Steps below not needed with One-Click Version._

Click on an empty space on the address bar of the folder and type `powershell`, and press enter.

In the Powershell window, run `python APKExtraction.py`.

The script will display:
* How many APK's have been detected
* Which APK is currently being extracted
* When the script is finished, and where the output directories to the created folders are

Note: this script has only been tested/used with Samsung Firmware files, and may work with firmware from other devices.

https://github.com/user-attachments/assets/5bf4bec7-ffbe-4b71-a89f-38f5ff4a84b2

