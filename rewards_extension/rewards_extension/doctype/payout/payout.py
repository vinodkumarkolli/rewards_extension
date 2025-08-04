# Copyright (c) 2025, Vinod Kumar K and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe.utils import now

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
	source_doc = frappe.get(payout_doc.payout_source_type,payout_doc.payout_source_link)
	source_doc.voucher_status = "Redeemed"
	source_doc.redeemed_date = now()
	source_doc.save(ignore_permissions=True)
	source_doc.add_comment('Comment', f'Voucher Redeemed on {payout_doc.transaction_date}')
	frappe.db.commit()
	return "Success"


@frappe.whitelist()
def reject_payout(payout_id):
	pass

@frappe.whitelist()
def hold_payout(payout_id):
	pass