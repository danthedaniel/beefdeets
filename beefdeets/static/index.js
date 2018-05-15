(function() {
  var ajax = function(method, url, success, error) {
    var request = new XMLHttpRequest();
    request.open(method, url, true);

    request.onload = function() {
      if (request.status >= 200 && request.status < 400) {
        success(JSON.parse(request.responseText));
      } else {
        error(request);
      }
    };

    request.send();
  };

  var format_playing = function(attrs) {
    return (
      attrs["album"] + " - \"" + attrs["title"] + "\" by " + attrs["artist"] +
      " (" + attrs["playback_pos"] + "/" + attrs["length"] + ")"
    );
  };

  // JSON API functions
  var API = {
    now_playing: function(success, error) {
      ajax("GET", "/player/now_playing.json", success, error);
    }
  };

  var request_delay = 1000; // 30 seconds
  var now_playing = document.getElementById("now-playing");

  setInterval(function() {
    API.now_playing(function(data) {
      now_playing.textContent = format_playing(data);
    });
  }, request_delay);
})();
