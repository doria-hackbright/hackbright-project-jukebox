## Office Jukebox

## Introduction
Office Jukebox is a crowd-sourced music player. It allows any user to create a new jukebox that they have ownership and admin rights over. They are able to play/pause/skip music and search for/add new songs from Spotify to their playlist. The jukebox also provides a unique URL used to invite guests. All users on a jukebox are connected through WebSockets, allowing realtime updates. Guests are given a limited view, with the ability to add songs to the playlist and upvote/downvote other songs. When a song is voted on, an updated version of the playlist will render for all users, ordered based on votes. And when the party's over, the admin can end the jukebox session.

## Table of Contents
* [Tech Stack](#tech_stack)
* [Jukebox Users](#users)
* [Adding and Voting on Music](#playlist)
* [Music Streaming](#music)
* [Version 2.0](#v2)
* [Author](#author)

## <a name="tech_stack"></a>Tech Stack
#### List of Technologies:
* Python
* Flask
* PostgreSQL
* SQLAlchemy
* Javascript
* jQuery
* AJAX
* Web Audio API
* Skeleton
* Loaders.css

## <a name="users"></a>Jukebox Users
#### Beginning a Jukebox

<!--gif: jukebox creation-->
![jukebox creation](/static/imgs/create_jukebox.gif)

To begin, any user can initiate a jukebox. When they create a jukebox, an encrypted Flask session with a unique admin user id is automatically generated. The jukebox and admin user are also both added to the database. The jukebox provides the admin with a music player, the ability to search for and add songs from Spotify, and a unique URL so they can invite their friends to join in and contribute to the jukebox.

<!--gif: jukebox admin view, song search and add-->
![admin view](/static/imgs/admin_view.gif)

#### Guest Users
Guests are given the ability to add new songs and upvote/downvote songs on a jukebox.

<!--gif: guest view of the jukebox-->
![guest view](/static/imgs/guest_view.gif)

## <a name="playlist"></a>Adding and Voting on Music
All users are connected via WebSockets, thus all new songs that are added and all upvotes/downvotes are rendered in realtime across all users. This ensures that users in the same jukebox will always have the most updated playlist information.

When adding new songs, users first search a keyword in the given search field. An AJAX request is sent to the server and a request is made to the Spotify Web API. The top 10 results for the keyword is returned and rendered on screen. The user then has the ability to add the song to their playlist.

## <a name="music"></a>Music Streaming
Admin users are able to play the music. Music streaming is done in two steps:
1. An AJAX request is made to the server and the server makes a request to libspotify. The server then recieves the raw PCM byte stream from Spotify.
2. The server then converts the byte stream to a wave buffer using the built-in Python wave library. This wave buffer is then streamed to the client-side and the music is played using the Web Audio API. Below is a code snippet that converts the bytestream into a wave buffer and then played using the Web Audio API.

**Python**
```python
import wave

...
buffer = wave.open("123.wav", "wb")
buffer.setparams((2, 2, 44100, 0, 'NONE', 'NONE'))

...
audio_format.sample_type == spotify.SampleType.INT16_NATIVE_ENDIAN)
buffer.writeframes(frames)
```
The buffer is a 16-bit wave file with sample rate of 44.1kHz.

**Javascript**
```javascript
window.AudioContext = window.AudioContext || window.webkitAudioContext;
var context = new AudioContext();
var songBuffer = null;

// An interface for the Audio Buffer is used: BuffAudio
var buffAudio = new BuffAudio(context, songBuffer);

function loadSound() {
    var request = new XMLHttpRequest();
    request.open('GET', "/play_song", true);
    request.responseType = 'arraybuffer';
    
    request.onload = function(evt) {
      context.decodeAudioData(request.response, function(buffer) {
        $('#loading-graphic').hide();
        buffAudio.initNewBuffer(buffer);
        buffAudio.play();
      },
      function (err) {
          console.log("ERR", err);
      });
    };
    request.send();
  }
```

## <a name="author"></a>Author
Office Jukebox is made by Doria Keung. If you have any questions regarding Office Jukebox, please do not hesitate to reach out:
<doria.keung@gmail.com> <br>
* [LinkedIn](https://www.linkedin.com/in/doriakeung) <br>
* [Website](http://doriable.github.io)
