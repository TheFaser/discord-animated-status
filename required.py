from threading import Thread
from datetime import datetime
import os
import sys
import time
import json
import string

import requests
import logging

version_m = "2.1.0 beta"
authors_m = ["https://github.com/eternalfrenzy", "https://github.com/RinkLinky"]
credits_m = {
    "eternalfrenzy": "-Request mining and collecting data\n-Core of the status changer\n-English translation",
	"RinkLinky": "-Multithreaded GUI\n-Russian translation\n-Bugfixing"
}

# Discord api url to work with
api_url = "https://discord.com/api/v6"
# List of ASCII-characters for checking the token
ascii_chars = list(string.ascii_lowercase + string.ascii_uppercase + string.digits + string.punctuation + " ")
