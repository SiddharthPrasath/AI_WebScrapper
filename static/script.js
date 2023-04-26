// Function to add a message to the chat window
function addMessage(message, sender) {
  const messageContainer = document.createElement("div");
  messageContainer.classList.add("message-container");
  messageContainer.classList.add(sender);

  const messageBubble = document.createElement("div");
  messageBubble.classList.add("message-bubble");
  messageBubble.textContent = message;

  messageContainer.appendChild(messageBubble);

  const chatbox = document.getElementById("response");
  chatbox.appendChild(messageContainer);
  chatbox.scrollTop = chatbox.scrollHeight;
}

// Function to add bot message to the chat window
function addBotMessage(message) {
  addMessage(message, "bot");
}

// Function to handle user input
function handleUserInput(event) {
  event.preventDefault();
  const userInput = document.getElementById("query").value;
  addMessage(userInput, "user");

  // Make an AJAX request to call the Flask backend
  fetch("/update", {
    method: "POST",
    body: JSON.stringify({ query: userInput }),
    headers: {
      "Content-Type": "application/json",
    },
  }).then((response) => {
    const output = document.getElementById("output");
    const source = new EventSource("/update");
    source.onmessage = (event) => {
      output.innerHTML += event.data + "<br>";
    };
  });
}

window.onload = function () {
  addBotMessage("What kind of data are you looking for?");
};

// Add event listener to form submission
const searchForm = document.getElementById("search-form");
searchForm.addEventListener("submit", handleUserInput);

// function displayFlashMessages() {
//   var flashMessages = document.getElementById("flash-messages");
//   fetch("/get_flashed_messages")
//     .then(function (response) {
//       return response.text();
//     })
//     .then(function (html) {
//       flashMessages.innerHTML = html;
//     });
// }
