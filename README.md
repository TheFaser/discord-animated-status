![Python 3.8.0](https://img.shields.io/badge/python-3.8.0-brightgreen) ![Gui PyQT](https://img.shields.io/badge/gui-pyqt-blue) ![Version](https://img.shields.io/badge/version-2.0--alpha-orange)

# Information
External libraries used:
```
PyQT
Requests
```
Will not work with bot tokens since the core edits your profile's settings (basically repeating the `settings` request with special parameters for status editing).  
  
You'll need to get your own user authorization token in order for it to work.  
  
Please keep in mind that your user authorization token is an important thing which basically allows anyone to do things with malicious intents on your discord account (sending messages, leaving servers, etc.). Discord Animated Status in no way uses this information with malicious intents, and only uses it (once) to change your custom user status.
