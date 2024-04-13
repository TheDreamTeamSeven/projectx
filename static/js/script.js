// script.js
var socket = io();
var tabs = [];
var currentTabId = 0;

function addTab() {
    var tabName = document.getElementById('new-tab-name').value.trim() || 'New Tab';
    var tabId = tabs.length;  // Assign a new tab ID based on length of the tabs array
    tabs.push(tabName);  // Store tab name in array
    var tab = document.createElement('div');
    tab.className = 'tab';
    tab.textContent = tabName;
    tab.setAttribute('data-tabid', tabId);  // Set a data attribute for the tabId
    tab.onclick = function () { switchTab(tabId); };
    document.getElementById('tabs').appendChild(tab);
    document.getElementById('new-tab-name').value = ''; // Clear input after adding
    switchTab(tabId); // Switch to new tab automatically
}

function switchTab(tabId) {
    currentTabId = tabId;
    var chatBox = document.getElementById('chat-box');
    chatBox.innerHTML = 'Chat content for ' + tabs[tabId];  // Use the tabId to fetch the correct tab name
}

function sendMessage() {
    var input = document.getElementById('chat-input');
    if (input.value.trim() === '') return;  // Prevent empty messages
    socket.emit('message', { tabId: currentTabId, data: input.value });
    input.value = '';
}

socket.on('response', function(data) {
    if (data.tabId === currentTabId) {
        var chatBox = document.getElementById('chat-box');
        chatBox.innerHTML += '<br>' + data.data;
    }
});
