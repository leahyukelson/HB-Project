// Night Out Javascript

// ~~~~~~~~~~~~~~~ Profile Page ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

$(".decline_plan_btn").click(decline_plan);

function decline_plan() {
    var decline_url;

    // Use value of URL button to send request to the route to decline a plan
    if (confirm("Are you sure you would no longer like to attend this plan?") == true) {
      decline_url = this.value;
      $.post(decline_url, {});
      alert("This plan is no longer in your profile");
    }
}

    // Make Line Chart of event frequency by month
    var ctx_line = $("#lineChart").get(0).getContext("2d");

    // Options for Chart JS
    var options = {
          responsive: true
        };

    // AJAX call to request user data for line chart
    $.get("/event-frequency.json", function (data) {
          var myLineChart = Chart.Line(ctx_line, {
                                        data: data,
                                        options: options
                                    });
    });


// ~~~~~~~~~~~~~~~ Add/ Edit Plan ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

// Bias the autocomplete object to the user's geographical location,
// as supplied by the browser's 'navigator.geolocation' object.
function geolocate() {
  if (navigator.geolocation) {
    navigator.geolocation.getCurrentPosition(function(position) {
      var geolocation = {
        lat: position.coords.latitude,
        lng: position.coords.longitude
      };
      var circle = new google.maps.Circle({
        center: geolocation,
        radius: position.coords.accuracy
      });
      autocomplete.setBounds(circle.getBounds());
    });
  }
}

// ~~~~~~~~~~~~~~~ Upcoming Plans ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

// Creates Google map for upcoming plan using events coordinates as the center
function initMap() {

      var plan_id = $("#first-plan").children(".plan-id").html();
      var event_name = $("#first-plan").children(".event-name").html();
      var event_latitude = parseFloat($("#first-plan").children(".event-latitude").html());
      var event_longitude = parseFloat($("#first-plan").children(".event-longitude").html());
      var food_name = $("#first-plan").children(".food-name").html();
      var food_latitude = parseFloat($("#first-plan").children(".food-latitude").html());
      var food_longitude = parseFloat($("#first-plan").children(".food-longitude").html());
      var eventltLng = {lat: event_latitude, lng: event_longitude};
      var foodltLng = {lat: food_latitude, lng: food_longitude};
      var event_image = '/static/calendar.png'
      var food_image = '/static/fork.png'
      
      var map = new google.maps.Map(document.getElementById("plan-map"), {
        zoom: 14,
        center: eventltLng,
        gestureHandling: 'cooperative',
        mapTypeControl: false,
        streetViewControl: false
      });

      var eventMarker = new google.maps.Marker({
        position: eventltLng,
        map: map,
        title: event_name,
        icon: event_image
      });

      if (food_name != "") {
        var foodMarker = new google.maps.Marker({
          position: foodltLng,
          map: map,
          title: food_name,
          icon: food_image
        });
      }
}