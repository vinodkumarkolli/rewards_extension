import frappe
from frappe.utils import cint
import random
from frappe.rate_limiter import rate_limit
from frappe.auth import LoginManager
from frappe import _
import hmac
import hashlib
import json
import base64
import time
import requests  # Added for WhatsApp API

# Simple in-memory session storage as fallback for guest users
SESSION_CACHE = {}
@frappe.whitelist(allow_guest=True)
@rate_limit(key="mobile_no", limit=5, seconds=60 * 5)  # Rate limit to 5 requests per 5 mins per mobile number
def send_login_otp(mobile_no: str):
	"""
	Sends an OTP to the user's mobile number for passwordless login.
	"""
	if not mobile_no:
		frappe.throw(_("Mobile number is required."))

	# Find user by mobile number
	user = frappe.db.get_value("User", {"mobile_no": mobile_no, "enabled": 1}, "name")

	if not user:
		# Instead of throwing error, return specific status for frontend handling
		return {"status": "user_not_found", "message": "User with this mobile number not found."}

	# Generate a 6-digit OTP
	otp = ''.join(random.choices('0123456789', k=6))

	# Generate a temporary ID to link this request with the verification request
	tmp_id = frappe.generate_hash(length=12)

	# Generate HMAC-signed token
	token_data = {"user": user, "otp": otp}
	token = generate_hmac_token(token_data)
	
	# Store session data in cache (5 minute expiration)
	expiration = time.time() + 300  # 5 minutes
	SESSION_CACHE[tmp_id] = {"token": token, "expiration": expiration}

	# Send OTP via WhatsApp
	if not send_whatsapp_otp(mobile_no, otp, "login"):
		frappe.log_error(f"Failed to send WhatsApp OTP to {mobile_no}", "WhatsApp OTP Error")

	# Send the temporary ID back to the client
	return {"status": "success", "tmp_id": tmp_id, "message": "OTP sent successfully."}

@frappe.whitelist(allow_guest=True)
@rate_limit(key="mobile_no", limit=5, seconds=60 * 5)
def signup(first_name: str, last_name: str, company_name: str, mobile_no: str, email: str, role_profile_name):
	"""
	Handles new user signup and sends OTP for verification
	"""
	if not all([first_name, last_name, mobile_no, email]):
		frappe.throw(_("First Name, Last Name, Mobile Number and Email are required for signup."))
	
	# Check if user already exists
	if frappe.db.exists("User", {"mobile_no": mobile_no}):
		frappe.throw(_("User with this mobile number already exists."))
	
	if frappe.db.exists("User", {"email": email}):
		frappe.throw(_("User with this email already exists."))
	
	# Create new user
	user = frappe.get_doc({
		"doctype": "User",
		"first_name": first_name,
		"last_name": last_name,
		"company_name": company_name,
		"mobile_no": mobile_no,
		"email": email,
		"enabled": 1,
		"send_welcome_email": 0,
		"role_profile_name":role_profile_name
	})
	user.insert(ignore_permissions=True)
	
	# Generate and send OTP
	otp = ''.join(random.choices('0123456789', k=6))
	tmp_id = frappe.generate_hash(length=12)
	# Generate HMAC-signed token
	token_data = {"user": user.name, "otp": otp}
	token = generate_hmac_token(token_data)
	
	# Store session data in cache (5 minute expiration)
	expiration = time.time() + 300  # 5 minutes
	SESSION_CACHE[tmp_id] = {"token": token, "expiration": expiration}
	
	# Send OTP via WhatsApp
	if not send_whatsapp_otp(mobile_no, otp, "signup"):
		frappe.log_error(f"Failed to send WhatsApp OTP to {mobile_no}", "WhatsApp OTP Error")
	
	return {"status": "success", "tmp_id": tmp_id, "message": "Account created. OTP sent to your mobile."}


@frappe.whitelist(allow_guest=True)
@rate_limit(key="tmp_id", limit=10, seconds=60 * 5) # Allow more verification attempts
def verify_login_otp(tmp_id: str, otp: str):
    """
    Verifies the OTP and logs the user in if it's correct.
    Allows multiple attempts without invalidating the session.
    """
    if not (tmp_id and otp):
        frappe.throw(_("Temporary ID and OTP are required."))

    # Retrieve token from cache
    if tmp_id not in SESSION_CACHE or time.time() > SESSION_CACHE[tmp_id]["expiration"]:
        frappe.throw(_("Login request expired. Please try again."))
    
    token = SESSION_CACHE[tmp_id]["token"]
    cached_data = verify_hmac_token(token)

    # Only clean up cache on success
    if str(cached_data.get("otp")) != str(otp):
        frappe.throw(_("Invalid OTP. Please try again."))

    # OTP is correct, log the user in
    frappe.local.login_manager = LoginManager()
    frappe.local.login_manager.login_as(cached_data.get("user"))

    # Clean up cache on success
    if tmp_id in SESSION_CACHE:
        del SESSION_CACHE[tmp_id]

    # Get user details to include in response
    user_doc = frappe.get_doc("User", cached_data.get("user"))
    return {
        "status": "success",
        "message": "Login successful.",
        "first_name": user_doc.first_name,
        "mobile_no": user_doc.mobile_no,
        "default_route": "/"
    }

