![Python 3.8](https://img.shields.io/badge/python-3.8-brightgreen) ![Gui PyQt5](https://img.shields.io/badge/gui-pyqt5-blue) ![Stable-Version](https://img.shields.io/badge/stable--version-2.1.0-green)

# Information
External libraries used:
* PyQt5
* requests
* pypresence
* psutil

Will not work with bot tokens since the core edits your profile's settings (basically repeating the `settings` request with special parameters for status editing).
You'll need to get your own user authorization token in order for it to work.

For Discord PRC animation needs client id of your application from [Developer Portal Applications](https://discord.com/developers/applications/)

# Getting your user authorization token
[This video](https://youtu.be/tI1lzqzLQCs) (also see the author's comment under the video)

# Safety
Please keep in mind that your user authorization token is an important thing which basically allows anyone to do things with malicious intents on your discord account (sending messages, leaving servers, etc.). Discord Animated Status in no way uses this information with malicious intents, and only uses it (once) to change your custom user status.

# Antivirus warnings
Discord Animated Status DOES NOT CONTAIN A VIRUS. Some antiviruses can show warnings about compiled exes, but that is because of how releases are compiled from source code to executables. We use PyInstaller to compile the source code to an executable, antiviruses can detect that and warn you about malware. Think about it for a moment: Even if it contains any viruses or malware, what is the point of publicly releasing the source code? You can grab the source and compile it by yourself, but to make things easier for you, we post already compiled executables in the Releases tab.
