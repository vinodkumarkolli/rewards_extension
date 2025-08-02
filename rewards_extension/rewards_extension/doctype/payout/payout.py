# Copyright (c) 2025, Vinod Kumar K and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document


class Payout(Document):
	pass

@frappe.whitelist()
def approve_payout(payout_id,trx_id,trx_amt,trx_date,trx_image):
	payout_doc = frappe.get_doc("Payout",payout_id)
	payout_doc.transaction_id = trx_id
	payout_doc.transaction_amount = trx_amt
	payout_doc.transaction_date = trx_date
	payout_doc.transaction_image = trx_image
	payout_doc.payout_status = "Processed"
	payout_doc.save(ignore_permissions=True)
	frappe.db.commit()
	return "Success"


@frappe.whitelist()
def reject_payout(payout_id):
	pass

@frappe.whitelist()
def hold_payout(payout_id):
	pass