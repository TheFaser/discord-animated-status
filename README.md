# Information
Changes your discord status every 3 seconds to the next frame. Basically creating an animated status.
# Setting up
Go to `config.txt`. You'l see this JSON table:
```
{
    "token": "XXX",
    "frames": [
      "This is frame 1",
      "This is frame 2",
      "This is frame 3"
    ]
}
```
Change the token field value to your user auth token.
You can add and remove frames by putting more strings in the `frames` table, and separating them by a `,`
The last frame string should not have a `,` at the end of it.
# Getting user auth token
Open up your discord and press `Ctrl+Shift+I`
Then, open up the `Network` tab in the popped up window.
Change your status to something else.
You will see multiple requests popping up in the network tab. Click the one with the name of `settings`
Scroll down to `Request Headers`, and find `authorization` field in there. 
This field contains your user auth token.
