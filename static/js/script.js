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

    // socket.emit('message', { tabId: currentTabId, data: input.value });

    const nlQuery = input.value;
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

            document.getElementById('sql-query').value = data.content || '';
            // Display additional data (if any) in the data-display area
            // document.getElementById('data-display').textContent = JSON.stringify(data.query_data, null, 2);
            displayDataAsTable(data.query_data);
            // displayHistory(data.last_history);

        // }
        input.value = ''; // Clear the NL input after processing
    })
    .catch(error => {
        console.error('Error processing NL query:', error);
        document.getElementById('data-display').textContent = 'Processing error: ' + error.message;
    });
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
        // const display = document.getElementById('data-display');
        // display.innerHTML = ''; // Clear previous results
        // data.forEach(row => {
        //     const content = document.createElement('p');
        //     content.textContent = JSON.stringify(row);
        //     display.appendChild(content);
        // });
        displayDataAsTable(data);  // Assuming 'data' is the JSON array received from the server

    })
    .catch(error => console.error('Error running query:', error));
}

// Function to display JSON data as a table in the data-display element
function displayDataAsTable(jsonData) {
    const displayArea = document.getElementById('data-display');
    displayArea.innerHTML = '';  // Clear previous contents

    if (!jsonData) {
        displayArea.innerHTML = '<p>No data to display.</p>';
        return;
    }

    // Create a table element
    const table = document.createElement('table');
    table.style.width = '100%';
    table.setAttribute('border', '1');
    table.setAttribute('cellspacing', '0');
    table.setAttribute('cellpadding', '5');

    // Create the header row
    const thead = document.createElement('thead');
    const headerRow = document.createElement('tr');
    Object.keys(jsonData[0]).forEach(key => {
        const headerCell = document.createElement('th');
        headerCell.textContent = key;
        headerRow.appendChild(headerCell);
    });
    thead.appendChild(headerRow);
    table.appendChild(thead);

    // Create the body of the table
    const tbody = document.createElement('tbody');
    jsonData.forEach(item => {
        const row = document.createElement('tr');
        Object.values(item).forEach(value => {
            const cell = document.createElement('td');
            cell.textContent = value;
            row.appendChild(cell);
        });
        tbody.appendChild(row);
    });
    table.appendChild(tbody);

    // Append the table to the display area
    displayArea.appendChild(table);
}

function displayHistory(historyPrompts) {
    const historyContainer = document.getElementById('chat-box');  // Ensure this is the correct container
    historyContainer.innerHTML = '';  // Clear previous content

    if (!Array.isArray(historyPrompts)) {
        console.error('Expected historyPrompts to be an array, received:', historyPrompts);
        return;
    }

    historyPrompts.forEach(entry => {
        const promptElement = document.createElement('div');
        promptElement.innerHTML = `
            <div class="history-entry">
                <p><strong>Prompt:</strong> ${entry.Prompt}</p>
                <p><strong>SQL:</strong> ${entry.Sql}</p>
                <p><strong>Cost:</strong> $${entry.TotalCost}</p>
            </div>
        `;
        historyContainer.appendChild(promptElement);
    });
}


// Listen for Socket.IO responses
socket.on('response', function(data) {
    if (data.tabId === currentTabId) {
        var chatBox = document.getElementById('chat-box');
        chatBox.innerHTML += '<br>' + data.data;
    }
});
