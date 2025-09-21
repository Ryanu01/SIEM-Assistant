const fs = require('fs');
const path = require('path');

// Load your fake SIEM data from the root queries.json file
const siemDataPath = path.join(__dirname, '../../queries.json');
const siemData = JSON.parse(fs.readFileSync(siemDataPath, 'utf8'));

/**
 * Simulates an API call to a specific SIEM endpoint based on the intent.
 * In a real application, this would use a library like 'axios' or 'node-fetch'
 * to make a real HTTP request.
 * @param {string} intent The detected intent from the user's query.
 * @param {object} params A dictionary of parameters (e.g., time_period).
 * @returns {Promise<object>} The data corresponding to the intent.
 */
const fetchSIEMData = async (intent, params) => {
    // This is the core logic: we map an intent to a key in our fake data
    // and pretend we're getting a real response.
    const dataKey = {
        "find_blocked_clicks": "find_blocked_logins", // Re-using old key for now
        "find_permitted_clicks": "find_failed_logins", // Re-using old key for now
        "find_blocked_messages": "find_malware",
        "find_delivered_messages": "find_malware",
        "find_all_threats": "find_malware",
    }[intent];

    if (!dataKey) {
        return { error: `No data mapping found for intent: ${intent}` };
    }

    // Simulate filtering based on parameters (e.g., time_period)
    // This part would be more complex in a real app
    const data = siemData[dataKey];
    
    return { status: 'success', data: data };
};

module.exports = { fetchSIEMData };
