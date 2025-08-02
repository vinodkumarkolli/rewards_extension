# Copyright (c) 2025, Vinod Kumar K and contributors
# For license information, please see license.txt

import frappe
import random
import string
from frappe.model.document import Document
from frappe.utils import nowdate


class VoucherCampaign(Document):
	def before_save(self):
		self.webpage_header_image = self._move_file(
			self.webpage_header_image, "Home/Voucher Templates/Website Headers"
		)
		# self.webpage_popup_image = self._move_file(
		# 	self.webpage_popup_image, "Home/Voucher Templates/Website Popups"
		# )

	def _move_file(self, file_path, target_folder):
		if not file_path or file_path.startswith(target_folder):
			return file_path

		try:
			file_doc = frappe.get_doc("File", {"file_url": file_path})
			filename = file_path.split("/")[-1]
			target_path = f"/{target_folder}/{filename}"

			file_doc.folder = target_folder
			file_doc.save()

			return target_path
		except frappe.DoesNotExistError:
			frappe.log_error(f"File not found for path: {file_path}", "Voucher Campaign File Move")
			return file_path

@frappe.whitelist()
def change_campaign_status(campaign:str,status:str):
    doc = frappe.get_doc("Voucher Campaign",campaign)
    doc.campaign_status=status
    doc.save()
    voucher_list = frappe.get_all("Gift Voucher", filters={"campaign": campaign}, pluck="name")
    if status == 'Held' or status == 'Expired':
        disable_gift_vouchers(voucher_list)
    if status == 'Active':
        enable_gift_vouchers(voucher_list)

#Create a Voucher Batch and subsequent Vouchers
@frappe.whitelist()
def create_voucher_batch(campaign:str,count:int):
     campaign_doc = frappe.get_doc("Voucher Campaign",campaign)
     row = campaign_doc.append('voucher_batch',{
         "voucher_count": count
     })
     row.save()
     row.batch_id = row.name
     row.save()
     #Create Gift Vouchers for this batch
     for i in range(count):
        voucher = frappe.new_doc("Gift Voucher",
            campaign=campaign,
            campaign_target=campaign_doc.campaign_target,
            batch_id=row.name,
            voucher_base_amount=campaign_doc.base_voucher_price,
            created_on=row.created_on,
            valid_till=campaign_doc.end_date,
            voucher_status='Generated',
            secret_code=generate_code(),
            status='Active'
        )
        voucher.insert(ignore_permissions=True)
        voucher.submit()
#Generates SECRET CODE for the Vouchers
def generate_code(length=6):
  """Generates a random code of specified length with uppercase letters and digits."""
  characters = string.ascii_uppercase + string.digits
  return ''.join(random.choice(characters) for _ in range(length))

#Enable gift vouchers
def enable_gift_vouchers(voucher_list:list):
    if not voucher_list:
        return []
    frappe.db.set_value("Gift Voucher", {"name": ("in", voucher_list), "voucher_status": "Disabled"}, "voucher_status", "Active")
    return voucher_list

#Disable gift vouchers
def disable_gift_vouchers(voucher_list:list):
    if not voucher_list:
        return []
    frappe.db.set_value("Gift Voucher", {"name": ("in", voucher_list), "voucher_status": ("in", ["Generated", "Active"])}, "voucher_status", "Disabled")
    return voucher_list

def activate_gift_vouchers(voucher_list:list):
    if not voucher_list:
        return []
    frappe.db.set_value("Gift Voucher", {"name": ("in", voucher_list), "voucher_status": "Generated"}, {"voucher_status": "Active", "activated_on": nowdate()})
    return voucher_list

#Get all Batches pending activation
@frappe.whitelist()
def get_pending_batches(campaign):
    return frappe.get_all(
        "Voucher Batch",
        filters={"activated_on": ("is", "not set"), "frozen": 0, "parent": campaign},
        pluck="name"
    )

#Activate Pending Batches
@frappe.whitelist()
def activate_pending_batch(batch,campaign):
    frappe.db.set_value("Voucher Batch", batch, "activated_on", nowdate())

    vouchers = frappe.get_all(
        "Gift Voucher",
        filters={"batch_id": batch, "campaign": campaign},
        pluck="name"
    )

    if vouchers:
        activate_gift_vouchers(vouchers)

    return 'Success'