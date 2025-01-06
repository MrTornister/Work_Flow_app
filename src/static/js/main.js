// main.js
document.addEventListener('DOMContentLoaded', function() {
    // Your JavaScript code goes here
    console.log('JavaScript is loaded and ready to go!');
    
    // Example: Add a click event to a button
    const button = document.getElementById('myButton');
    if (button) {
        button.addEventListener('click', function() {
            alert('Button clicked!');
        });
    }
});