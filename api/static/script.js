//check autoscroll
// check download button style
// checl table style- max width
// explore max height

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
  scrollToBottom();
}
function addLoadingMessage() {
  const messageContainer = document.createElement("div");
  messageContainer.classList.add("message-container");
  messageContainer.classList.add("bot");

  const loadingMessage = document.createElement("div");

  let dots = 0;
  const intervalId = setInterval(() => {
    loadingMessage.textContent =
      "Please wait while I search for your data" + ".".repeat(dots);
    dots = (dots + 1) % 4;
  }, 500);
  loadingMessage.classList.add("message-bubble");
  loadingMessage.classList.add("loading-message");
  messageContainer.appendChild(loadingMessage);

  const chatbox = document.getElementById("response");
  chatbox.appendChild(messageContainer);
  // chatbox.scrollTop = chatbox.scrollHeight;

  // Save the interval ID so that we can stop the interval later
  messageContainer.dataset.intervalId = intervalId;
}
// add a download button like a bot message clicking which goes to the /download endpoint
function addDownloadbutton() {
  const messageContainer = document.createElement("div");
  messageContainer.classList.add("message-container");
  messageContainer.classList.add("user");

  const downloadButton = document.createElement("button");
  downloadButton.classList.add("button");
  downloadButton.classList.add("download-button");
  downloadButton.textContent = "Download";

  downloadButton.addEventListener("click", function () {
    fetch("/download")
      .then((response) => response.blob())
      .then((blob) => {
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement("a");
        a.style.display = "none";
        a.href = url;
        a.download = "data.xlsx";
        document.body.appendChild(a);
        a.click();
        window.URL.revokeObjectURL(url);
      });
  });

  messageContainer.appendChild(downloadButton);

  const chatbox = document.getElementById("response");
  chatbox.appendChild(messageContainer);
  chatbox.scrollTop = chatbox.scrollHeight;
}
// function to scroll to bottom of the chat window
function scrollToBottom() {
  const chatbox = document.getElementById("response-wrapper");
  //scroll to bottom
  // chatbox.scrollTop = chatbox.scrollHeight;
}
//WHEN DOWNLOAD BUTTON IS CLICKEd IT SHOULD GO TO THE /DOWNLOAD ENDPOINT
//function for response handler

// Function to add bot message to the chat window
function addBotMessage(response, type) {
  // Stop the loading message interval if it exists
  const loadingMessage = document.querySelector(".loading-message");
  if (loadingMessage) {
    const intervalId = loadingMessage.parentNode.dataset.intervalId;
    clearInterval(intervalId);
  }
  if (type != "preview") {
    addMessage(message, "bot");
  } else {
    addBotMessage("Data Search Completed!", "bot");
    // addMessage("Here is a preview of the data", "bot");
    addMessage(
      "I found " +
        response.num_rows +
        " rows Total, this is a preview of the Data: ",
      "bot"
    );
    addtablemessage(response.response);
    addDownloadbutton();
  }
}
function killLoadingmessage() {
  const loadingMessage = document.querySelector(".loading-message");
  if (loadingMessage) {
    const intervalId = loadingMessage.parentNode.dataset.intervalId;
    clearInterval(intervalId);
  }
}
function addPreviewmessage(response) {
  // Stop the loading message interval if it exists
  killLoadingmessage();

  // addMessage("Here is a preview of the data", "bot");
  addMessage(
    "I found " +
      response.num_rows +
      " rows Total, this is a preview of the Data: ",
    "bot"
  );
  addtablemessage(response.preview);
  addDownloadbutton();
}
function addtablemessage(response) {
  const messageContainer = document.createElement("div");
  messageContainer.classList.add("message-container");
  messageContainer.classList.add("bot");

  const table = document.createElement("table");
  table.classList.add("data-table");
  table.innerHTML = response;

  messageContainer.appendChild(table);

  const chatbox = document.getElementById("response");
  chatbox.appendChild(messageContainer);
  chatbox.scrollTop = chatbox.scrollHeight;
}
window.onload = function () {
  addMessage("What kind of data are you looking for?", "bot");
};

// Function to handle form submission
function handleUserInput(event) {
  event.preventDefault();
  const userInput = document.getElementById("query");
  const userMessage = userInput.value;
  addMessage(userMessage, "user");

  // Add loading message
  addLoadingMessage();

  // Send POST request to backend
  fetch("/scrape", {
    method: "POST",
    body: JSON.stringify({ message: userMessage }),
    headers: {
      "Content-Type": "application/json",
    },
  })
    .then((response) => response.json())
    .then((data) => {
      // Add bot message with response from backend
      // if data has type preview then add preview message
      addMessage("Data Search Completed!", "bot");
      //check length of the response array

      if (data.response && data.response.length > 0) {
        data.response.forEach((responseData) => {
          if (responseData.type == "preview") {
            killLoadingmessage();
            addPreviewmessage(responseData, "preview");
          }
          if (responseData.type == "error") {
            //send message to user that there was an error
            killLoadingmessage();
            addMessage(responseData.message, "bot");
          }
        });
      }
    })
    .catch((error) => {
      console.error("Error:", error);
    });

  // Clear input field
  userInput.value = "";
}

// Add event listener to form submission
const searchForm = document.getElementById("search-form");
searchForm.addEventListener("submit", handleUserInput);
