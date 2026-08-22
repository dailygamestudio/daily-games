const https = require('https');
const fs = require('fs');
const path = require('path');

const NIM_API_URL = 'https://integrate.api.nvidia.com/v1/chat/completions';
const NIM_MODEL = 'nvidia/nemotron-3-ultra-550b-a55b';

const NIM_KEY_FILE = path.join('/home/ethan/.hermes/profiles/default', '.nim-api-key');
const NIM_API_KEY = fs.existsSync(NIM_KEY_FILE) ? fs.readFileSync(NIM_KEY_FILE, 'utf-8').trim() : '';

const HEADERS = {
    'Authorization': `Bearer ${NIM_API_KEY}`,
    'Content-Type': 'application/json'
};

async function callNIMAPI(prompt, maxRetries = 3) {
    const payload = {
        model: NIM_MODEL,
        messages: [{ role: 'user', content: prompt }],
        temperature: 0.3,
        max_tokens: 8000
    };

    for (let attempt = 0; attempt < maxRetries; attempt++) {
        try {
            const response = await makeRequest(payload);
            return response;
        } catch (error) {
            console.log(`NIM API attempt ${attempt + 1} failed: ${error.message}`);
            
            if (error.message.includes('429')) {
                console.log('Rate limited (429). Waiting 30 minutes...');
                await sleep(30 * 60 * 1000);
                continue;
            }
            
            if (attempt === maxRetries - 1) {
                throw error;
            }
            
            await sleep(60 * 1000);
        }
    }
    
    throw new Error('NIM API failed after max retries');
}

function makeRequest(payload) {
    return new Promise((resolve, reject) => {
        const data = JSON.stringify(payload);
        
        const options = {
            hostname: 'integrate.api.nvidia.com',
            path: '/v1/chat/completions',
            method: 'POST',
            headers: {
                ...HEADERS,
                'Content-Length': Buffer.byteLength(data)
            }
        };
        
        const req = https.request(options, (res) => {
            let data = '';
            res.on('data', chunk => data += chunk);
            res.on('end', () => {
                if (res.statusCode === 200) {
                    try {
                        resolve(JSON.parse(data));
                    } catch (e) {
                        reject(new Error('Invalid JSON response'));
                    }
                } else if (res.statusCode === 429) {
                    reject(new Error('429 Rate Limited'));
                } else {
                    reject(new Error(`HTTP ${res.statusCode}: ${data}`));
                }
            });
        });
        
        req.on('error', reject);
        req.write(data);
        req.end();
    });
}

function sleep(ms) {
    return new Promise(resolve => setTimeout(resolve, ms));
}

module.exports = { callNIMAPI };