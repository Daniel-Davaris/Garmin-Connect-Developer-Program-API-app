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
import pandas as pd

app = Flask(__name__)
app.secret_key = 'lotus'


consumer_key = os.environ.get('consumer_key')
consumer_secret = os.environ.get('consumer_secret')
access_token = os.environ.get('julian_access_token')
access_token_secret = os.environ.get('julian_access_token_secret')

#callback_url = "https://gcdp.azurewebsites.net/callback"

#request_token_secret_dict = {}

# def request_respiration_data(access_token, access_token_secret):
#     consumer_key = os.environ.get('consumer_key')
#     consumer_secret = os.environ.get('consumer_secret')
    
#     # Configure OAuth1Session with the access token and secret
#     oauth = OAuth1Session(
#         consumer_key,
#         client_secret=consumer_secret,
#         resource_owner_key=access_token,
#         resource_owner_secret=access_token_secret
#     )

#     # Prepare the request parameters
#     start_time = int(time.time()) - 86400
#     end_time = int(time.time())

#     url = f"https://apis.garmin.com/wellness-api/rest/respiration?uploadStartTimeInSeconds={start_time}&uploadEndTimeInSeconds={end_time}"
    
#     # Make a request to the Garmin API
#     response = oauth.get(url)

#     if response.status_code == 200:
#         print("Data: ",response.json())
#         return response.json()
#     else:
#         print("Error getting respiration data:", response.text)
#         return None


# def request_respiration_backfill_data(access_token, access_token_secret, start_time, end_time):
#     consumer_key = os.environ.get('consumer_key')
#     consumer_secret = os.environ.get('consumer_secret')
    
#     oauth = OAuth1Session(
#         consumer_key,
#         client_secret=consumer_secret,
#         resource_owner_key=access_token,
#         resource_owner_secret=access_token_secret
#     )


#     #callback_url = "https://gcdp.azurewebsites.net/HEALTH-Respiration"
#     url = f"https://apis.garmin.com/wellness-api/rest/backfill/respiration?summaryStartTimeInSeconds={start_time}&summaryEndTimeInSeconds={end_time}"
    

#    # url = f"https://apis.garmin.com/wellness-api/rest/backfill/respiration?summaryStartTimeInSeconds={start_time}&summaryEndTimeInSeconds={end_time}"
#     print("URL:", url)
#     print("Params:", {
#         'summaryStartTimeInSeconds': start_time,
#         'summaryEndTimeInSeconds': end_time,
#         'callbackEndpoint': urllib.parse.quote(callback_url)
#     })

#     response = oauth.get(url)

#     if response.status_code == 202:
#         print("Backfill data request accepted")
#         return f'Backfill data request accepted:{response.text}'
#     else:
#         print("Error requesting respiration backfill data:", response.text)
#         return f'Error requesting respiration backfill data:{response.text}'






@app.route("/")
def home():
    return render_template('index.html')
    
# @app.route("/request")
# def generate_user_authorization_link():
    
#     # API endpoint URL
#     url = 'https://connectapi.garmin.com/oauth-service/oauth/request_token'
#     print("\nRequest URL:\n",url)

#     # OAuth parameters
#     params = {
#         'oauth_consumer_key': consumer_key,
#         'oauth_nonce': str(random.randint(0, 1e16)),
#         'oauth_signature_method': 'HMAC-SHA1',
#         'oauth_timestamp': str(int(time.time())),
#         'oauth_version': '1.0',
#     }

#     # Generate signature base string
#     base_string = '&'.join([
#         'POST',
#         requests.utils.quote(url, safe=''),
#         requests.utils.quote('&'.join([
#             f"{requests.utils.quote(k, safe='')}"
#             f"={requests.utils.quote(params[k], safe='')}"
#             for k in sorted(params)
#         ]), safe='')
#     ])
#     print("\nSignature Base String: \n", base_string)

