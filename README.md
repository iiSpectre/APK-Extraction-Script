# APKExtraction-Script
Recursively scans for APK files, extracts their contents, and collects embedded image assets (PNG, JPG, JPEG). Images are labeled as Bugdroid-related or general based on path and filename keywords, then copied to separate output directories with collision-safe, resolution-prefixed filenames.

# Instructions:
Install the latest Python from the [Microsoft Store](https://apps.microsoft.com/detail/9pnrbtzxmb4z).

Open Command Prompt and execute `pip install pillow`.

Place APKExtraction.py into the folder you'd like for it to scan.

Click on an empty space on the address bar of the folder and type `powershell`, and press enter.

In the Powershell window, run `python APKExtraction.py`.

The script will display:
* How many APK's have been detected
* Which APK is currently being extracted
* When the script is finished

Note: this script has only been tested/used with Samsung Firmware files, it may work with firmware from other devices.
