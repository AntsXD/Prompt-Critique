from flask import Flask, request, jsonify, render_template_string
import warnings
warnings.filterwarnings("ignore")
from crew_builder import create_crew
import os


import threading
import time



app = Flask(__name__)




HTML_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
<title>AI Response Generator</title>
<meta name="viewport" content="width=device-width, initial-scale=1">
<style>
body { font-family: Arial, sans-serif; max-width: 800px; margin: 0 auto; padding: 20px; }
.container { background: #f5f5f5; padding: 20px; border-radius: 10px; }
textarea { width: 100%; height: 100px; margin: 10px 0; padding: 10px; border: 1px solid #ddd; border-radius: 5px; }
button { background: #007bff; color: white; padding: 10px 20px; border: none; border-radius: 5px; cursor: pointer; }
button:hover { background: #0056b3; }
button:disabled { background: #ccc; cursor: not-allowed; }
.response { background: white; padding: 20px; margin: 20px 0; border-radius: 5px; border-left: 4px solid #007bff; }
.loading { color: #666; font-style: italic; }
.error { color: #dc3545; background: #f8d7da; padding: 10px; border-radius: 5px; }

        /* Basic styling for Markdown output */
        .response h1, .response h2, .response h3, .response h4, .response h5, .response h6 {
            margin-top: 1em;
            margin-bottom: 0.5em;
        }
        .response ul, .response ol {
            margin-left: 20px;
            padding-left: 0;
        }
        .response p {
            margin-bottom: 1em;
        }
        .response pre {
            background-color: #eee;
            padding: 10px;
            border-radius: 5px;
            overflow-x: auto;
        }
        .response code {
            font-family: monospace;
            background-color: #f0f0f0; /* Lighter background for inline code */
            padding: 2px 4px;
            border-radius: 3px;
        }
        .response pre code {
            background-color: transparent; /* No extra background for block code */
            padding: 0;
        }
</style>
    <script src="https://cdn.jsdelivr.net/npm/marked/marked.min.js"></script>
</head>
<body>
<div class="container">
<h1>🤖 AI Response Generator</h1>
<p>Enter your prompt and get a comprehensive, well-researched response!</p>

<form id="promptForm">
<textarea id="promptInput" placeholder="Enter your question or prompt here..." required></textarea>
<br>
<button type="submit" id="submitBtn">Generate Response</button>
</form>

<div id="result"></div>
</div>

<script>
document.getElementById('promptForm').addEventListener('submit', async function(e) {
e.preventDefault();

const prompt = document.getElementById('promptInput').value;
const submitBtn = document.getElementById('submitBtn');
const result = document.getElementById('result');

// Show loading state
submitBtn.disabled = true;
submitBtn.textContent = 'Generating...';
result.innerHTML = '<div class="loading">🔄 Processing your request... This may take a few minutes.</div>';

try {
const response = await fetch('/generate', {
method: 'POST',
headers: {
'Content-Type': 'application/json',
},
body: JSON.stringify({ prompt: prompt })
});

const data = await response.json();

if (data.success) {
// Use marked.parse() to convert Markdown to HTML
                    // Marked.js automatically handles HTML escaping of its output
const htmlResponse = marked.parse(data.response);

                    // Changed <pre> to <div> because marked.js outputs full HTML
result.innerHTML = `<div class="response"><h3>✅ Generated Response:</h3><div style="max-height: 400px; overflow: auto;">${htmlResponse}</div></div>`;
} else {
result.innerHTML = `<div class="error">❌ Error: ${data.error}</div>`;
}
} catch (error) {
result.innerHTML = `<div class="error">❌ Error: ${error.message}</div>`;
}

// Reset button
submitBtn.disabled = false;
submitBtn.textContent = 'Generate Response';
});
</script>
</body>
</html>
"""


@app.route('/')
def home():
    return render_template_string(HTML_TEMPLATE)

@app.route('/generate', methods=['POST'])
def generate_response():
    try:
        data = request.get_json()
        prompt = data.get('prompt')

        if not prompt:
            return jsonify({'success': False, 'error': 'No prompt provided'})
        crew = create_crew(prompt)
        result = crew.kickoff()
      

       
        

        return jsonify({'success': True, 'response': str(result)})

    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/health')
def health_check():
    return jsonify({'status': 'healthy', 'message': 'Server is running'})

if __name__ == '__main__':
    
    app.run(host='0.0.0.0', port=10000, debug=False)


