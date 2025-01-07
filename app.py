from flask import Flask, render_template, request, jsonify
import urllib.request
import json
import os
import ssl
from dotenv import load_dotenv  # Import load_dotenv

app = Flask(__name__)

# Load environment variables from .env file
load_dotenv()

# Allow self-signed certificates if necessary
def allowSelfSignedHttps(allowed):
    if allowed and not os.environ.get('PYTHONHTTPSVERIFY', '') and getattr(ssl, '_create_unverified_context', None):
        ssl._create_default_https_context = ssl._create_unverified_context

allowSelfSignedHttps(True)

# Azure endpoint details from environment variables
url = os.getenv('URL')
api_key = os.getenv('API_KEY')

if not url or not api_key:
    raise ValueError("URL and API_KEY must be set in the .env file.")

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/ask', methods=['POST'])
def ask():
    user_input = request.form['query']
    data = {'Query': user_input}
    body = str.encode(json.dumps(data))
    headers = {
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {api_key}'
    }

    req = urllib.request.Request(url, body, headers)

    try:
        with urllib.request.urlopen(req) as response:
            result = response.read()
            result_json = json.loads(result)
            print("API Response:", result_json)  # Log the full API response

            # Extract 'Output' from the API response
            answer = result_json.get('Output', 'No answer provided.')

            return jsonify({'answer': answer})
    except urllib.error.HTTPError as error:
        error_message = error.read().decode()
        print(f"HTTPError: {error.code} - {error_message}")  # Log HTTP errors
        return jsonify({'error': f"Request failed with status code: {error.code}, message: {error_message}"})
    except Exception as e:
        print(f"Exception: {str(e)}")  # Log unexpected exceptions
        return jsonify({'error': f"An unexpected error occurred: {str(e)}"})

if __name__ == '__main__':
    app.run(debug=True)
