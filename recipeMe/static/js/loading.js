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
    body: formData
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

// document
//   .getElementById("regenerate-button")
//   .addEventListener("click", function (e) {
//     e.preventDefault(); // prevent the default click action

//     // Show the loading screen
//     document.getElementById("original-content").style.display = "none";
//     document.getElementById("loading-screen").style.display = "block";

//     var url = "/regenerate"; // Endpoint URL to trigger the regeneration process

//     // Trigger the regenerate action using fetch
//     fetch(url, {
//       method: "POST" // Use POST since that's the method defined for the /regenerate endpoint
//     })
//       .then((response) => response.json()) // Parse the JSON response
//       .then((data) => {
//         console.log(data);
//         if (data.success) {
//           // Redirect to the provided URL (which will be /recipe in this case)
//           window.location.href = data.redirect_url;
//         } else {
//           // Handle the error, show an alert, and hide the loading screen
//           console.error("Error:", data.message);
//           alert(data.message);
//           document.getElementById("loading-screen").style.display = "none";
//           document.getElementById("original-content").style.display = "block";
//         }
//       })
//       .catch((error) => {
//         // handle any other errors
//         console.error("Error:", error);
//         document.getElementById("loading-screen").style.display = "none";
//         document.getElementById("original-content").style.display = "block";
//         alert("An error occurred. Please try again.");
//       });
//   });
