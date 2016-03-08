$(function() {

  // Guest creation
  // NOTE: Guest creation must occur before the WebSocket setup because
  // AJAX requests async and get request will resolve async from post
  jukeboxData = "jukebox_id=" + window.location.href.slice(-36);

  $.post('/guest', jukeboxData, function() {
    console.log("I made a new user!");
  });

  // Playlist socket setup
  var playlistSocket = new WebSocket("ws://" + document.domain + ":5000/playlist_socket/");

  // WebSocket on-open
  playlistSocket.onopen = function() {
    
    // Render current playlist for the jukebox
    $.get("/jukebox_id", function (data) {
      console.log(data);

      playlistSocket.send('{"jukebox_id" : ' + '"' + data['jukebox_id'] + '" ,' +
                          '"first_load" : ' + '"yes"' + '}');
      });
  
    console.log("Socket Opened");
  
  };

  // WebSocket on-message 
  playlistSocket.onmessage = function(evt) {

    // Parse data from server for song object
    var songObj = JSON.parse(evt['data']);

    // When something is loaded for the first time
    if (songObj['first_load']) {
      playlistRow = "<tr id=" + "'" + songObj['song_user_id'] + "'" + ">" +
                     "<td class='song-name'>" + songObj['song_name'] + "</td>" +
                     "<td class='song-artist'>" + songObj['song_artist'] + "</td>" +
                     "<td class='song-album'>" + songObj['song_album'] + "</td>" +
                     "<td>" + "<form class='vote'><input type='hidden' name='vote-value' value='1'>" +
                     "<input type='hidden' name='guest-id' value=" + "'" + songObj['guest_id'] + "'" + ">" +
                     "<input type='hidden' name='song-user-relation' value=" + "'" + songObj['song_user_id'] + "'" + ">" +
                     "<button><input type='submit' value='upvote' style='display:none;'><i class='fa fa-thumbs-o-up'></i></button></form>" +
                     "<td>" + "<form class='vote'><input type='hidden' name='vote-value' value='-1'>" +
                     "<input type='hidden' name='guest-id' value=" + "'" + songObj['guest_id'] + "'" + ">" +
                     "<input type='hidden' name='song-user-relation' value=" + "'" + songObj['song_user_id'] + "'" + ">" +
                     "<button><input type='submit' value='downvote' style='display:none;'><i class='fa fa-thumbs-o-down'></i></button></form>";

      $('#playlist-display').append(playlistRow);

      // Setting up voting event listener
      $('.vote').submit(function (evt) {
        evt.preventDefault();
        var formData = $(this).serialize();

        // Need to first get jukebox_id and guest_id
        $.get('/guest_id', function (data) {

          var voteRoute = "/jukebox/" + data['jukebox_id'] + "/vote";
          formData += "&voter-id=" + data['guest_id'];
          console.log(formData);

          // Then use the jukebox_id and guest_id to make a post request to vote route
          $.post(voteRoute, formData, function (data) {
            
            $('#vote-flash').text(data['message']).fadeIn();
            
            setTimeout(function() {
              $('#vote-flash').fadeOut();
            }, 2500);

            playlistSocket.send(JSON.stringify(data));
          });
        });
      });
    }

    // When a playlist is rerendered because a new song is added
    if (songObj['new_song']) {

      if (songObj['order'] === 0) {
        $('#playlist-display').empty();
      }

      playlistRow = "<tr id=" + "'" + songObj['song_user_id'] + "'" + ">" +
                     "<td class='song-name'>" + songObj['song_name'] + "</td>" +
                     "<td class='song-artist'>" + songObj['song_artist'] + "</td>" +
                     "<td class='song-album'>" + songObj['song_album'] + "</td>" +
                     "<td>" + "<form class='vote'><input type='hidden' name='vote-value' value='1'>" +
                     "<input type='hidden' name='guest-id' value=" + "'" + songObj['guest_id'] + "'" + ">" +
                     "<input type='hidden' name='song-user-relation' value=" + "'" + songObj['song_user_id'] + "'" + ">" +
                     "<input type='submit' value='upvote'></form>" +
                     "<td>" + "<form class='vote'><input type='hidden' name='vote-value' value='-1'>" +
                     "<input type='hidden' name='guest-id' value=" + "'" + songObj['guest_id'] + "'" + ">" +
                     "<input type='hidden' name='song-user-relation' value=" + "'" + songObj['song_user_id'] + "'" + ">" +
                     "<input type='submit' value='downvote'></form>";

      $('#playlist-display').append(playlistRow);

      // Setting up voting event listener
      $('.vote').submit(function (evt) {
        evt.preventDefault();
        var formData = $(this).serialize();

        // Need to first get jukebox_id and guest_id
        $.get('/guest_id', function (data) {

          var voteRoute = "/jukebox/" + data['jukebox_id'] + "/vote";
          formData += "&voter-id=" + data['guest_id'];
          console.log(formData);

          // Then use the jukebox_id and guest_id to make a post request to vote route
          $.post(voteRoute, formData, function (data) {
            
            $('#vote-flash').text(data['message']).fadeIn();
            
            setTimeout(function() {
              $('#vote-flash').fadeOut();
            }, 2500);

            playlistSocket.send(JSON.stringify(data));
          });
        });
      });
    }

    // When a playlist is rerendered based on vote update
    if (songObj['vote_update']){
      
      if (songObj['order'] === 0) {
        $('#playlist-display').empty();
      }

      playlistRow = "<tr id=" + "'" + songObj['song_user_id'] + "'" + ">" +
               "<td class='song-name'>" + songObj['song_name'] + "</td>" +
               "<td class='song-artist'>" + songObj['song_artist'] + "</td>" +
               "<td class='song-album'>" + songObj['song_album'] + "</td>" +
               "<td>" + "<form class='vote'><input type='hidden' name='vote-value' value='1'>" +
               "<input type='hidden' name='guest-id' value=" + "'" + songObj['guest_id'] + "'" + ">" +
               "<input type='hidden' name='song-user-relation' value=" + "'" + songObj['song_user_id'] + "'" + ">" +
               "<input type='submit' value='upvote'></form>" +
               "<td>" + "<form class='vote'><input type='hidden' name='vote-value' value='-1'>" +
               "<input type='hidden' name='guest-id' value=" + "'" + songObj['guest_id'] + "'" + ">" +
               "<input type='hidden' name='song-user-relation' value=" + "'" + songObj['song_user_id'] + "'" + ">" +
               "<input type='submit' value='downvote'></form>";

      $('#playlist-display').append(playlistRow);

      // Setting up voting event listener
      $('.vote').submit(function (evt) {
        evt.preventDefault();

        var formData = $(this).serialize();
        console.log(formData);

        // Need to first get jukebox_id and guest_id
        $.get('/guest_id', function (data) {

          var voteRoute = "/jukebox/" + data['jukebox_id'] + "/vote";
          formData += "&voter-id=" + data['guest_id'];
          console.log(formData);

          // Then use the jukebox_id and guest_id to make a post request to vote route
          $.post(voteRoute, formData, function (data) {
            
            console.log(data);
            $('#vote-flash').text(data['message']).fadeIn();
            
            setTimeout(function() {
              $('#vote-flash').fadeOut();
            }, 2500);

            console.log(JSON.stringify(data));
            playlistSocket.send(JSON.stringify(data));

          });
        });
      });
    }

    // Re-rendering based on playing a song
    if (songObj['play']) {
      console.log(songObj);
      
      if (songObj['order'] === 0) {
        $('#playlist-display').empty();
      }

      playlistRow = "<tr id=" + "'" + songObj['song_user_id'] + "'" + ">" +
               "<td class='song-name'>" + songObj['song_name'] + "</td>" +
               "<td class='song-artist'>" + songObj['song_artist'] + "</td>" +
               "<td class='song-album'>" + songObj['song_album'] + "</td>" +
               "<td>" + "<form class='vote'><input type='hidden' name='vote-value' value='1'>" +
               "<input type='hidden' name='guest-id' value=" + "'" + songObj['guest_id'] + "'" + ">" +
               "<input type='hidden' name='song-user-relation' value=" + "'" + songObj['song_user_id'] + "'" + ">" +
               "<input type='submit' value='upvote'></form>" +
               "<td>" + "<form class='vote'><input type='hidden' name='vote-value' value='-1'>" +
               "<input type='hidden' name='guest-id' value=" + "'" + songObj['guest_id'] + "'" + ">" +
               "<input type='hidden' name='song-user-relation' value=" + "'" + songObj['song_user_id'] + "'" + ">" +
               "<input type='submit' value='downvote'></form>";

      $('#playlist-display').append(playlistRow);

      // Setting up voting event listener
      $('.vote').submit(function (evt) {
        evt.preventDefault();

        var formData = $(this).serialize();
        console.log(formData);

        // Need to first get jukebox_id and guest_id
        $.get('/guest_id', function (data) {

          var voteRoute = "/jukebox/" + data['jukebox_id'] + "/vote";
          formData += "&voter-id=" + data['guest_id'];
          console.log(formData);

          // Then use the jukebox_id and guest_id to make a post request to vote route
          $.post(voteRoute, formData, function (data) {
            
            console.log(data);
            $('#vote-flash').text(data['message']).fadeIn();
            
            setTimeout(function() {
              $('#vote-flash').fadeOut();
            }, 2500);

            playlistSocket.send(JSON.stringify(data));

          });
        });
      });
    }

    // Empty playlist render
    if (songObj['empty_playlist']) {
      $('#playlist-display').empty();
    }
  };

  // Player socket setup
  var playerSocket = new WebSocket("ws://" + document.domain + ":5000/player_socket/");

  playerSocket.onopen = function() {
    console.log("HURRAH");
  };

  // Search toggling
  $("#search-toggle").click(function() {
      $("#search-form").slideToggle(750);
  });

  // Search request
  $("#search-form").submit(function (evt){
    evt.preventDefault();

    $.get("/search", {'search-term': $('#search-term').val()}, function(data) {

      $("#search-results").slideDown(250);

      if (data['tracks']['items'].length > 0) {
      
      var searchResults = "";
        
      for (var i = 0; i < data['tracks']['items'].length; i++) {
              
        var songName = data['tracks']['items'][i]['name'],
            artist = data['tracks']['items'][i]['artists'][0]['name'],
            album = data['tracks']['items'][i]['album']['name'],
            uri = data['tracks']['items'][i]['uri'];

        searchResults += "<div><strong>Song Name:</strong> " + songName +
                          ", <strong>Artist:</strong> " + artist +
                          "<form action='/song/add' method='post' class='add-song'>" +
                          "<input type='hidden' name='song-name' value=" +
                          "'" + songName + "'>" +
                          "<input type='hidden' name='song-artist' value=" +
                          "'" + artist + "'>" +
                          "<input type='hidden' name='song-album' value=" +
                          "'" + album + "'>" +
                          "<input type='hidden' name='song-uri' value=" +
                          "'" + uri + "'>" +
                          "<input type='submit' value='Add to playlist'></form></div>";
      }

      $("#search-results").html(searchResults);

      // Adding new songs - event listener
      $('.add-song').submit(function (evt) {
        evt.preventDefault();
        formData = $(this).serialize();

        $.post('/song/add', formData, function (data) {

            $('#search-flash').text(data['song_name'] + " has been added.").fadeIn();
            
            setTimeout(function() {
              $('#search-flash').fadeOut();
            }, 2500);

          playlistSocket.send(JSON.stringify(data));
 
        });
      });
    } else { $('#search-results').text("There are no results, sorry!"); }
    });
  });
});
