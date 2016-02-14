**Issue:** Need to figure out how to stream music from the server to the client

Some things I found out:

- there is a Web Sockets plug-in for Flask: http://flask-socketio.readthedocs.org/en/latest/
- gevent: http://www.gevent.org/
- A Node.js music player using Mopidy https://github.com/samcreate/Apollo-Player
- Python module for running Apple scripts to control Spotify for Mac desktop app (yuck) https://github.com/csu/PySpotifyControl
- Mopidy, Spotify extension, using Mopidy backend to stream music 
    + https://github.com/mopidy/mopidy-spotify/blob/develop/mopidy_spotify/playback.py
- Gstreamer, whatever the fuck that is: http://gstreamer.freedesktop.org/features/
- A Python music player: https://github.com/devsnd/cherrymusic
- Some guy does not explain his API. Also it's broken: https://github.com/Hexxeh/spotify-websocket-api/blob/master/examples/gstreamer.py
- GST Python -- needed for Gstreamer, I think? https://github.com/alessandrod/gst-python
- A tutorial for Gstreamer Python http://brettviren.github.io/pygst-tutorial-org/pygst-tutorial.pdf
- Oh, hmm, maybe it's Pygst I needed... some nifty shell script for putting it into the virtualenv https://gist.github.com/jegger/10003813
- Mopidy stuff:
    + https://docs.mopidy.com/en/latest/ext/http/#hosting-web-clients
    + https://docs.mopidy.com/en/latest/ext/stream/
    + http://mopidy.readthedocs.org/en/latest/api/backend/#backend-api
    + 
- Node js stuff with streaming + sockets:
    + https://github.com/JohanObrink/node-libspotify/blob/master/lib/player.js
- Heroku sockets demo:
    + https://github.com/heroku-examples/python-websockets-chat/blob/master/chat.py
- There is a client... look into this:
    + https://github.com/drsounds/bungalow
- More shit I found
    + https://github.com/bkz/social-jukebox/blob/master/mp3stream.py
- http://www.schillmania.com/projects/soundmanager2/
    + http://www.nyan.cat/original
- Some stuff about PCM frames (whatever the fuck that is)
    + http://ask.programmershare.com/107_17569527/
    + http://davidbella.github.io/hacks/spotifypcm/2013/06/25/capturing-pcm-data-from-the-libspotify-c-api
    + https://developer.spotify.com/docs/libspotify/12.1.45/structsp__session__callbacks.html#a33a31478b8de1882ad7847ad033fbaeb
- Getting educated on codecs:
    + http://www.streamingmedia.com/Articles/Editorial/What-Is-.../What-is-a-Codec-74487.aspx
- Blergh:
    + https://wiki.python.org/moin/PythonInMusic
    + http://edna.sourceforge.net/
    + http://www.anti-particle.com/old/pymps.shtml
- RTCP:
    + https://www.cs.kent.ac.uk/people/staff/jsc6/teaching/networks/l9.pdf