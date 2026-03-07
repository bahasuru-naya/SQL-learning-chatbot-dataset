//turn dark mode on default
document.getElementById('dark').checked = true;

// Connect to RASA server
const socket = io("http://localhost:5005");
socket.on('connect', function () {
    console.log("Connected to Socket.io server");
});
socket.on('connect_error', (error) => {
    // Write any connection errors to the console 
    console.error(error);
});

//menu
function menuCheckbox() {
    if (window.innerWidth < 868) {
        document.getElementById('nav-toggle').checked = true;
    }
}
menuCheckbox();

//remove blur
const removeblur = document.getElementById('chatbot');
removeblur.addEventListener("click", () => {
    if (window.innerWidth < 868) {
        document.getElementById('nav-toggle').checked = true;
    }
});

//dark mode
const darkMode = document.getElementById('dark');
darkMode.addEventListener("click", () => {
    if (darkMode.checked) {
        // Define the light mode colors
        const lightModeColors = {
            '--background': '#ffffff',
            '--navbar-dark-primary': '#18283b',
            '--navbar-dark-secondary': '#2c3e50',
            '--navbar-light-primary': '#f5f6fa',
            '--navbar-light-secondary': '#8392a5',
            '--black': '#000000',
            '--white': '#ffffff',
        };

        // Get the root element
        const root = document.documentElement;



        // Change the colors to light mode
        for (let color in lightModeColors) {
            root.style.setProperty(color, lightModeColors[color]);

        }

        // Select the img element
        var imgElement = document.querySelector('#nav-footer-avatar img');

        // Change the src attribute
        imgElement.src = './images/settings-64.png'; // Replace with your new image path
    }
    else {
        // Define the light mode colors
        const darkModeColors = {
            '--background': '#18283b',
            '--navbar-dark-primary': '#f5f6fa',
            '--navbar-dark-secondary': '#8392a5',
            '--navbar-light-primary': '#18283b',
            '--navbar-light-secondary': '#2c3e50',
            '--black': '#ffffff',
            '--white': '#000000',
        };

        // Get the root element
        const root = document.documentElement;


        // Change the colors to light mode
        for (let color in darkModeColors) {
            root.style.setProperty(color, darkModeColors[color]);

        }
        // Select the img element
        var imgElement = document.querySelector('#nav-footer-avatar img');

        // Change the src attribute
        imgElement.src = './images/settings-64 - dark.png'; // Replace with your new image path
    }
});

//slider link
const s1 = document.getElementById('s1');
s1.addEventListener('click', () => {
    let msg1 = "Show all tables";
    socket.emit('user_uttered', { "message": msg1 });
    appendMessage(msg1, "sent");
    wait();
});
const s2 = document.getElementById('s2');
s2.addEventListener('click', () => {
    let msg2 = "show stock";
    socket.emit('user_uttered', { "message": msg2 });
    appendMessage(msg2, "sent");
    wait();
});
const s3 = document.getElementById('s3');
s3.addEventListener('click', () => {
    let msg3 = "add camera and 240 to stock";
    socket.emit('user_uttered', { "message": msg3 });
    appendMessage(msg3, "sent");
    wait();
});
const s4 = document.getElementById('s4');
s4.addEventListener('click', () => {
    let msg4 = "delete camera and 240 from stock";
    socket.emit('user_uttered', { "message": msg4 });
    appendMessage(msg4, "sent");
    wait();
});
const s5 = document.getElementById('s5');
s5.addEventListener('click', () => {
    let msg5 = "show details about sales of each items";
    socket.emit('user_uttered', { "message": msg5 });
    appendMessage(msg5, "sent");
    wait();
});


//text input
const textInput = document.getElementById('text-input');
const form1 = document.getElementById('form');

textInput.addEventListener('focusin', () => {
    form1.style.width = '90%';
});
textInput.addEventListener('focusout', () => {
    form1.style.width = '90%';
});


var isTrue = true;
var checkbox = document.getElementById('voice');

function checkCheckboxState() {

    // Check if checkbox is checked
    if (checkbox.checked) {
        // Print 'true' to console
        isTrue = true;
        console.log(isTrue);
    }
    else {
        isTrue = false;
        console.log(isTrue);
        synth.cancel();
    }
}


// Add event listener to checkbox
checkbox.addEventListener('change', function () {
    checkCheckboxState();
});



const messages = document.getElementById('messages');
const form = document.getElementById('form');
let messageInput = document.getElementById('message-input');


form.addEventListener('submit', function (e) {
    e.preventDefault();
    if (recording) {
        stopRecording();
    }
    const msg = messageInput.value;
    if (msg) {
        socket.emit('user_uttered', { "message": msg });
        messageInput.value = '';

        appendMessage(msg, "sent");
        wait();
        messageInput.placeholder = "Type your command..";
        clearBtn.style.display = "none";
        form1.style.width = '80%';
    }
});

