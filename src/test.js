const express = require('express');
const cors = require('cors');
const path = require('path');
const fs = require('fs');
const app = express();
const jwt = require('jsonwebtoken');
const port = 3000;

// Correctly import the nlpService module
const { nlpParse } = require('./services/nlpService');

// This file is now our mock database, located at the root
const queriesFilePath = path.join(__dirname, 'data', 'queries.json');
const siemData = JSON.parse(fs.readFileSync(queriesFilePath, 'utf8'));

app.use(cors());
app.use(express.json());

// --- New Endpoint Logic ---

//Mock user data

const users = [
    {username: 'admin', password: 'admin'}
];

//New endpoint for login

const JWT_SECRET = "930239daba3eda311bb2e41d67b312eba2bfd0be8cf11971f9a68ae465b05c9d";

app.post('/api/v1/login', (req, res) => {
    const {username, password} = req.body;
    if(!username || !password) {
        return res.status(400).json({ status: 'error', message: 'Username and password required'});
    }
    
    const user = users.find(u => u.username === username);

    if (user && user.password === password) {

        const token = jwt.sign(
            {username: user.username},
            JWT_SECRET,
            {expiresIn: '1h'}
        );

        return res.
        json({status: 'success',
        message: 'Login successfull',
        user: {username: user.username}, 
        token: token});
    }else {
        return res.status(401).json({ status: 'error', message: 'Invalid username or password'});
    }
})

app.get('api/v1/users', (req, res) => {
    res.json(users);
})


// Endpoint for fetching events for blocked clicks
app.post('/v2/siem/clicks/blocked', (req, res) => {
    // In a real app, this would query the SIEM for blocked clicks
    const mockData = siemData.find_failed_logins;
    res.json({
        status: 'success',
        data: mockData
    });
});

// Endpoint for fetching events for messages with a known threat
app.post('/v2/siem/messages/blocked', (req, res) => {
    // In a real app, this would query the SIEM for blocked messages
    const mockData = siemData.find_malware;
    res.json({
        status: 'success',
        data: mockData
    });
});

// Endpoint for fetching all clicks and messages related to known threats
app.post('/v2/siem/all', (req, res) => {
    // This is a more complex endpoint, so we combine data
    const allThreats = [
        ...siemData.find_malware, 
        ...siemData.find_failed_logins
    ];
    res.json({
        status: 'success',
        data: allThreats
    });
});

// --- Your main conversational assistant endpoint ---
// This endpoint now acts as a router that directs traffic
app.post('/api/v1/query', async (req, res) => {
    const userQuery = req.body.user_query;

    if (!userQuery) {
        return res.status(400).json({ status: 'error', message: 'Missing user_query in request body.' });
    }

    const { intent } = nlpParse(userQuery);

    if (intent === 'unknown') {
        return res.status(404).json({
            status: 'error',
            message: 'Sorry, I could not understand the request'
        });
    }

    // A simple mapping to route the request to the correct internal endpoint
    const endpointMap = {
        'find_failed_logins': '/v2/siem/clicks/blocked',
        'find_malware': '/v2/siem/messages/blocked',
        'count_alerts_by_host': '/v2/siem/all',
    };

    const targetEndpoint = endpointMap[intent];
    if (!targetEndpoint) {
         return res.status(500).json({ status: 'error', message: `No API endpoint found for intent: '${intent}'.` });
    }

    try {
        // Use an internal fetch call to route to the correct endpoint
        const response = await fetch(`http://localhost:${port}${targetEndpoint}`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ user_query: userQuery })
        });
        
        const data = await response.json();
        
        // Return the data from the specific endpoint
        res.json({
            status: 'success',
            data: data.data,
            intent: intent
        });

    } catch (error) {
        console.error('Routing failed:', error);
        res.status(500).json({ status: 'error', message: 'An internal routing error occurred.' });
    }
});


app.get('/', (req, res) => {
  res.sendFile(path.join(__dirname, '..', 'public', 'second.htm'));
});


// Serve the static HTML file
app.use(express.static('public'));

app.listen(port, () => {
    console.log(`Server is listening at http://localhost:${port}`);
});
