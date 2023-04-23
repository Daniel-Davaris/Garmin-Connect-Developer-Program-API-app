# Daniel Davaris for Open Data Connect Pty Ltd
# 04/2023
# Garmin Connect Developer Program app/API

import requests
import hmac
import hashlib
import time
from datetime import date
import random
import base64
import urllib.parse
import os
import json
from requests_oauthlib import OAuth1Session
from flask import Flask, redirect, request, render_template, session, jsonify 
import logging


app = Flask(__name__)
app.secret_key = 'lotus'


# Consumer key and secret
consumer_key = os.environ.get('consumer_key')
consumer_secret = os.environ.get('consumer_secret')

callback_url = "https://gcdp.azurewebsites.net/callback"

request_token_secret_dict = {}

def request_respiration_data(access_token, access_token_secret):
    consumer_key = os.environ.get('consumer_key')
    consumer_secret = os.environ.get('consumer_secret')
    
    # Configure OAuth1Session with the access token and secret
    oauth = OAuth1Session(
        consumer_key,
        client_secret=consumer_secret,
        resource_owner_key=access_token,
        resource_owner_secret=access_token_secret
    )

    # Prepare the request parameters
    start_time = int(time.time()) - 86400
    end_time = int(time.time())

    url = f"https://apis.garmin.com/wellness-api/rest/respiration?uploadStartTimeInSeconds={start_time}&uploadEndTimeInSeconds={end_time}"
    
    # Make a request to the Garmin API
    response = oauth.get(url)

    if response.status_code == 200:
        print("Data: ",response.json())
        return response.json()
    else:
        print("Error getting respiration data:", response.text)
        return None


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

    # Add the access token and secret to the session object
    session['access_token'] = access_token
    session['access_token_secret'] = access_token_secret

    print("\naccess_token:\n",access_token)
    print("\naccess_token_secret:\n",access_token_secret)
    return render_template('got_token.html', access_token=access_token,access_token_secret=access_token_secret)

# @app.route("/data")
# def get_data():
#     # Get access token and secret from session or database
#     # Later on this will be setup to the user that authenticates but for now it is just going to connect to a single user for testing 
#     #access_token = session.get('access_token')
#     #access_token_secret = session.get('access_token_secret')
#     access_token = os.environ.get('julian_access_token')
#     access_token_secret = os.environ.get('julian_access_token_secret')

#     return f'Julians access token {access_token}'

@app.route("/data")
def get_data():
    access_token = os.environ.get('julian_access_token')
    access_token_secret = os.environ.get('julian_access_token_secret')

    
    logging.info("Fetching respiration data...")
    respiration_data = request_respiration_data(access_token, access_token_secret)
    
    if respiration_data is None:
        return "Error fetching respiration data", 500
    logging.info("Respiration data fetched successfully")

    #return f'Respiration data {respiration_data}'
   
    logging.info("Sending respiration data to /HEALTH-Respiration...")
    response = requests.post("https://gcdp.azurewebsites.net/HEALTH-Respiration", json=respiration_data,timeout=20)
    if response.status_code == 200:
        logging.info("Respiration data sent successfully")
        return "Respiration data sent successfully"
    else:
        logging.error(f"Error sending respiration data: {response.text}")
        return f"Error sending respiration data: {response.text}", 500
    
    



@app.route("/HEALTH-Respiration", methods=['POST'])
def receive_respiration_summaries():
    data = request.json

    # Check if the data is a dictionary, otherwise set an empty dictionary as a fallback
    if not isinstance(data, dict):
        data = {}

    respiration_data = data.get("respirationData", {})
    session["respiration_data"] = respiration_data
    
    return jsonify({"message": "Respiration summaries data received successfully"})
 

@app.route("/display_respiration_data")
def display_respiration_data():
    respiration_data = session.get("respiration_data", {})
    if not respiration_data:
        return "No respiration data available", 404
    return render_template("display_respiration_data.html", respiration_data=respiration_data)

@app.route("/test")
def test_route():
    return "Test route is working"

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    app.run()