#     # Generate signature
#     key = f"{requests.utils.quote(consumer_secret, safe='')}&"
#     signature = hmac.new(
#         key.encode('utf-8'),
#         base_string.encode('utf-8'),
#         hashlib.sha1
#     ).digest()
#     params['oauth_signature'] = base64.b64encode(signature).decode('utf-8')
#     print("\nOAuth signature:\n",key)
#     print("\nOAuth signature encoded:\n",params['oauth_signature'])

#     # Set headers
#     headers = {
#         'Authorization': 'OAuth ' + ', '.join([
#             f"{k}=\"{requests.utils.quote(params[k], safe='')}\","
#             for k in sorted(params)
#         ])[:-1]
#     }
#     print("\nAuthorization HTTP header:\n",headers)

#     # Make API request
#     response = requests.post(url, headers=headers)
#     print("\nRequest response:\n",response)

#     # Extract request token and secret from response
#     response_text = response.text
#     request_token = response_text.split('&')[0].split('=')[1]
#     request_token_secret = response_text.split('&')[1].split('=')[1]

#     print(f"\nRequest Token:\n {request_token}")
#     print(f"\nRequest Token Secret:\n {request_token_secret}")

#     authorize_url = f"https://connect.garmin.com/oauthConfirm?oauth_token={request_token}&oauth_callback={urllib.parse.quote(callback_url)}"
#     print("\nUser authorization link:\n",authorize_url,"\n")

#     request_token_secret_dict[request_token] = request_token_secret
#     return redirect(authorize_url)
    


# @app.route("/callback")
# def get_access_token():
#     global request_token_secret_dict
#     ACCESS_TOKEN_URL = "https://connectapi.garmin.com/oauth-service/oauth/access_token"
    
#     # Obtain the request token and secret from the query parameters
#     request_token = request.args.get("oauth_token")
#     request_token_secret = request_token_secret_dict.get(request_token)
#     if not request_token_secret:
#         return "Request token secret not found", 400

#     oauth = OAuth1Session(
#         consumer_key,
#         client_secret=consumer_secret,
#         resource_owner_key=request_token,
#         resource_owner_secret=request_token_secret,
#         verifier=request.args.get("oauth_verifier"),
#     )

#     response = oauth.fetch_access_token(ACCESS_TOKEN_URL)

#     access_token = response.get("oauth_token")
#     access_token_secret = response.get("oauth_token_secret")

#     if not access_token or not access_token_secret:
#         return "Access token or access token secret not found", 400

#     # Add the access token and secret to the session object
#     session['access_token'] = access_token
#     session['access_token_secret'] = access_token_secret

#     print("\naccess_token:\n",access_token)
#     print("\naccess_token_secret:\n",access_token_secret)
#     return render_template('got_token.html', access_token=access_token,access_token_secret=access_token_secret)


# @app.route("/data")
# def get_data():
#     access_token = os.environ.get('julian_access_token')
#     access_token_secret = os.environ.get('julian_access_token_secret')

    
#     logging.info("Fetching respiration data...")
#     respiration_data = request_respiration_data(access_token, access_token_secret)
    
#     if respiration_data is None:
#         return "Error fetching respiration data", 500
#     logging.info("Respiration data fetched successfully")

#     return f'Respiration data {respiration_data}'

# @app.route("/data_all")
# def get_data_all():
#     access_token = os.environ.get('julian_access_token')
#     access_token_secret = os.environ.get('julian_access_token_secret')

#     # Request backfill data
#     start_time = int(time.time()) - (86400 * 10)  # 10 days ago
#     end_time = int(time.time()) - 86400  # 1 day ago
#     request_respiration_backfill_data(access_token, access_token_secret, start_time, end_time)
    
#     return "Done!"

# @app.route("/HEALTH-Respiration", methods=['POST'])
# def receive_respiration_summaries():
#     data = request.get_json()

#     # Check if the data is a dictionary, otherwise set an empty dictionary as a fallback
#     if not isinstance(data, dict):
#         data = {}

