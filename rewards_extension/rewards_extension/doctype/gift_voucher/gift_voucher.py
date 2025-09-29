# Copyright (c) 2025, Vinod Kumar K and contributors
# For license information, please see license.txt

import frappe
import json
from frappe.model.document import Document
from frappe.utils import now

class GiftVoucher(Document):
	pass

@frappe.whitelist()
def validate_coupon_code_and_create_trail(coupon_code, user, campaign_id, profile):
	# Validate coupon exists and is active
	if isinstance(profile, str):
		redeemer_profile = json.loads(profile)
	else:
		redeemer_profile = profile
	voucher_name = frappe.db.get_value(
		"Gift Voucher",
		filters={"secret_code": coupon_code, "voucher_status": ["in",["Active","Blocked"]], "campaign": campaign_id},
		fieldname="name",
	)
	if not voucher_name:
		# The original implementation returned a dict. Throwing an exception is cleaner
		# and can be caught by the frontend call, which has a try-catch block.
		return {'valid': False, 'message': 'Invalid Coupon Code'}

	voucher_doc = frappe.get_doc("Gift Voucher", voucher_name)
	campaign_doc = frappe.get_doc("Voucher Campaign", campaign_id)

	if voucher_doc.voucher_status == "Active":
		comment = f"{user} has blocked the present voucher ({voucher_doc.name}) to his profile on {now()}"
		voucher_doc.add_comment("Info", comment)
		customer_type = redeemer_profile.get("customer_type")
		# Map customer_type to beneficiary_type using switch-like logic
		beneficiary_type = {
        "Retailer": "Customer Profile",
		"Wholesaler": "Customer Profile",
		"Consumer": "Customer Profile",
        "Distributor": "Distributor Profile",
        "Sales Person": "Sales Person Profile"
		}.get(customer_type, customer_type)  # Default to original if not found
		voucher_doc.beneficiary_type = beneficiary_type
		voucher_doc.save(ignore_permissions=True)
		voucher_doc.beneficiary = redeemer_profile.get("customer_name")
		voucher_doc.voucher_status = "Blocked"
		voucher_doc.blocked_date = now()
		voucher_doc.blocked_by_user = user
		voucher_doc.voucher_trails = voucher_doc.voucher_trails + 1
		voucher_doc.save(ignore_permissions=True)
		comment = f"{redeemer_profile.get('customer_name')} of type {redeemer_profile.get('customer_type')} is allocated this voucher"
		voucher_doc.add_comment('Edit',comment)
		return {
			"valid": True,
			"coupon_details": {
				"coupon_code": voucher_doc.secret_code,
				"voucher_name": voucher_doc.name,
				"campaign_target": voucher_doc.campaign_target,
				"voucher_value": voucher_doc.voucher_base_amount,
				"beneficiary_type": voucher_doc.beneficiary_type,
				"beneficiary": voucher_doc.beneficiary,
				"doctype":voucher_doc.doctype,
				"voucher_base_amount":voucher_doc.voucher_base_amount,
			}
		}
	if (voucher_doc.voucher_status == "Blocked") and (voucher_doc.voucher_trails <= campaign_doc.voucher_retries):
		comment = f"{user} has retried for - {voucher_doc.name} voucher. Time: {now()}"
		voucher_doc.add_comment("Info", comment)
		# voucher_doc.blocked_by_user = user
		voucher_doc.voucher_trails = voucher_doc.voucher_trails + 1
		voucher_doc.save(ignore_permissions=True)
		frappe.db.commit()
		if voucher_doc.blocked_by_user == user:
			return {
				"valid": True,
				"coupon_details": {
					"coupon_code": voucher_doc.secret_code,
					"voucher_name": voucher_doc.name,
					"campaign_target": voucher_doc.campaign_target,
					"voucher_value": voucher_doc.voucher_base_amount,
					"beneficiary_type": voucher_doc.beneficiary_type,
					"beneficiary": voucher_doc.beneficiary,
					"doctype":voucher_doc.doctype,
					"voucher_base_amount":voucher_doc.voucher_base_amount,
				}
			}
		else:
			return {
				"valid": False,
				"message": 'You cannot use this Voucher. This is blocked by another user'
			}
	else:
		return {
			"valid": False,
			"message": 'Voucher has been tried too many times. And Blocked. Try another Coupon'
		}
@frappe.whitelist()
def fraud_analysis(beneficiary_type,beneficiary,user):
	pass

@frappe.whitelist()
def get_all_customer_profiles():
	"""
	Fetches all Customer Profile documents with their name and customer_name fields.
	Returns a list of Customer Profile documents.
	"""
	profiles = frappe.get_all("Customer Profile", fields=["name", "customer_name", "modified","customer_type"])
	return profiles

@frappe.whitelist()
def link_customer_profile_to_user(profile_name, user):
	"""
	Links a Customer Profile to a User by adding the user to the profile's User Mapping table.
	"""
	try:
		profile = frappe.get_doc("Customer Profile", profile_name)
		
		# Check if user is already linked to this profile
		for user_mapping in profile.users:
			if user_mapping.user == user:
				return {"success": True, "message": "User already linked to this profile", "profile": profile.as_dict()}
		
		# Add user to the profile's User Mapping table
		profile.append("users", {
			"user": user
		})
		profile.save(ignore_permissions=True)
		
		return {"success": True, "message": "Profile linked successfully", "profile": profile.as_dict()}
	except Exception as e:
		frappe.log_error(f"Error linking profile {profile_name} to user {user}: {str(e)}")
		return {"success": False, "message": str(e)}

