const express = require('express');
const cors = require('cors');
const path = require('path');
const app = express();
const port = 3000;


const { nlpParse } = require('./services/nlpService');

const fs = require('fs');

const queryFilePath = path.join(__dirname, 'data', 'queries.json'); 
const siemData = JSON.parse(fs.readFileSync(queryFilePath, 'utf8'));


app.use(cors());
app.use(express.json());


app.post('/api/v1/query', (req, res) => {
    const userQuery = req.body.user_query;

    if(!userQuery) {
        return res.status(400)
        .json({ status: 'error', message: 'Missing user_query in request body. '});
    }

    const { intent } = nlpParse(userQuery);

    if(intent === 'unknown') {
        return res.status(404).json({
            status: 'error',
            message: 'Sorry, I could not understand the request'
        });
    }

    const responseData = siemData[intent];

    if(!responseData) {
        return res.status(500).json({
            status: 'error',
            message: `Internal error: No data found for intent '${intent}'.`
        });
    }

    res.json({
        status: 'success',
        data: responseData
    });

});




app.listen(port, () => {
  console.log(`Server is listening at http://localhost:${port}`);
    
})