// Get the modal
var modal = document.getElementById("myModal");

// Get the button that opens the modal
var btn = document.getElementById("submit-button");

// Get the <span> element that closes the modal
var span = document.getElementsByClassName("close")[0];

// When the user clicks the button, open the modal
btn.onclick = function() {
  modal.style.display = "block";
}

// When the user clicks on <span> (x), close the modal
span.onclick = function() {
  modal.style.display = "none";
}

// When the user clicks anywhere outside of the modal, close it
window.onclick = function(event) {
  if (event.target == modal) {
    modal.style.display = "none";
  }
}

// Add event listener to confirm-yes button
document.getElementById("confirm-yes").addEventListener("click", function() {
    document.getElementById("course-form").submit();
});

// Add event listener to confirm-no button
document.getElementById("confirm-no").addEventListener("click", function() {
    modal.style.display = "none";
});

// Function to go back to the previous page
function goBack() {
    window.history.back();
}