function appendMessage(msg, type) {
    const avatar = document.createElement('img');
    if (type == "received") {
        removeWait();
        avatar.src = "./images/robot.png";
        avatar.classList.add("avatar-r");
    } else {
        avatar.src = "./images/user.png";
        avatar.classList.add("avatar-s");
    }

    avatar.style.width = "40px"; // Set the width
    avatar.style.height = "40px"; // Set the height 

    const pic = document.createElement('div');
    pic.appendChild(avatar);
    pic.classList.add("picture");

    const item = document.createElement('div');
    item.classList.add("message");
    item.classList.add(`message_${type}`);

    const isTableMessage = msg.includes('|');

    if (isTableMessage) {
        const text = document.createElement('div');
        if (type == "received") {
            item.appendChild(pic);
        }
        const parts = msg.trim().split('~');
        parts.forEach(part => {
            const isTable = part.includes('|');
            if (isTable) {
                const table = document.createElement('table');
                const lines = part.trim().split('\n');

                lines.forEach((line, index) => {
                    const row = document.createElement('tr');
                    const cells = line.split('|').filter(cell => cell.trim() !== '');

                    cells.forEach(cell => {
                        const cellElement = document.createElement(index === 0 ? 'th' : 'td'); // First row as <th>
                        cellElement.textContent = cell.trim();
                        row.appendChild(cellElement);
                    });

                    table.appendChild(row);
                });

                table.classList.add(`message_${type}_table`);
                text.appendChild(table);
                text.classList.add(`message_${type}_text`);
                item.appendChild(text);
            }
            else {
                if (part !== "") {

                    const lines = part.split('\n');

                    lines.forEach((line, index) => {
                        const textNode = document.createTextNode(line.trim());
                        text.appendChild(textNode);

                        // Add a <br> element if it's not the last line
                        if (index !== lines.length - 1) {
                            text.appendChild(document.createElement('br'));
                        }
                    });

                    text.classList.add(`message_${type}_text`);
                    item.appendChild(text);
                }
            }
        });
        if (type == "sent") {
            item.appendChild(pic);
        }

    } else {
        const text = document.createElement('div');
        const lines = msg.split('\n');

        lines.forEach((line, index) => {
            const textNode = document.createTextNode(line.trim());
            text.appendChild(textNode);

            // Add a <br> element if it's not the last line
            if (index !== lines.length - 1) {
                text.appendChild(document.createElement('br'));
            }
        });

        text.classList.add(`message_${type}_text`);

        if (type == "received") {
            item.appendChild(pic);
            item.appendChild(text);
        } else {
            item.appendChild(text);
            item.appendChild(pic);
        }
    }

    messages.appendChild(item);
    scrollToBottom();
}



function wait() {
    const avatar = document.createElement('img');
    avatar.src = "./images/robot.png";
    avatar.classList.add("avatar-r");
    avatar.style.width = "40px"; // Set the width
    avatar.style.height = "40px"; // Set the height
    const pic = document.createElement('div');
    pic.appendChild(avatar);
    pic.classList.add("picture");
    const text = document.createElement('div');
    const l1 = document.createElement('div');
    l1.classList.add("typing");
    l1.classList.add("typing-1");
    const l2 = document.createElement('div');
    l2.classList.add("typing");
    l2.classList.add("typing-2");
    const l3 = document.createElement('div');
    l3.classList.add("typing");
    l3.classList.add("typing-3");
    text.appendChild(l1);
    text.appendChild(l2);
    text.appendChild(l3);
    const item = document.createElement('div');
    item.id = "wait";
    item.classList.add("message");
    item.classList.add(`message_received`);
    text.classList.add(`message_received_text`);
    item.appendChild(pic);
    item.appendChild(text);
    messages.appendChild(item);
    scrollToBottom();
}

function removeWait() {
    const item = document.getElementById('wait');
    item.remove();
}

function scrollToBottom() {
    var element = document.getElementById("messages");
    element.scrollTo({
        top: element.scrollHeight,
        behavior: 'smooth' // Add smooth behavior
    });
}

socket.on('bot_uttered', function (response) {
    console.log("Bot uttered:", response);
    if (response.text) {

        appendMessage(response.text, "received");
    }
    if (response.attachment) {
        appendImage(response.attachment.payload.src, "received");
    }
    if (response.quick_replies) {
        appendQuickReplies(response.quick_replies);
    }

    checkCheckboxState();
    if (isTrue == true) {
        if (response.text !== "") {
            if (!synth.speaking) {
                textToSpeech(response.text);

            }
            if (response.text.length > 80) {
                setInterval(() => {
                    if (!synth.speaking && !isSpeaking) {
                        isSpeaking = true;

                    } else {
                    }
                }, 500);
                if (isSpeaking) {
                    synth.resume();
                    isSpeaking = false;

                } else {
                    synth.pause();
                    isSpeaking = true;

                }
            } else {

            }
        }

    }

});

function appendImage(src, type) {
    const item = document.createElement('div');
    item.classList.add("message");
    item.classList.add(`message_${type}`);
    const img = document.createElement('img');
    img.src = src;
    img.onload = scrollToBottom;
    img.classList.add(`message_received_img`);
    item.appendChild(img);
    messages.appendChild(item);
}

