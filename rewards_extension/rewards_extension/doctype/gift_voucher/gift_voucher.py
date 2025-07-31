# Copyright (c) 2025, Vinod Kumar K and contributors
# For license information, please see license.txt

import frappe
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
