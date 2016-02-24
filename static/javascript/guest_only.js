$(function() {

  // Guest creation
  // NOTE: Guest creation must occur before the WebSocket setup because
  // AJAX requests async and get request will resolve async from post
  jukebox_data = "jukebox_id=" + window.location.href.slice(-36);

  $.post('/guest', jukebox_data, function() {
    console.log("I made a new user!");
  });

  // WebSocket setup
  var socket = new WebSocket("ws://" + document.domain + ":5000/websocket/");

  // WebSocket on-open
  socket.onopen = function () {
    
    // Render current playlist for the jukebox
    $.get("/jukebox_id", function (data) {
      console.log(data);

      socket.send('{"jukebox_id" : ' + '"' + data['jukebox_id'] + '" ,' +
                    '"first_load" : ' + '"yes"' + '}');
      });
  
    console.log("Socket Opened");
  
  };

  // WebSocket on-message 
  socket.onmessage = function(evt) {

    // Parse data from server for song object
    var song_obj = JSON.parse(evt['data']);
    console.log(song_obj);

    // If data contains song, renders new row in playlist display
    if (song_obj['song_name'] !== undefined && song_obj['vote_update'] === undefined) {
      playlist_row = "<tr id=" + "'" + song_obj['song_user_id'] + "'" + ">" +
                     "<td class='song-name'>" + song_obj['song_name'] + "</td>" +
                     "<td class='song-artist'>" + song_obj['song_artist'] + "</td>" +
                     "<td class='song-album'>" + song_obj['song_album'] + "</td>" +
                     "<td>" + "<form class='vote'><input type='hidden' name='vote-value' value='1'>" +
                     "<input type='hidden' name='guest-id' value=" + "'" + song_obj['guest_id'] + "'" + ">" +
                     "<input type='hidden' name='song-user-relation' value=" + "'" + song_obj['song_user_id'] + "'" + ">" +
                     "<input type='submit' value='upvote'></form>" +
                     "<td>" + "<form class='vote'><input type='hidden' name='vote-value' value='-1'>" +
                     "<input type='hidden' name='guest-id' value=" + "'" + song_obj['guest_id'] + "'" + ">" +
                     "<input type='hidden' name='song-user-relation' value=" + "'" + song_obj['song_user_id'] + "'" + ">" +
                     "<input type='submit' value='downvote'></form>";

      $('#playlist-display').append(playlist_row);

      // Setting up voting event listener
      $('.vote').submit(function (evt) {
        evt.preventDefault();

        var formData = $(this).serialize();
        console.log(formData);

        // Need to first get jukebox_id and guest_id
        $.get('/guest_id', function (data) {

          var vote_route = "/jukebox/" + data['jukebox_id'] + "/vote";
          formData += "&voter-id=" + data['guest_id'];
          console.log(formData);

          // Then use the jukebox_id and guest_id to make a post request to vote route
          $.post(vote_route, formData, function (data) {
            
            console.log(data);
            $('#vote-flash').text(data['message']).fadeIn();
            
            setTimeout(function() {
              $('#vote-flash').fadeOut();
            }, 2500);

            console.log(JSON.stringify(data));
            socket.send(JSON.stringify(data));

          });
        });
      
        // Disable the submit button
        $(this).find('input=[submit]').attr('disabled', 'disabled');

      });
    }

    // Re-rendering playlist on new votes
    if (song_obj['song_name'] !== undefined && song_obj['vote_update'] !== undefined) {
      console.log("VOTE RESET");
      console.log(song_obj);
      console.log("VOTE RESET");
      
      if (song_obj['order'] === 0) {
        $('#playlist-display').empty();
      }

      playlist_row = "<tr id=" + "'" + song_obj['song_user_id'] + "'" + ">" +
               "<td class='song-name'>" + song_obj['song_name'] + "</td>" +
               "<td class='song-artist'>" + song_obj['song_artist'] + "</td>" +
               "<td class='song-album'>" + song_obj['song_album'] + "</td>" +
               "<td>" + "<form class='vote'><input type='hidden' name='vote-value' value='1'>" +
               "<input type='hidden' name='guest-id' value=" + "'" + song_obj['guest_id'] + "'" + ">" +
               "<input type='hidden' name='song-user-relation' value=" + "'" + song_obj['song_user_id'] + "'" + ">" +
               "<input type='submit' value='upvote'></form>" +
               "<td>" + "<form class='vote'><input type='hidden' name='vote-value' value='-1'>" +
               "<input type='hidden' name='guest-id' value=" + "'" + song_obj['guest_id'] + "'" + ">" +
               "<input type='hidden' name='song-user-relation' value=" + "'" + song_obj['song_user_id'] + "'" + ">" +
               "<input type='submit' value='downvote'></form>";

      $('#playlist-display').append(playlist_row);

      // Setting up voting event listener
      $('.vote').submit(function (evt) {
        evt.preventDefault();

        var formData = $(this).serialize();
        console.log(formData);

        // Need to first get jukebox_id and guest_id
        $.get('/guest_id', function (data) {

          var vote_route = "/jukebox/" + data['jukebox_id'] + "/vote";
          formData += "&voter-id=" + data['guest_id'];
          console.log(formData);

          // Then use the jukebox_id and guest_id to make a post request to vote route
          $.post(vote_route, formData, function (data) {
            
            console.log(data);
            $('#vote-flash').text(data['message']).fadeIn();
            
            setTimeout(function() {
              $('#vote-flash').fadeOut();
            }, 2500);

            console.log(JSON.stringify(data));
            socket.send(JSON.stringify(data));

          });
        });
      
        // Disable the submit button
        $(this).find('input=[submit]').attr('disabled', 'disabled');

      });
    }
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

      // TODO: Put a null state if the search doesn't return anything
      console.log(data['tracks']['items']);
      if (data['tracks']['items'].length > 0) {
      
      var search_results = "";
        
      for (var i = 0; i < data['tracks']['items'].length; i++) {
              
        var song_name = data['tracks']['items'][i]['name'],
            artist = data['tracks']['items'][i]['artists'][0]['name'],
            album = data['tracks']['items'][i]['album']['name'],
            uri = data['tracks']['items'][i]['uri'];

        search_results += "<div><strong>Song Name:</strong> " + song_name +
                          ", <strong>Artist:</strong> " + artist +
                          "<form action='/song/add' method='post' class='add-song'>" +
                          "<input type='hidden' name='song-name' value=" +
                          "'" + song_name + "'>" +
                          "<input type='hidden' name='song-artist' value=" +
                          "'" + artist + "'>" +
                          "<input type='hidden' name='song-album' value=" +
                          "'" + album + "'>" +
                          "<input type='hidden' name='song-uri' value=" +
                          "'" + uri + "'>" +
                          "<input type='submit' value='Add to playlist'></form></div>";
      }

      $("#search-results").html(search_results);

      // Adding new songs - event listener
      $('.add-song').submit(function (evt) {
        evt.preventDefault();

        formData = $(this).serialize();

        console.log(formData);

        $.post('/song/add', formData, function (data) {

            console.log(data);
            $('#search-flash').text(data['song_name'] + " has been added.").fadeIn();
            
            setTimeout(function() {
              $('#search-flash').fadeOut();
            }, 2500);

          var playlist_route = window.location.href.slice(0,-6) + "/playlist";

          socket.send(JSON.stringify(data));
 
        });
      });
    } else { $('#search-results').text("There are no results, sorry!"); }
    });
  });
});