def generate_hmac_token(data: dict) -> str:
	"""Generate HMAC-signed token for session storage"""
	# Get secret from configuration with fallback
	secret = frappe.local.conf.get("hmac_secret") or frappe.local.conf.secret_key
	
	# Use Frappe's encryption key if both are missing
	if not secret:
		from frappe.utils.password import get_encryption_key
		secret = get_encryption_key()
		
	if not secret:
		frappe.throw(_("System configuration error: Missing HMAC secret key"))
		
	data_json = frappe.as_json(data).encode()
	signature = hmac.new(secret.encode(), data_json, hashlib.sha256).hexdigest()
	payload = base64.b64encode(data_json).decode()
	return f"{payload}.{signature}"

def verify_hmac_token(token: str) -> dict:
	"""Verify HMAC token and return data if valid"""
	try:
		payload, signature = token.split('.')
		
		# Get secret from configuration with fallback
		secret = frappe.local.conf.get("hmac_secret") or frappe.local.conf.secret_key
		
		# Use Frappe's encryption key if both are missing
		if not secret:
			from frappe.utils.password import get_encryption_key
			secret = get_encryption_key()
			
		if not secret:
			frappe.throw(_("System configuration error: Missing HMAC secret key"))
			
		data_json = base64.b64decode(payload.encode())
		expected_signature = hmac.new(secret.encode(), data_json, hashlib.sha256).hexdigest()
		
		if not hmac.compare_digest(expected_signature, signature):
			frappe.throw(_("Invalid token signature."))
			
		return frappe.parse_json(data_json.decode())
	except Exception as e:
		frappe.log_error(f"Token verification failed: {str(e)}")
		frappe.throw(_("Invalid token format."))
		
def decode_mobile_from_email(email):
	"""
	Decodes mobile number from specially formatted email addresses
	Format: u_<base64_encoded_mobile>@sravie.in
	"""
	if not email or "@sravie.in" not in email:
		return None
		
	try:
		# Extract base64 portion
		encoded = email.split("@")[0]
		if not encoded.startswith("u_"):
			return None
			
		# Decode and return mobile number
		encoded = encoded[2:]
		# Add padding if needed
		padding = 4 - (len(encoded) % 4)
		if padding < 4:
			encoded += "=" * padding
		return base64.b64decode(encoded).decode()
	except Exception as e:
		frappe.log_error(f"Email decoding failed: {str(e)}")
		return None

def send_whatsapp_otp(mobile_no, otp, purpose):
	"""Send OTP via WhatsApp API securely without logging sensitive data"""
	# Get API configuration from environment
	api_url = frappe.conf.get("whatsapp_api_url")
	api_version = frappe.conf.get("whatsapp_api_version")
	access_token = frappe.conf.get("whatsapp_access_token")
	phone_number_id = frappe.conf.get("wa_phone_number_id")
	template_name = frappe.conf.get("wa_login_otp_template")
	
	if not all([api_url, api_version, access_token, phone_number_id, template_name]):
		frappe.log_error("WhatsApp configuration incomplete", "WhatsApp Config Error")
		return False
	
	try:
		# Construct API endpoint
		url = f"{api_url}/{api_version}/{phone_number_id}/messages"
		
		# Prepare request data
		headers = {
			"Authorization": f"Bearer {access_token}",
			"Content-Type": "application/json"
		}
		
		# # Convert OTP to base36 to shorten the URL parameter
		# import base64
		# base36_otp = base64.b36encode(str(otp).encode()).decode()
		
		payload = {
			"messaging_product": "whatsapp",
			"to": mobile_no,
			"type": "template",
			"template": {
				"name": template_name,
				"language": {"code": "en"},
				"components": [
					{
						"type": "BODY",
						"parameters": [
							{"type": "text", "text": otp}
						]
					},
					{
						"type": "BUTTON",
						"sub_type": "url",
						"index": 0,
						"parameters": [
							{"type": "text", "text": f"{otp}"}
						]
					}
				]
			}
		}
		
		# Send request
		response = requests.post(url, headers=headers, json=payload)
		response.raise_for_status()
		
		# Log successful send without sensitive data
		frappe.logger().info(f"WhatsApp OTP sent to {mobile_no} for {purpose}")
		return True
	except Exception as e:
		frappe.log_error(
			f"WhatsApp API error: {str(e)}",
			"WhatsApp API Error"
		)
		return False
