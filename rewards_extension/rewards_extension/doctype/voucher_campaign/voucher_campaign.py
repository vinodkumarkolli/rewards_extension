# Copyright (c) 2025, Vinod Kumar K and contributors
# For license information, please see license.txt

import frappe
import random
import string
from frappe import _
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
    result = {}
    if status == 'Held' or status == 'Expired':
        result = disable_gift_vouchers(voucher_list)
    if status == 'Active':
        result = enable_gift_vouchers(voucher_list)
    return result

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
            secret_code=generate_unique_code_for_campaign(campaign),
            status='Active'
        )
        voucher.insert(ignore_permissions=True)
        voucher.submit()
        voucher.add_comment('Edit', 'Voucher Status is changed to <b>Generated</b>')
#Generates SECRET CODE for the Vouchers
def generate_code(length=6):
  """Generates a random code of specified length with uppercase letters and digits."""
  characters = string.ascii_uppercase + string.digits
  return ''.join(random.choice(characters) for _ in range(length))

def is_code_unique_in_campaign(code, campaign):
  """Check if the generated code is unique within the specified campaign."""
  existing_vouchers = frappe.get_all("Gift Voucher",
                                      filters={"secret_code": code, "campaign": campaign},
                                      limit=1)
  return len(existing_vouchers) == 0

def generate_unique_code_for_campaign(campaign, length=6, max_attempts=100):
  """Generate a unique code for the specified campaign.
  
  Args:
      campaign (str): The campaign name to check uniqueness against
      length (int): Length of the code to generate
      max_attempts (int): Maximum number of attempts to generate a unique code
      
  Returns:
      str: A unique code for the campaign
      
  Raises:
      Exception: If unable to generate a unique code within max_attempts
  """
  for _ in range(max_attempts):
      code = generate_code(length)
      if is_code_unique_in_campaign(code, campaign):
          return code
  raise Exception(f"Unable to generate a unique code for campaign {campaign} after {max_attempts} attempts")

#Enable gift vouchers
def enable_gift_vouchers(voucher_list:list):
    if not voucher_list:
        return {"count": 0, "vouchers": []}
    
    # Get the list of vouchers that will actually be updated (those with voucher_status = "Disabled")
    vouchers_to_update = frappe.get_all("Gift Voucher",
                                       filters={"name": ("in", voucher_list), "voucher_status": "Disabled"},
                                       pluck="name")
    
    # For each disabled voucher, find the previous status from comments and revert to it
    for voucher_name in vouchers_to_update:
        voucher_doc = frappe.get_doc("Gift Voucher", voucher_name)
        
        # Get the previous status by looking at comment history
        previous_status = "Active"  # Default fallback
        
        # Get comments in chronological order (oldest first)
        comments = frappe.get_all("Comment",
                                 filters={"reference_doctype": "Gift Voucher", "reference_name": voucher_name, "comment_type": "Edit"},
                                 fields=["content"],
                                 order_by="creation asc")
        
        # Look for the last status change comment before the current "Disabled" status
        for comment in reversed(comments):  # Check newest comments first
            if "Voucher Status is changed to <b>Disabled</b>" in comment.content:
                continue  # Skip the current "Disabled" comment
            elif "Voucher Status is changed to <b>Active</b>" in comment.content:
                previous_status = "Active"
                break
            elif "Voucher Status is changed to <b>Generated</b>" in comment.content:
                previous_status = "Generated"
                break
        
        # Update the voucher status to the previous status
        voucher_doc.voucher_status = previous_status
        voucher_doc.save()
        frappe.db.commit()
        # Add comment about the status change
        voucher_doc.add_comment('Edit', f'Voucher Status is changed to <b>{previous_status}</b>')
    
    return {"count": len(vouchers_to_update), "vouchers": vouchers_to_update}

#Disable gift vouchers
def disable_gift_vouchers(voucher_list:list):
    if not voucher_list:
        return {"count": 0, "vouchers": []}
    vouchers_to_update = frappe.get_all("Gift Voucher",
                                       filters={"name": ("in", voucher_list), "voucher_status": ("in", ["Generated", "Active"])},
                                       pluck="name")
    frappe.db.set_value("Gift Voucher", {"name": ("in", voucher_list), "voucher_status": ("in", ["Generated", "Active"])}, "voucher_status", "Disabled")
    # Add comment to each Gift Voucher that was actually updated to "Disabled" status
    for voucher_name in vouchers_to_update:
        voucher_doc = frappe.get_doc("Gift Voucher", voucher_name)
        voucher_doc.add_comment('Edit', 'Voucher Status is changed to <b>Disabled</b>')
    return {"count": len(vouchers_to_update), "vouchers": vouchers_to_update}

def activate_gift_vouchers(voucher_list:list):
    if not voucher_list:
        return []
    # Get the list of vouchers that will actually be updated (those with voucher_status = "Generated")
    vouchers_to_update = frappe.get_all("Gift Voucher",
                                       filters={"name": ("in", voucher_list), "voucher_status": "Generated"},
                                       pluck="name")
    
    # Update the vouchers
    frappe.db.set_value("Gift Voucher", {"name": ("in", voucher_list), "voucher_status": "Generated"}, {"voucher_status": "Active", "activated_on": nowdate()})
    
    # Add comment to each Gift Voucher that was actually updated to "Active" status
    for voucher_name in vouchers_to_update:
        voucher_doc = frappe.get_doc("Gift Voucher", voucher_name)
        voucher_doc.add_comment('Edit', 'Voucher Status is changed to <b>Active</b>')
    
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

@frappe.whitelist()
def can_delete_campaign(campaign):
    """
    Check if all associated Gift Vouchers are in 'Disabled' status
    """
    # Get all gift vouchers for this campaign
    vouchers = frappe.get_all(
        "Gift Voucher",
        filters={"campaign": campaign},
        fields=["voucher_status"]
    )
    
    # Check if all vouchers are in 'Disabled' status
    for voucher in vouchers:
        if voucher.voucher_status != "Disabled":
            return False
    
    return True

@frappe.whitelist()
def delete_campaign(campaign):
    """
    Delete a campaign and all associated data
    """
    # First check if all vouchers are disabled
    if not can_delete_campaign(campaign):
        frappe.throw(_("Cannot delete campaign. Some vouchers are still active."))
    
    # Get all gift vouchers for this campaign
    voucher_names = frappe.get_all(
        "Gift Voucher",
        filters={"campaign": campaign},
        pluck="name"
    )
    
    # Cancel and delete all gift vouchers
    for voucher_name in voucher_names:
        voucher_doc = frappe.get_doc("Gift Voucher", voucher_name)
        if voucher_doc.docstatus == 1:  # Submitted
            voucher_doc.cancel()
        frappe.delete_doc("Gift Voucher", voucher_name, ignore_permissions=True)
    
    # Get the campaign document
    campaign_doc = frappe.get_doc("Voucher Campaign", campaign)
    
    # Cancel the campaign if it's submitted
    if campaign_doc.docstatus == 1:  # Submitted
        campaign_doc.cancel()
    
    # Delete the campaign itself (this will also delete associated voucher batches as they are child tables)
    frappe.delete_doc("Voucher Campaign", campaign, ignore_permissions=True)
    
    return "Campaign deleted successfully"