@frappe.whitelist()
def search_customer_profile_for_contact(user):
	"""
	Searches for a Customer Profile linked to the given user via the 'User Mapping' child table.
	Returns the Customer Profile document if found, otherwise None.
	"""
	customer_profile_name = frappe.db.get_value("User Mapping", {"user": user}, "parent")

	if customer_profile_name:
		return frappe.get_doc("Customer Profile", customer_profile_name)

	return None

#customer_data is a json or serialised json (that is supported in function call). It contains address, customer_name, customer_type
#profile_source will always be 'Gift Voucher' and profile_source_link is passed in voucher argument
@frappe.whitelist()
def create_customer_profile(customer_data, user):
	"""
	Creates a new Customer Profile and a linked Address from the provided data.
	customer_data is a dict with customer_name, customer_type, and address details.
	voucher is the name of the Gift Voucher document.
	user is the user to be linked in the profile.
	"""
	if isinstance(customer_data, str):
		customer_data = json.loads(customer_data)

	address_data = customer_data.get("address", {})

	# Create Address document
	address = frappe.get_doc({
		"doctype": "Address",
		"address_title": customer_data.get("customer_name"),
		"address_type": "Billing",
		"address_line1": address_data.get("address_line1"),
		"address_line2": address_data.get("locality"),
		"city": address_data.get("city"),
		"pincode": address_data.get("pincode"),
		"country": frappe.db.get_default("country") or "India"
	}).insert(ignore_permissions=True)

	# Create Customer Profile document
	profile = frappe.get_doc({
		"doctype": "Customer Profile",
		"customer_name": customer_data.get("customer_name"),
		"customer_type": customer_data.get("customer_type"),
		"address": address.name,
		"users": [{"user": user}]
	}).insert(ignore_permissions=True)
	
	# Add dynamic link from Address to Customer Profile
	address.append("links", {
		"link_doctype": "Customer Profile",
		"link_name": profile.name
	})
	address.save(ignore_permissions=True)
	return profile.as_dict()

@frappe.whitelist()
def update_redemption_details(voucher_name,redeem_details,user):
	voucher_doc = frappe.get_doc("Gift Voucher", voucher_name)
	voucher_doc.payout_mode = redeem_details.get("payout_mode")
	voucher_doc.settlement_amount = redeem_details.get("settlement_amount")
	if redeem_details.get("payout_mode") == "UPI ID":
		voucher_doc.beneficiary_upi_details = redeem_details.get("upi_id")
	if redeem_details.get("payout_mode") == "GPAY":
		voucher_doc.beneficiary_upi_details = redeem_details.get("gpay_number")
	voucher_doc.save(ignore_permissions=True)
	comment = f"{user} has submitted his payment details to redeem this voucher for a Settlement Amount of {voucher_doc.settlement_amount} and Payout Mode: {redeem_details.get('payout_mode')} & Details: {voucher_doc.beneficiary_upi_details}"
	voucher_doc.add_comment('Edit',comment)
	payout_result = create_payout_doc(voucher_doc)
	if payout_result.get('status') == 'success':
		voucher_doc.voucher_status = "Payout Requested"
		voucher_doc.save(ignore_permissions=True)
		comment1 = f"{payout_result.get('payout').name} - payout request has been created for this voucher"
		voucher_doc.add_comment('Edit',comment1)
		return {'status':'success'}
	else:
		return {'status':'failed', 'message': 'Payout creation failed'}

@frappe.whitelist()
def create_payout_doc(voucher_doc):
	try:
		payout_doc = frappe.get_doc({
			"doctype": "Payout",
			"payout_amount":voucher_doc.settlement_amount,
			"payout_mode": voucher_doc.payout_mode,
			"beneficiary_type": voucher_doc.beneficiary_type,
			"beneficiary": voucher_doc.beneficiary,
			"beneficiary_details": voucher_doc.beneficiary_upi_details,
			"payout_source_type":voucher_doc.doctype,
			"payout_source_link":voucher_doc.name,
			"payout_date": now(),
			"payout_status":"Under Process"
		})
		payout_doc.insert(ignore_permissions=True)
		payout_doc.submit()
		return {'status':'success','payout':payout_doc}
	except Exception as e:
		frappe.log_error(f"Payout creation failed for voucher {voucher_doc.name}: {str(e)}")
		return {'status':'failed', 'message': str(e)}
	

@frappe.whitelist()
def expire_old_vouchers():
    """
    Expire vouchers where voucher_status is 'Active' or 'Generated' 
    and valid_till date has passed
    """
    today = frappe.utils.nowdate()
    
    # Get all expired vouchers
    expired_vouchers = frappe.get_all(
        "Gift Voucher",
        filters={
            "voucher_status": ["in", ["Active", "Generated"]],
            "valid_till": ["<", today]
        },
        fields=["name"]
    )
    
    # Update status to 'Expired'
    for voucher in expired_vouchers:
        voucher_doc = frappe.get_doc("Gift Voucher", voucher.name)
        voucher_doc.voucher_status = "Expired"
        voucher_doc.save(ignore_permissions=True)
        voucher_doc.add_comment('Comment', f'Voucher Expired on {now()}')
        frappe.db.commit()
        
    frappe.logger().info(f"Expired {len(expired_vouchers)} gift vouchers")
