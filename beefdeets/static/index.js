(function() {
  var ajax = function(method, url, success, error) {
    var request = new XMLHttpRequest();
    request.open(method, url, true);

    request.onload = function() {
      if (request.status >= 200 && request.status < 400) {
        if (success) {
          success(JSON.parse(request.responseText));
        }
      } else if (error) {
        error(request);
      }
    };

    request.send();
  };

  var set_cover = function() {
    // Add cache-breaker to URL to force a redownload
    album_cover.src = "/player/album_cover.jpg?" + new Date().getTime();
  };

  var set_title = function(attrs) {
    var new_title = attrs["album"] + " - \"" + attrs["title"] + "\" by " + attrs["artist"];

    if (now_playing.textContent != new_title) {
      set_cover();
    }

    now_playing.textContent = new_title;
  };

  var timestamp_seconds = function(timestamp) {
    var matches = /^(?:(?<hours>\d+):)?(?<minutes>\d+):(?<seconds>\d+)$/.
      exec(timestamp);

    if (matches) {
      var groups = matches.groups;
      if (!groups.hours) {
        groups.hours = "0";
      }

      return parseInt(groups.hours) * 3600 +
        parseInt(groups.minutes) * 60 +
        parseInt(groups.seconds);
    }
  };

  var set_progress = function(attrs) {
    var percent = timestamp_seconds(attrs.playback_pos) / timestamp_seconds(attrs.length) * 100;
    progress_bar.textContent = "(" + attrs["playback_pos"] + " / " + attrs["length"] + ")";
    progress_bar.style.width = percent + "%"
  };

  var set_all = function(data) {
    set_progress(data);
    set_title(data);
  };

  // JSON API functions
  var API = {
    now_playing: function(success, error) {
      ajax("GET", "/player/now_playing.json", success, error);
    },
    previous: function(success, error) {
      ajax("PATCH", "/player/prev.json", success, error);
    },
    next: function(success, error) {
      ajax("PATCH", "/player/next.json", success, error);
    },
    play_pause: function(success, error) {
      ajax("PATCH", "/player/play_pause.json", success, error);
    }
  };

  var now_playing = document.getElementById("now-playing");
  var progress_bar = document.getElementById("progress");
  var album_cover = document.getElementById("cover");

  document.getElementById("prev-button").onclick = function() { API.previous() };
  document.getElementById("play-button").onclick = function() { API.play_pause() };
  document.getElementById("next-button").onclick = function() { API.next() };

  setInterval(function() {
    API.now_playing(set_all);
  }, 1000);
})();
