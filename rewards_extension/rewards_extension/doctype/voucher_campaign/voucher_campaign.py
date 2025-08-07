# Copyright (c) 2025, Vinod Kumar K and contributors
# For license information, please see license.txt

import frappe
import random
import string
from frappe.model.document import Document
from frappe.utils import nowdate


class VoucherCampaign(Document):
	def before_submit(self):
		for instruction in frappe.get_all("Campaign Instruction", filters={"parent": self.name, "parenttype": "Voucher Campaign"}, fields=["instruction_thumbnail"]):
			if instruction.instruction_thumbnail:
				filename = instruction.instruction_thumbnail.split("/")[-1]
				target_folder = "Home/Voucher Templates/Instruction Thumbnails"
				target_path = f"{target_folder}/{filename}"
				
				if not instruction.instruction_thumbnail.startswith(target_folder):
					file_doc = frappe.get_doc("File", {"file_url": instruction.instruction_thumbnail})
					file_doc.folder = target_folder
					file_doc.save()
					frappe.db.set_value("Campaign Instruction", instruction.name, "instruction_thumbnail", target_path)
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


@frappe.whitelist()
def expire_old_campaigns():
    """
    Expire campaigns where campaign_status is 'Active' 
    and end_date has passed
    """
    today = frappe.utils.nowdate()
    
    # Get all expired campaigns
    expired_campaigns = frappe.get_all(
        "Voucher Campaign",
        filters={
            "campaign_status": "Active",
            "end_date": ["<", today]
        },
        fields=["name"]
    )
    
    # Update status to 'Expired'
    for campaign in expired_campaigns:
        doc = frappe.get_doc("Voucher Campaign", campaign.name)
        doc.campaign_status = "Expired"
        doc.save(ignore_permissions=True)
        doc.add_comment('Edit', f"The Voucher Campaign expired on {today}")
        
    frappe.logger().info(f"Expired {len(expired_campaigns)} voucher campaigns")
