# SimpleVoice
A really simple api for doing speech-to-text and text-to-speech
# How to use
SimpleVoice can be ran manually, or via the provided docker image. Inital run may take several minutes as moonshine downloads required assets. Once it's running, there are 2 endpoints of note:
* `/speech` Takes a .wav file and converts it to text that is then returned in a json object in the format `{"generated_text": generated_text}`
* `/text` Takes a query string of text, and returns a .wav file of a synthesised voice speaking it
# Please note
This was a something I threw together very quickly, so there's no parameters to control the voice that's used. Likewise there's no caching on the moonshine assets.