function appendQuickReplies(quickReplies) {
    const quickRepliesNode = document.createElement('div');
    quickRepliesNode.classList.add("quick-replies");
    quickReplies.forEach(quickReply => {
        const quickReplyDiv = document.createElement('button');
        quickReplyDiv.innerHTML = quickReply.title;
        quickReplyDiv.classList.add("button");
        quickReplyDiv.addEventListener("click", () => {
            messages.removeChild(quickRepliesNode);
            appendMessage(quickReply.title, "sent");
            socket.emit('user_uttered', {
                "message": quickReply.payload,
            });
        })
        quickRepliesNode.appendChild(quickReplyDiv);
    })
    messages.appendChild(quickRepliesNode);
    scrollToBottom();
}

//voice to text

const voiceList = document.querySelector("select");

let synth = speechSynthesis,
    isSpeaking = true;

voices();

function voices() {
    for (let voice of synth.getVoices()) {
        let selected = voice.name === "Google US English" ? "selected" : "";
        let option = `<option value="${voice.name}" ${selected}>${voice.name} (${voice.lang})</option>`;
        voiceList.insertAdjacentHTML("beforeend", option);
    }
}

synth.addEventListener("voiceschanged", voices);

function textToSpeech(text) {
    let utterance = new SpeechSynthesisUtterance(text);
    for (let voice of synth.getVoices()) {
        if (voice.name === voiceList.value) {
            utterance.voice = voice;
        }
    }
    synth.speak(utterance);

}


//voice recognition

const languages = [
    {
        no: "16",
        name: "English",
        native: "English",
        code: "en",
    },];

const recordBtn = document.querySelector(".record"),
    result = document.querySelector(".result");


let SpeechRecognition =
    window.SpeechRecognition || window.webkitSpeechRecognition,
    recognition,
    recording = false;



function speechToText() {
    try {
        recognition = new SpeechRecognition();
        recognition.lang = "en";
        recognition.interimResults = true;
        recordBtn.classList.add("recording");
        //recordBtn.querySelector("p").innerHTML = "";
        recognition.start();
        recognition.onresult = (event) => {
            const speechResult = event.results[0][0].transcript;


            messageInput.placeholder = "";


            //detect when intrim results
            if (event.results[0].isFinal) {

                messageInput.value += " " + speechResult;
                clearBtn.style.display = "block";
            }
            else {

                messageInput.placeholder += " " + speechResult;

            }

        };
        recognition.onspeechend = () => {
            speechToText();
        };
        recognition.onerror = (event) => {
            stopRecording();
            if (event.error === "no-speech") {
                alert("No speech was detected. Stopping...");
            } else if (event.error === "audio-capture") {
                alert("No microphone was found. Ensure that a microphone is installed.");
            } else if (event.error === "not-allowed") {
                alert("Permission to use microphone is blocked.");
            } else if (event.error === "aborted") {
                alert("Listening Stopped.");
            } else {
                alert("Error occurred in recognition: " + event.error);
            }
        };
    } catch (error) {
        recording = false;

        console.log(error);
    }
}

recordBtn.addEventListener("click", () => {
    if (!recording) {
        speechToText();
        recording = true;
    } else {
        stopRecording();

        messageInput.placeholder = "Type your command..";
        // Output the text content
        console.log(resultText);
    }
});

function stopRecording() {
    recognition.stop();
    //recordBtn.querySelector("p").innerHTML = "Start Listening";
    recordBtn.classList.remove("recording");
    recording = false;
}

messageInput.addEventListener("input", function () {
    if (messageInput.value !== "") {
        clearBtn.style.display = "block";
    }
    else {
        clearBtn.style.display = "none";
    }

});

const clearBtn = document.querySelector(".clear");
clearBtn.addEventListener("click", () => {

    messageInput.value = "";
    messageInput.placeholder = "Type your command..";
    clearBtn.style.display = "none";
});



//slider image
const btns = document.querySelectorAll(".btnn");
const slideRow = document.getElementById("slide-row");
const main = document.querySelector("main");

let currentIndex = 0;

function updateSlide() {
    const mainWidth = main.offsetWidth;
    const translateValue = currentIndex * -mainWidth;
    slideRow.style.transform = `translateX(${translateValue}px)`;

    btns.forEach((btnn, index) => {
        btnn.classList.toggle("active", index === currentIndex);
    });
}

btns.forEach((btnn, index) => {
    btnn.addEventListener("click", () => {
        currentIndex = index;
        updateSlide();
    });
});

window.addEventListener("resize", () => {
    updateSlide();
});

function moveNextSlideAutomatically(timePeriod) {
    setInterval(() => {
        currentIndex = (currentIndex + 1) % btns.length;
        updateSlide();
    }, timePeriod);
}

// Example usage: move to next slide every 5 seconds
moveNextSlideAutomatically(5000);
