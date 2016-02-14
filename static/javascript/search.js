$(function() {

    // Search toggling
    $("#search-toggle").click(function() {
        $("#search-form").slideToggle(750);
    });

    // Search request
    $("#search-form").submit(function (evt){
        evt.preventDefault();

        $.get("/songs", {'search-term': $('#search-term').val()}, function(data) {

            console.log(data);

            $("#search-results").slideDown(750);
            var search_results = "";

            for (var i = 0; i < data['tracks']['items'].length; i++) {
                search_results += "<div><strong>Song Name:</strong> " +
                                  data['tracks']['items'][i]['name'] +
                                  ", <strong>Artist:</strong> " +
                                  data['tracks']['items'][i]['artists'][0]['name'] +
                                  "<form action='/song/add' method='post'>" +
                                  "<input type='hidden' name='song-name' value=" +
                                  data['tracks']['items'][i]['name'] +
                                  "><input type='hidden' name='song-uri' value=" +
                                  data['tracks']['items'][i]['uri'] +
                                  "><input type='submit' value='Add to playlist'></form></div>";
            }

            $("#search-results").html(search_results);
        });
    });
});
