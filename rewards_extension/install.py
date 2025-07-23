import frappe;
def after_install():
    create_app_folders()

def create_app_folders():
    frappe.call('frappe.core.api.file.create_new_folder',"Voucher Templates","Home")
    frappe.call('frappe.core.api.file.create_new_folder',"Payout Images","Home")
    frappe.call('frappe.core.api.file.create_new_folder',"Invoice Uploads","Home")