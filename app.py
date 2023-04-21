import requests
import hmac
import hashlib
import time
import random
import base64
import urllib.parse

# Consumer key and secret
from config import *
callback_url = "https://www.opendataconnect.com"

def generate_user_authorization_link(callback_url,consumer_key,consumer_secret):
    
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


generate_user_authorization_link(callback_url,consumer_key,consumer_secret)