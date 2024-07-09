import base64
import requests
from .auth import MpesaBase
import datetime

class MpesaExpress(MpesaBase):
	def __init__(self, env="sandbox", app_key=None, app_secret=None, sandbox_url=None, live_url=None):
		MpesaBase.__init__(self, env, app_key, app_secret, sandbox_url, live_url)

		self.authentication_token = self.authenticate()

	def stk_push(self, business_shortcode=None, passcode=None, amount=None, callback_url=None, reference_code=None, phone_number=None, description=None):
		time = str(datetime.datetime.now()).split(".")[0].replace("-", "").replace(",", "").replace(":", "")
		password = f"{business_shortcode}{passcode}{time}"
		encoded = base64.b64encode(password.encode())
		payload = {
			"BusinessShortCode": business_shortcode,
			"Pasword": encoded.decode('utf-8'),
			"Timestamp": time,
			"TransactionType": "CustomerPayBillOnline",
			"Amount": amount,
			"PartyA": int(phone_number),
			"PartyB": business_shortcode,
			"PhoneNumber": int(phone_number),
			"CallBackURL": callback_url,
			"AccountReference": reference_code,
			"TransactionDesc": description
		}
		headers = {'Authorization': f"Bearer {self.authentication_token}", 'Content-Type': "application/json"}
		if self.env == "production":
			base_safaricom_url = self.live_url
		else:
			saf_url = f"{base_safaricom_url}/mpesa/stkpush/v1/processrequest"
		r = requests.post(saf_url, headers=headers, json=payload)
		return r.json()

def query(self, business_shortcode=None, checkout_request_id=None, passcode=None):
	time = str(datetime.datetime.now()).split(".")[0].replace(
            "-", "").replace(" ", "").replace(":", "")
	password = f"{business_shortcode}{passcode}{time}"
	encoded = base64.b64encode(password.encode())
	payload = {
            "BusinessShortCode": business_shortcode,
            "Password": str(encoded),
            "Timestamp": time,
            "CheckoutRequestID": checkout_request_id
        }
	headers = {'Authorization': f"Bearer {self.authentication_token}", 'Content-Type': "application/json"}
	if self.env == "production":
            base_safaricom_url = self.live_url
        else:
            base_safaricom_url = self.sandbox_url
        saf_url = f"{base_safaricom_url}/mpesa/stkpushquery/v1/query"
	r = requests.post(saf_url, headers=headers, json=payload)
	return r.json()