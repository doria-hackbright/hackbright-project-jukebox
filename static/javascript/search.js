$(function() {
  
  // Using WebSockets
  // var socket = new WebSocket("ws://" + document.domain + ":5000/websocket/");

  // socket.onopen = function() {
  //   socket.send("Socket Connected");
  // }

  // socket.onupdate = function(playlist) {
    // Render playlist
  // }

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
                  uri = data['tracks']['items'][i]['uri'];


              search_results += "<div><strong>Song Name:</strong> " + song_name +
                                ", <strong>Artist:</strong> " + artist +
                                "<form action='/song/add' method='post' class='add-song'>" +
                                "<input type='hidden' name='song-name' value=" +
                                "'" + song_name + "'" +
                                "><input type='hidden' name='song-uri' value=" +
                                "'" + uri + "'" +
                                "><input type='submit' value='Add to playlist'></form></div>";

              console.log(search_results);
              console.log("whee");
          }

          $("#search-results").html(search_results);

          // Adding new songs - event listener
          $('.add-song').submit(function (evt) {
            evt.preventDefault();

            formData = $(this).serialize();

            $.post('/song/add', formData, function (data) {
                
                console.log(data);
                $('#search-flash').text(data).fadeIn();
                
                setTimeout(function() {
                  $('#search-flash').fadeOut();
                }, 2500);

            var playlist_route = window.location.href.slice(0,-6) + "/playlist";

            $.post(playlist_route, function (data) {
              
              console.log("Rendering a playlist.");

              // Receive JSON data back

              // Parse and populate the table

              // Remove Jinja template

            });
              
              });
          });
      });
  });
});
