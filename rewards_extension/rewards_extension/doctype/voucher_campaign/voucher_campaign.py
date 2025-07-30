# Copyright (c) 2025, Vinod Kumar K and contributors
# For license information, please see license.txt

import frappe
import random
import string
from frappe.model.document import Document
from frappe.utils import nowdate


class VoucherCampaign(Document):
    def before_save(self):
        # Move files to custom folders if set
        if self.webpage_header_image:
            # Extract filename from path
            filename = self.webpage_header_image.split("/")[-1]
            
            # Define target folder path
            target_folder = "Home/Voucher Templates/Website Headers"
            target_path = f"{target_folder}/{filename}"
            
            # Skip if already in target folder
            if not self.webpage_header_image.startswith(target_folder):
                # Move file to target folder
                file_doc = frappe.get_doc("File", {"file_url": self.webpage_header_image})
                file_doc.folder = target_folder
                file_doc.save()
                
                # Update document field with new path
                self.webpage_header_image = target_path
                
        # Handle webpage_popup_image
        if self.webpage_popup_image:
            filename = self.webpage_popup_image.split("/")[-1]
            target_folder = "Home/Voucher Templates/Website Popups"
            target_path = f"{target_folder}/{filename}"
            
            if not self.webpage_popup_image.startswith(target_folder):
                file_doc = frappe.get_doc("File", {"file_url": self.webpage_popup_image})
                file_doc.folder = target_folder
                file_doc.save()
                self.webpage_popup_image = target_path
                
@frappe.whitelist()
def change_campaign_status(campaign:str,status:str):
    doc = frappe.get_doc("Voucher Campaign",campaign)
    doc.campaign_status=status
    doc.save()
    voucher_list = frappe.db.sql("""SELECT name FROM `tabGift Voucher` WHERE campaign=%s""",(campaign),as_dict=True)
    if status == 'Held' or status == 'Expired':
        disable_gift_vouchers([v['name'] for v in voucher_list])
    if status == 'Active':
        enable_gift_vouchers([v['name'] for v in voucher_list])
#Create a Voucher Batch and subsequent Vouchers
@frappe.whitelist()
def create_voucher_batch(campaign:str,count:int):
     campaign_doc = frappe.get_doc("Voucher Campaign",campaign)
     row = campaign_doc.append('voucher_batch',{})
     row.voucher_count=count
     row.save()
     row.batch_id = row.name
     row.save()
     #Create Gift Vouchers for this batch
     for i in range(count):
        voucher = frappe.new_doc("Gift Voucher")
        voucher.campaign=campaign
        voucher.campaign_target=campaign_doc.campaign_target
        voucher.batch_id=row.name
        voucher.voucher_base_amount=campaign_doc.base_voucher_price
        voucher.created_on=row.created_on
        voucher.valid_till=campaign_doc.end_date
        voucher.voucher_status='Generated'
        voucher.secret_code=generate_code()
        voucher.status='Active'
        voucher.voucher_print_template=campaign_doc.print_template
        voucher.insert(ignore_permissions=True)
        voucher.submit()
#Generates SECRET CODE for the Vouchers
def generate_code(length=6):
  """Generates a random code of specified length with uppercase letters and digits."""
  characters = string.ascii_uppercase + string.digits
  return ''.join(random.choice(characters) for _ in range(length))

#Enable gift vouchers
def enable_gift_vouchers(voucher_list:list):
    vouchers=[]
    for voucher in voucher_list:
      vouchr_doc = frappe.get_doc("Gift Voucher",voucher)
      if vouchr_doc.voucher_status=='Disabled':
          vouchr_doc.voucher_status='Active'
          vouchr_doc.save()
          vouchers.append(vouchr_doc.name)
    return vouchers
#Disable gift vouchers
def disable_gift_vouchers(voucher_list:list):
    vouchers=[]
    for voucher in voucher_list:
      vouchr_doc = frappe.get_doc("Gift Voucher",voucher)
      if vouchr_doc.voucher_status=='Generated' or vouchr_doc.voucher_status=='Active':
           vouchr_doc.voucher_status='Disabled'
           vouchr_doc.save()
           vouchers.append(vouchr_doc.name)
    return vouchers
def activate_gift_vouchers(voucher_list:list):
    vouchers=[]
    for voucher in voucher_list:
      vouchr_doc = frappe.get_doc("Gift Voucher",voucher)
      if vouchr_doc.voucher_status=='Generated':
          vouchr_doc.voucher_status='Active'
          vouchr_doc.activated_on=nowdate()
          vouchr_doc.save()
          vouchers.append(vouchr_doc.name)
    return vouchers
#Get all Batches pending activation
@frappe.whitelist()
def get_pending_batches(campaign):
    batches = frappe.db.sql("""SELECT * FROM `tabVoucher Batch` WHERE activated_on IS NULL AND frozen=0 AND parent=%s""",campaign, as_dict=True)
    #iterate on batches and prepare a list of batch names
    b_list=[]
    for batch in batches:
       b_list.append(batch.name)
    return b_list
#Activate Pending Batches
@frappe.whitelist()
def activate_pending_batch(batch,campaign):
    batch_doc = frappe.get_doc("Voucher Batch",batch)
    batch_doc.activated_on=nowdate()
    query = "SELECT name FROM `tabGift Voucher` WHERE batch_id='{a}'".format(a=batch,b=campaign)
    vouchers = frappe.db.sql(query,as_dict=True)
    activate_gift_vouchers([v['name'] for v in vouchers])
    batch_doc.save()
    return 'Success'