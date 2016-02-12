// Admin View Specific Javascript

$(function() {

    // Ensures that the proper public URL is provided
    $("#public-url").text(window.location.href.slice(0,-6));

    // Set the action to the proper url
    $("#delete-jukebox").attr("action", "/jukebox/" +
    window.location.href.slice(-42, -6) + "/delete");

});

