# Information
Changes your discord status every 3 seconds to the next frame. Basically creating an animated status.
# Setting up
Go to `config.json`. You'll see this JSON table:
```
{
  "token": "XXX",
  "frames": [
    {"str":"The time is: #curtime#", "emoji":"\u23F0"},
    {"str":"My server count: #servcount#", "emoji":"🤡"}
  ],
  "speed": 3
}
```
Change the token field value to your user auth token.
You can add and remove frames by putting more frames in the `frames` table, and separating them by a `,`
The last frame string should not have a `,` at the end of it.
`str` stands for the status text, and `emoji` stands for the status emoji.
# Regular expressions
You can use regex in your frame strings. For example, if you type `#curtime#` in your frame string, it will get replaced with current time displayed as `HOUR:MINUTE`. An example frame for this would be: `{"str":"The time is: #curtime#", "emoji":"\u23F0"}`, displaying current time with an alarm clock emoji.
# Getting user auth token
Open up your discord and press `Ctrl+Shift+I`
Then, open up the `Network` tab in the popped up window.
Change your status to something else.
You will see multiple requests popping up in the network tab. Click the one with the name of `settings`
Scroll down to `Request Headers`, and find `authorization` field in there. 
This field contains your user auth token.
