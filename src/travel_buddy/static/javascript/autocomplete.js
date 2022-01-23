function initMap() {
    const map = new google.maps.Map(document.getElementById("map"), {
      center: { lat: 50.7184, lng: 3.5339 },
      zoom: 13,
      mapTypeControl: false,
    });
    const input1 = document.getElementById("input-1");
    const input2 = document.getElementById("input-2");
    const options = {
      fields: ["formatted_address", "geometry", "name"],
      strictBounds: false,
      types: ["establishment"],
    };
  
    const autocomplete1 = new google.maps.places.Autocomplete(input1, options);
    const autocomplete2 = new google.maps.places.Autocomplete(input2, options);
  
    autocomplete1.bindTo("bounds", map);
    autocomplete2.bindTo("bounds", map);
  
    const infowindow = new google.maps.InfoWindow();
    const infowindowContent = document.getElementById("infowindow-content");
  
    infowindow.setContent(infowindowContent);
  
    const marker = new google.maps.Marker({
      map,
      anchorPoint: new google.maps.Point(0, -29),
    });
  
    autocomplete1.addListener("place_changed", () => {
      infowindow.close();
      marker.setVisible(false);
  
      const place = autocomplete1.getPlace();
  
      if (!place.geometry || !place.geometry.location) {
        window.alert("No details available for input: '" + place.name + "'");
        return;
      }
  
      // If the place has a geometry, then present it on a map.
      if (place.geometry.viewport) {
        map.fitBounds(place.geometry.viewport);
      } else {
        map.setCenter(place.geometry.location);
        map.setZoom(17);
      }
  
      marker.setPosition(place.geometry.location);
      marker.setVisible(true);
      infowindowContent.children["place-name"].textContent = place.name;
      infowindowContent.children["place-address"].textContent =
        place.formatted_address;
      infowindow.open(map, marker);
    });

    autocomplete2.addListener("place_changed", () => {
      infowindow.close();
      marker.setVisible(false);
  
      const place = autocomplete2.getPlace();
  
      if (!place.geometry || !place.geometry.location) {
        // User entered the name of a Place that was not suggested and
        // pressed the Enter key, or the Place Details request failed.
        window.alert("No details available for input: '" + place.name + "'");
        return;
      }
  
      // If the place has a geometry, then present it on a map.
      if (place.geometry.viewport) {
        map.fitBounds(place.geometry.viewport);
      } else {
        map.setCenter(place.geometry.location);
        map.setZoom(17);
      }
  
      marker.setPosition(place.geometry.location);
      marker.setVisible(true);
      infowindowContent.children["place-name"].textContent = place.name;
      infowindowContent.children["place-address"].textContent =
        place.formatted_address;
      infowindow.open(map, marker);
    });
  
    autocomplete1.bindTo("bounds", map);
    autocomplete2.bindTo("bounds", map);
  }