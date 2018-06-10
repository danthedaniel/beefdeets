// IIFE, BABY!
(function() {
  "use strict";
  /**
   * @callback successCallback
   * @param {*} response
   */

  /**
   * @callback errorCallback
   * @param {XMLHttpRequest} xhr
   */

  /**
   * Initiate an XHR.
   * @param {string} method
   * @param {string} url
   * @param {successCallback} success
   * @param {errorCallback} error
   */
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

  /**
   * Set the album cover artwork.
   */
  var set_cover = function() {
    // Add cache-breaker to URL to force a re-download
    album_cover.src = "/player/album_cover.jpg?" + new Date().getTime();
  };

  /**
   * Set the page and display card title.
   *
   * @param {Object} attrs - "Now Playing" parameters.
   */
  var set_title = function(attrs) {
    var new_title = attrs.album + " - \"" + attrs.title + "\" by " + attrs.artist;

    if (now_playing.textContent != new_title) {
      set_cover();
    }

    now_playing.textContent = new_title;
    document.title = new_title;
  };

  /**
   * Get the number of seconds for a timestamp.
   *
   * @param {string} timestamp - String in H:MM:SS or MM:SS format.
   */
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

  /**
   * Set the progress bar size and text.
   *
   * @param {Object} attrs - "Now Playing" parameters.
   */
  var set_progress = function(attrs) {
    var percent = timestamp_seconds(attrs.playback_pos) / timestamp_seconds(attrs.length) * 100;
    // progress_bar.textContent = "(" + attrs.playback_pos + " / " + attrs.length + ")";
    progress_bar.style.width = percent + "%";
  };

  /**
   * Update every element of the application with a new "now_playing" response.
   *
   * @param {Object} attrs - "Now Playing" parameters.
   */
  var set_all = function(attrs) {
    set_progress(attrs);
    set_title(attrs);
  };

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
    play: function(success, error) {
      ajax("PATCH", "/player/play.json", success, error);
    },
    pause: function(success, error) {
      ajax("PATCH", "/player/pause.json", success, error);
    }
  };

  var now_playing = document.getElementById("now-playing");
  var progress_bar = document.getElementById("progress");
  var album_cover = document.getElementById("cover");

  document.getElementById("prev-button").onclick = function() { API.previous() };
  document.getElementById("pause-button").onclick = function() { API.pause() };
  document.getElementById("play-button").onclick = function() { API.play() };
  document.getElementById("next-button").onclick = function() { API.next() };

  setInterval(function() { API.now_playing(set_all) }, 1000);
})();
