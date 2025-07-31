# Copyright (c) 2025, Vinod Kumar K and contributors
# For license information, please see license.txt

import frappe
import json
from frappe.model.document import Document
from frappe.utils import now

class GiftVoucher(Document):
	pass

@frappe.whitelist()
def validate_coupon_code_and_create_trail(coupon_code, user, campaign_id):
	# Validate coupon exists and is active
	voucher = frappe.get_value(
		"Gift Voucher",
		filters={"secret_code": coupon_code, "voucher_status": "Active","campaign": campaign_id},
		fieldname=["name", "secret_code", "campaign_target", "voucher_base_amount"]
	)
	if not voucher:
		return {
			"valid": False,
			"message": "Invalid coupon code or voucher is not active"
		}
	
	# Extract values from tuple
	voucher_name, secret_code, campaign_target, voucher_value = voucher
	
	# Create trail record
	trail = frappe.get_doc({
		"doctype": "Voucher Redeem Trail",
		"parent": voucher_name,
		"parenttype": "Gift Voucher",
		"parentfield": "trail",
		"user": user,
		"trail_datetime": now(),
		"trail_status": "Initiated"
	})
	trail.insert(ignore_permissions=True)
	trail.submit()
	
	return {
		"valid": True,
		"coupon_details": {
			"coupon_code": coupon_code,
			"voucher_name": voucher_name,
			"campaign_target": campaign_target,
			"voucher_value": voucher_value
		},
		"trail": {
			"trail_id": trail.name,
			"trail_datetime": trail.trail_datetime,
			"trail_status": trail.trail_status
		}
	}
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
def update_beneficiary_profile(profile,voucher):
	#update beneficiary_type and beneficiary fields of voucher doc
	pass