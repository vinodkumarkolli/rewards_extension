import frappe
from frappe.utils import random_string, cint
from frappe.rate_limiter import rate_limit
from frappe.auth import LoginManager
from frappe import _


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
	otp = random_string(6, "1234567890")

	# Generate a temporary ID to link this request with the verification request
	tmp_id = frappe.generate_hash(length=12)

	# Cache the OTP and user details with the temporary ID, expiring in 5 minutes (300 seconds)
	cache_key = f"passwordless_otp_{tmp_id}"
	frappe.cache().set(cache_key, {"user": user, "otp": otp}, 300)
	print('Mobile No: ', mobile_no)
	print('OTP: ', otp)
	print('User: ', user)
	# Send OTP via SMS using Requests
	try:
		import requests
		sms_response = requests.post(
			"https://api.smsprovider.com/send",
			json={
				"api_key": frappe.conf.sms_api_key,
				"recipient": mobile_no,
				"message": f"Your login OTP is {otp}"
			},
			timeout=5
		)
		if sms_response.status_code != 200:
			frappe.log_error(f"SMS sending failed: {sms_response.text}", "SMS Error")
	except Exception as e:
		frappe.log_error(f"SMS sending error: {str(e)}", "SMS Exception")
	# For testing, log the OTP
	frappe.log_error(f"Passwordless Login OTP for {mobile_no} ({user}): {otp}", "OTP Log")

	# Send the temporary ID back to the client
	return {"status": "success", "tmp_id": tmp_id, "message": "OTP sent successfully."}

@frappe.whitelist(allow_guest=True)
@rate_limit(key="mobile_no", limit=5, seconds=60 * 5)
def signup(first_name: str, last_name: str, company_name: str, mobile_no: str, email: str):
	"""
	Handles new user signup and sends OTP for verification
	"""
	if not all([first_name, last_name, company_name, mobile_no, email]):
		frappe.throw(_("All fields are required for signup."))
	
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
		"roles": [{"role": "Customer"}]
	})
	user.insert(ignore_permissions=True)
	
	# Generate and send OTP
	otp = random_string(6, "1234567890")
	tmp_id = frappe.generate_hash(length=12)
	cache_key = f"passwordless_otp_{tmp_id}"
	frappe.cache().set(cache_key, {"user": user.name, "otp": otp}, 300)
	
	# Send OTP via SMS using Requests
	try:
		import requests
		sms_response = requests.post(
			"https://api.smsprovider.com/send",
			json={
				"api_key": frappe.conf.sms_api_key,
				"recipient": mobile_no,
				"message": f"Your signup OTP is {otp}"
			},
			timeout=5
		)
		if sms_response.status_code != 200:
			frappe.log_error(f"SMS sending failed: {sms_response.text}", "SMS Error")
	except Exception as e:
		frappe.log_error(f"SMS sending error: {str(e)}", "SMS Exception")
	# For testing, log the OTP
	frappe.log_error(f"Signup OTP for {mobile_no} ({user.name}): {otp}", "OTP Log")
	
	return {"status": "success", "tmp_id": tmp_id, "message": "Account created. OTP sent to your mobile."}


@frappe.whitelist(allow_guest=True)
@rate_limit(key="tmp_id", limit=10, seconds=60 * 5) # Allow more verification attempts
def verify_login_otp(tmp_id: str, otp: str):
	"""
	Verifies the OTP and logs the user in if it's correct.
	"""
	if not (tmp_id and otp):
		frappe.throw(_("Temporary ID and OTP are required."))

	cache_key = f"passwordless_otp_{tmp_id}"
	cached_data = frappe.cache().get(cache_key)

	if not cached_data:
		frappe.throw(_("Login request expired. Please try again."))

	if str(cached_data.get("otp")) != str(otp):
		frappe.throw(_("Invalid OTP."))

	# OTP is correct, log the user in
	frappe.local.login_manager = LoginManager()
	frappe.local.login_manager.login_as(cached_data.get("user"))

	# Clean up the cache
	frappe.cache().delete_key(cache_key)

	return {"status": "success", "message": "Login successful."}