#     respiration_data = data.get("respirationData", {})
#     session["respiration_data"] = respiration_data

#     # Store backfill data if available
#     if "backfill" in data:
#         backfill_respiration_data = data.get("backfill", {}).get("respirationData", {})
#         session["backfill_respiration_data"] = backfill_respiration_data
#         requests.post("https://gcdp.azurewebsites.net/backfill_respiration_data", json={"respirationData": backfill_respiration_data})

#     return jsonify({"message": "Respiration summaries data received successfully"})



# @app.route("/display_respiration_data")
# def display_respiration_data():
#     respiration_data_raw = session.get("respiration_data", {})
#     if not respiration_data_raw:
#         return "No respiration data available", 404

#     respiration_data = [
#         {
#             "timestamp": item["timestamp"],
#             "respirationRate": item["respirationRate"]
#         }
#         for item in respiration_data_raw
#     ]

#     return render_template("display_respiration_data.html", respiration_data=respiration_data)


# @app.route("/backfill_respiration_data", methods=['POST'])
# def backfill_respiration_data():
#     data = request.json

#     # Check if the data is a dictionary, otherwise set an empty dictionary as a fallback
#     if not isinstance(data, dict):
#         data = {}

#     respiration_data = data.get("respirationData", {})
#     session["backfill_respiration_data"] = respiration_data

#     return jsonify({"message": "Backfill respiration data received successfully"})


# @app.route("/display_backfill_respiration_data")
# def display_backfill_respiration_data():
#     backfill_respiration_data_raw = session.get("backfill_respiration_data", {})
#     if not backfill_respiration_data_raw:
#         return "No backfill respiration data available", 404

#     backfill_respiration_data = [
#         {
#             "timestamp": item["timestamp"],
#             "respirationRate": item["respirationRate"]
#         }
#         for item in backfill_respiration_data_raw
#     ]

#     return render_template("display_backfill_respiration_data.html", backfill_respiration_data=backfill_respiration_data)

def fetch_respiration_summaries(upload_start_time, upload_end_time):
    base_url = "https://apis.garmin.com/wellness-api/rest/respiration"
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json"
    }
    params = {
        "uploadStartTimeInSeconds": upload_start_time,
        "uploadEndTimeInSeconds": upload_end_time
    }
    response = requests.get(base_url, headers=headers, params=params)
    
    if response.status_code == 200:
        return response.json()  
    else:
        return None

def fetch_respiration_summaries(upload_start_time, upload_end_time):
    base_url = "https://apis.garmin.com/wellness-api/rest/respiration"
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json"
    }
    params = {
        "uploadStartTimeInSeconds": upload_start_time,
        "uploadEndTimeInSeconds": upload_end_time
    }
    response = requests.get(base_url, headers=headers, params=params)
    
    if response.status_code == 200:
        print("RESSSSSSSSSSSSSPONCEEE")
        return response.json()
    else:
        return None


@app.route("/HEALTH-Respiration", methods=["POST"])
def webhook1():
    # Parse the incoming JSON payload
    # Parse the incoming JSON payload
    payload = request.json
    print(payload)
    # Check if the payload has the expected fields
    if "uploadStartTimeInSeconds" in payload and "uploadEndTimeInSeconds" in payload:
        upload_start_time = payload["uploadStartTimeInSeconds"]
        upload_end_time = payload["uploadEndTimeInSeconds"]

        # Fetch the respiration summaries using these timestamps
        respiration_summaries = fetch_respiration_summaries(upload_start_time, upload_end_time)
        
        # Display or process the respiration summaries as needed
        print(respiration_summaries)
        
        return jsonify({"message": "Received and processed respiration summaries"}), 200
    else:
        return jsonify({"message": "Invalid payload"}), 400

@app.route("/HEALTH-Sleeps", methods=["POST"])
def webhook2():
    # Parse the incoming JSON payload
    payload = request.json
   
    print("New data recieved: ")
    print(payload)
    return "Good"


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    app.run()