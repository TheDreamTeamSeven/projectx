// script.js
var socket = io();
var tabs = [];
var currentTabId = 0;

// Add a new tab
function addTab() {
    var tabName = document.getElementById('new-tab-name').value.trim() || 'New Tab';
    var tabId = tabs.length; // Assign a new tab ID based on the length of the tabs array
    tabs.push(tabName); // Store tab name in the array
    var tab = document.createElement('div');
    tab.className = 'tab';
    tab.textContent = tabName;
    tab.setAttribute('data-tabid', tabId); // Set a data attribute for the tabId
    tab.onclick = function () { switchTab(tabId); };
    document.getElementById('tabs').appendChild(tab);
    document.getElementById('new-tab-name').value = ''; // Clear input after adding
    switchTab(tabId); // Switch to new tab automatically
}

// Switch the chat tab
function switchTab(tabId) {
    currentTabId = tabId;
    var chatBox = document.getElementById('chat-box');
    chatBox.innerHTML = 'Chat content for ' + tabs[tabId]; // Use the tabId to fetch the correct tab name
}

// Send a message
function sendMessage() {
    var input = document.getElementById('chat-input');
    if (input.value.trim() === '') return; // Prevent empty messages
    socket.emit('message', { tabId: currentTabId, data: input.value });
    input.value = '';
}

// Process natural language query
function processNLQuery() {
    const nlQuery = document.getElementById('chat-input').value; // Reusing chat-input for NL query
    fetch('/process-query', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ query: nlQuery })
    })
    .then(response => response.json())
    .then(data => {
        console.log('Query processed:', data);
        document.getElementById('data-display').textContent = JSON.stringify(data, null, 2);
    })
    .catch(error => console.error('Error processing NL query:', error));
}

// Run SQL query
function sendQuery() {
    const query = document.getElementById('sql-query').value;
    fetch('/execute-query', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ query: query })
    })
    .then(response => response.json())
    .then(data => {
        const display = document.getElementById('data-display');
        display.innerHTML = ''; // Clear previous results
        data.forEach(row => {
            const content = document.createElement('p');
            content.textContent = JSON.stringify(row);
            display.appendChild(content);
        });
    })
    .catch(error => console.error('Error running query:', error));
}

// Initialize database structure
function initDatabase() {
    fetch('/init-db-structure')
        .then(response => response.json())
        .then(data => {
            console.log('Database initialized:', data);
        })
        .catch(error => console.error('Error initializing database:', error));
}

document.addEventListener('DOMContentLoaded', function() {
    initDatabase(); // Automatically initialize the database on page load
});

// Listen for Socket.IO responses
socket.on('response', function(data) {
    if (data.tabId === currentTabId) {
        var chatBox = document.getElementById('chat-box');
        chatBox.innerHTML += '<br>' + data.data;
    }
});
