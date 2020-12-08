import string

VERSION_M = "2.1.0"
AUTHORS_M = ["https://github.com/eternalfrenzy", "https://github.com/RinkLinky"]
CREDITS_M = {
    "eternalfrenzy": "-Request mining and collecting data\n-Core of the status changer\n-English translation",
	"RinkLinky": "-Multithreaded GUI\n-Russian translation\n-Bugfixing"
}

# Discord api url to work with
API_URL = "https://discord.com/api/v6"
# List of ASCII-characters for checking the token
ASCII_CHARS = list(string.ascii_lowercase + string.ascii_uppercase + string.digits + string.punctuation + " ")
