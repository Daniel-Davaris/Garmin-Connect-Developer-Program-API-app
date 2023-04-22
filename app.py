# Daniel Davaris for Open Data Connect Pty Ltd
# 04/2023
# Garmin Connect Developer Program app/API

import requests
import hmac
import hashlib
import time
import random
import base64
import urllib.parse
import os
from requests_oauthlib import OAuth1Session
from flask import Flask, redirect, request, render_template

app = Flask(__name__)

# Consumer key and secret
consumer_key = os.environ.get('consumer_key')
consumer_secret = os.environ.get('consumer_secret')

callback_url = request.host_url + "callback"

request_token_secret_dict = {}

@app.route("/")
def home():
    return render_template('index.html')
    
@app.route("/request")
def generate_user_authorization_link():
    
    # API endpoint URL
    url = 'https://connectapi.garmin.com/oauth-service/oauth/request_token'
    print("\nRequest URL:\n",url)

    # OAuth parameters
    params = {
        'oauth_consumer_key': consumer_key,
        'oauth_nonce': str(random.randint(0, 1e16)),
        'oauth_signature_method': 'HMAC-SHA1',
        'oauth_timestamp': str(int(time.time())),
        'oauth_version': '1.0',
    }

    # Generate signature base string
    base_string = '&'.join([
        'POST',
        requests.utils.quote(url, safe=''),
        requests.utils.quote('&'.join([
            f"{requests.utils.quote(k, safe='')}"
            f"={requests.utils.quote(params[k], safe='')}"
            for k in sorted(params)
        ]), safe='')
    ])
    print("\nSignature Base String: \n", base_string)

    # Generate signature
    key = f"{requests.utils.quote(consumer_secret, safe='')}&"
    signature = hmac.new(
        key.encode('utf-8'),
        base_string.encode('utf-8'),
        hashlib.sha1
    ).digest()
    params['oauth_signature'] = base64.b64encode(signature).decode('utf-8')
    print("\nOAuth signature:\n",key)
    print("\nOAuth signature encoded:\n",params['oauth_signature'])

    # Set headers
    headers = {
        'Authorization': 'OAuth ' + ', '.join([
            f"{k}=\"{requests.utils.quote(params[k], safe='')}\","
            for k in sorted(params)
        ])[:-1]
    }
    print("\nAuthorization HTTP header:\n",headers)

    # Make API request
    response = requests.post(url, headers=headers)
    print("\nRequest response:\n",response)

    # Extract request token and secret from response
    response_text = response.text
    request_token = response_text.split('&')[0].split('=')[1]
    request_token_secret = response_text.split('&')[1].split('=')[1]

    print(f"\nRequest Token:\n {request_token}")
    print(f"\nRequest Token Secret:\n {request_token_secret}")

    authorize_url = f"https://connect.garmin.com/oauthConfirm?oauth_token={request_token}&oauth_callback={urllib.parse.quote(callback_url)}"
    print("\nUser authorization link:\n",authorize_url,"\n")

    request_token_secret_dict[request_token] = request_token_secret
    return redirect(authorize_url)
    


@app.route("/callback")
def get_access_token():
    global request_token_secret_dict
    ACCESS_TOKEN_URL = "https://connectapi.garmin.com/oauth-service/oauth/access_token"
    
    # Obtain the request token and secret from the query parameters
    request_token = request.args.get("oauth_token")
    request_token_secret = request_token_secret_dict.get(request_token)
    if not request_token_secret:
        return "Request token secret not found", 400

    oauth = OAuth1Session(
        consumer_key,
        client_secret=consumer_secret,
        resource_owner_key=request_token,
        resource_owner_secret=request_token_secret,
        verifier=request.args.get("oauth_verifier"),
    )

    response = oauth.fetch_access_token(ACCESS_TOKEN_URL)

    access_token = response.get("oauth_token")
    access_token_secret = response.get("oauth_token_secret")

    if not access_token or not access_token_secret:
        return "Access token or access token secret not found", 400

    return f"Access Token: {access_token}<br>Access Token Secret: {access_token_secret}"


if __name__ == "__main__":
    app.run()