document.getElementById("my-form").addEventListener("submit", function (e) {
  e.preventDefault(); // prevent the form from submitting normally

  // show the loading screen
  document.getElementById("original-content").style.display = "none";
  document.getElementById("loading-screen").style.display = "block";
  var url = e.target.action; // get the form's action attribute
  var formData = new FormData(e.target); // get the form data

  // submit the form data using fetch
  fetch(url, {
    method: "POST",
    body: formData,
  })
    .then((response) => {
      if (!response.ok) {
        throw new Error("Network response was not ok");
      }
      return response.json();
    })
    .then((data) => {
      console.log(data); // Add this line
      // When the data is ready, redirect to the new page
      window.location.href = data.redirect_url;
    })
    .catch((error) => {
      // handle any errors
      console.error("Error:", error);

      // hide the loading screen
      document.getElementById("loading-screen").style.display = "none";
    });
});
