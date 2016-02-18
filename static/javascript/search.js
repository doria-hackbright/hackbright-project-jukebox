$(function() {

    // Start WebSockets
    var socket = new WebSocket("ws://" + document.domain + ":5000/websocket/");

    socket.onopen = function () {
      // Get Jukebox id
      $.get("/jukebox_id", function (data) {
        socket.send('{"jukebox_id" : ' + '"' + data + '" ,' +
                    '"first_load" : ' + '"yes"' + '}');
      });
      console.log("Socket Opened");
    };

    socket.onmessage = function(evt) {
    console.log(evt);

    var song_obj = JSON.parse(evt['data']);

    // If data contains song, renders new row to sockets.
    if (song_obj['song_name'] !== undefined) {
      playlist_row = "<tr>" +
                     "<td>" + song_obj['song_name'] + "</td>" +
                     "<td>" + song_obj['song_artist'] + "</td>" +
                     "<td>" + song_obj['song_album'] + "</td>" +
                     "<td>" + song_obj['song_votes'] + "</td>" +
                     "</tr>";

      $('#playlist-display').append(playlist_row);
      
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

          console.log(data);

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
