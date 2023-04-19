import requests
from requests_oauthlib import OAuth2Session

# Sep up the OAuth 2.0 client with your client ID and client secret
from config import * # Stored in git ingnored file for security

# Setup the OAuth 2.0 session 
garmin_oauth = OAuth2Session(client_id,redirect_uri='http://localhost:8000/callback')

# A function to initate the OAuth 2.0 flow and redirect the user to the Garmin Connect login page
def authorise():
    # Generate the authorisation URL with the requested data scopes
    authorisation_url, state = garmin_oauth.authorization_url(
        authorisation_base_url,
        scope=['read_all','profile'],
    )

    # Redirect the user to the authorization URL
    return authorisation_url

# A function to handle the callback URL after the user logs in and authorizes the app
def callback(url):
    # Exchange the authorization code for an access token
    garmin_oauth.fetch_token(
        token_url,
        authorization_response=url,
        client_secret=client_secret,
    )

    # Use the access token to make API requests to the Garmin Connect API
    access_token = garmin_oauth.token(['access_token'])
    # Make API requests with the access_token