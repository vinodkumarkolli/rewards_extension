# Copyright (c) 2025, Vinod Kumar K and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document


class CampaignInstruction(Document):
    def before_save(self):
        # Handle instruction_thumbnail
        if self.instruction_thumbnail:
            filename = self.instruction_thumbnail.split("/")[-1]
            target_folder = "Home/Voucher Templates/Instruction Thumbnails"
            target_path = f"{target_folder}/{filename}"
            
            if not self.instruction_thumbnail.startswith(target_folder):
                file_doc = frappe.get_doc("File", {"file_url": self.instruction_thumbnail})
                file_doc.folder = target_folder
                file_doc.save()
                self.instruction_thumbnail = target_path
