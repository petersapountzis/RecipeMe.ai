document.getElementById("my-form").addEventListener("submit", function (e) {
  console.log("Form submitted");
  e.preventDefault(); // prevent the form from submitting normally

  // show the loading screen
  document.getElementById("original-content").style.display = "none";
  document.getElementById("loading-screen").style.display = "block";
  var url = e.target.action; // get the form's action attribute
  var formData = new FormData(e.target); // get the form data

  console.log("Submitting form..."); // Add this line

  // submit the form data using fetch
  console.log("About to fetch...");

  fetch(url, {
    method: "POST",
    body: formData,
  })
    .then((response) => {
      console.log("Response received"); // Add this line
      if (!response.ok) {
        throw new Error("Network response was not ok");
      }
      return response.json();
    })
    .then((data) => {
      console.log(data);
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
