$(function() {

  // WebSocket setup
  var socket = new WebSocket("ws://" + document.domain + ":5000/websocket/");

  // WebSocket on-open
  socket.onopen = function () {
    
    // Get current jukebox playlist
    $.get("/jukebox_id", function (data) {
      console.log(data);
      
      socket.send('{"jukebox_id" : ' + '"' + data + '" ,' +
                  '"first_load" : ' + '"yes"' + '}');
    });

      console.log("Socket Opened");
  };

  // WebSocket on-message
  socket.onmessage = function(evt) {

    // Parse data from server for song object
    var song_obj = JSON.parse(evt['data']);

    // If data contains song, renders new row to sockets.
    if (song_obj['song_name']) {
      playlist_row = "<tr id=" + "'" + song_obj['song_user_id'] + "'" + ">" +
                     "<td class='song-name'>" + song_obj['song_name'] + "</td>" +
                     "<td class='song-artist'>" + song_obj['song_artist'] + "</td>" +
                     "<td class='song-album'>" + song_obj['song_album'] + "</td>" +
                     "<td class='song-votes'>" + song_obj['song_votes'] + "</td>" +
                     "</tr>";

      $('#playlist-display').append(playlist_row);
    }

    console.log(song_obj);
    console.log(song_obj['song_user_id']);

    // Handling vote updates
    if (song_obj['vote_value']) {
      var selector = "#" + String(song_obj['song_user_id']) + " .song-votes";
      var original_vote_value = $(selector).text(),
          new_vote_value = song_obj['vote_value'];
      console.log(original_vote_value);
      console.log(new_vote_value );
      $(selector).text(parseInt(original_vote_value, 10) + parseInt(new_vote_value, 10));
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
    });
  });
});
