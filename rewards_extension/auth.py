# The authentication module for frappe-ui based Single Page Applications
# Frappe 2FA - frappe.twofactor.authenticate_for_2factor
import frappe
import random
import string
import hmac
import uuid
import hashlib
import json
import base64
from enum import Enum
from frappe.sessions import Session
class AuthStatus(Enum):
    SUCCESS = "success"
    FAILURE = "failure"
class WACheck(Enum):
    NO_WANUMBER = 1
    OTP_SEND_ERROR = 2
    OTP_SENT = 3
import time

def get_secret_key():
    """Get or generate a secret key for HMAC"""
    # Use site's secret key or generate one
    return frappe.get_site_config().get('secret_key', 'default_secret_key_for_otp')

def create_otp_token(mobile, otp, expiry_timestamp):
    """Create an HMAC token containing OTP and expiry info"""
    secret_key = get_secret_key()
    data = {
        'mobile': mobile,
        'otp': otp,
        'expiry': expiry_timestamp
    }
    data_string = json.dumps(data, sort_keys=True)
    token = hmac.new(
        secret_key.encode('utf-8'),
        data_string.encode('utf-8'),
        hashlib.sha256
    ).hexdigest()
    
    # Encode the data and token together
    payload = {
        'data': data,
        'token': token
    }
    return base64.b64encode(json.dumps(payload).encode('utf-8')).decode('utf-8')

def verify_otp_token(mobile, provided_otp, stored_token):
    """Verify the OTP using the stored HMAC token"""
    try:
        # Decode the stored token
        payload = json.loads(base64.b64decode(stored_token.encode('utf-8')).decode('utf-8'))
        data = payload['data']
        stored_hmac = payload['token']
        
        # Check if token is for the correct mobile number
        if data['mobile'] != mobile:
            return False
            
        # Check if token has expired
        if int(time.time()) > data['expiry']:
            return False
            
        # Verify HMAC
        secret_key = get_secret_key()
        data_string = json.dumps(data, sort_keys=True)
        expected_hmac = hmac.new(
            secret_key.encode('utf-8'),
            data_string.encode('utf-8'),
            hashlib.sha256
        ).hexdigest()
        
        if not hmac.compare_digest(stored_hmac, expected_hmac):
            return False
            
        # Check if provided OTP matches
        return data['otp'] == provided_otp
        
    except Exception as e:
        print(f"Error verifying OTP token: {e}")
        return False

@frappe.whitelist(allow_guest=True)
def check_existing_wanumber(mobile):
    # return {'staus':False,'user':{'uname':'','pwd':''}}
    #Step 1: Check if OTP is sent to the mobile number
    #Step 2: Check if the mobile number is a valid Whatsapp Number
    #Step 2: Check if the user exists in Rewards Portal
    otp = generate_otp()
    print('mobile: ',mobile)
    print('OTP: ',otp)
    expiry = 300  # 5 minutes
    expiry_timestamp = int(time.time()) + expiry
    
    # Create HMAC token and store in session
    otp_token = create_otp_token(mobile, otp, expiry_timestamp)
    print('OTP Token:', otp_token)
    guest_otp_uuid = str(uuid.uuid4())
    guest_otp = frappe.new_doc("Guest OTP")
    guest_otp.mobile = mobile
    guest_otp.otp = otp
    guest_otp.expiry_timestamp = expiry_timestamp
    guest_otp.uuid = guest_otp_uuid
    guest_otp.insert()
    return {'status': WACheck.OTP_SENT.value, 'otp': {'expiry': expiry_timestamp, 'guest_otp_uuid': guest_otp_uuid}}

@frappe.whitelist()
def validate_otp(mobile, otp, guest_otp_uuid):
    print('Mobile: ',mobile)
    print('Provided OTP: ',otp)
    print('Guest OTP UUID: ', guest_otp_uuid)

    # Get stored token from DocType
    guest_otp = frappe.get_doc("Guest OTP", {"uuid": guest_otp_uuid})
    if not guest_otp:
        print('No OTP token found in DocType')
        return False

    # Verify the OTP using HMAC
    is_valid = verify_otp_token(mobile, otp, guest_otp.otp, guest_otp.otp)

    if is_valid:
        # Remove the token after successful validation
        guest_otp.delete()
        print('OTP validation successful')
        return True
    else:
        print('OTP validation failed')
        return False
def generate_otp():
    otp = ''.join(random.choices(string.digits, k=6))
    return otp
@frappe.whitelist(allow_guest=True)
def get_user(mobile):
    pass
@frappe.whitelist(allow_guest=True)
def signup_user(first_name, last_name, email, mobile):
    pass
def generate_username(length=10):
  """Generates a random username of specified length with lowercase letters and digits."""
  characters = string.ascii_lowercase + string.digits
  return ''.join(random.choice(characters) for _ in range(length)) + '@sravie.rewards'
def generate_password(length=8):
    """Generates a random password of specified length with lowercase letters, uppercase letters, digits, and special characters."""
    characters = string.ascii_lowercase + string.ascii_uppercase + string.digits + "!@#$%^&*"
    return ''.join(random.choice(characters) for _ in range(length))