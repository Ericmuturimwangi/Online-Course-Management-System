import requests
from requests.auth import HTTPBasicAuth
from django.conf import settings

def get_mpesa_access_token():
    url = "https://sandbox.safaricom.co.ke/oauth/v1/generate?grant_type=client_credentials"
    auth = HTTPBasicAuth(settings.MPESA_CONSUMER_KEY, settings.MPESA_CONSUMER_SECRET)

    response  = requests.get(url, auth=auth)
    access_token = response.json().get("access_token")
    return access_token

