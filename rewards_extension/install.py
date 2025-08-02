import frappe
import os
import json
from frappe.core.doctype.user.user import generate_keys

def after_install():
    create_app_roles()
    create_app_folders()


def create_app_roles():
    roles = [
        "Campaign Manager",
        "Manufacturer",
        "Consumer",
        "Sales Person"
    ]
    for role in roles:
        if not frappe.db.exists("Role", role):
            new_role = frappe.new_doc("Role")
            new_role.role_name = role
            new_role.desk_access = 0
            if role == "Campaign Manager":
                new_role.desk_access = 1
            if role == "Manufacturer":
                new_role.desk_access = 1
            #Only if role is "Manufacturer", allow desk access and for other roles no desk access
            new_role.insert(ignore_permissions=True)
    
    create_role_profiles()

def create_role_profiles():
    """Create default role profiles for the application"""
    profiles = [
        {
            "profile_name": "Consumer Profile",
            "roles": ["Consumer"]
        },
        {
            "profile_name": "Sales Person Profile",
            "roles": ["Sales Person"]
        },
        {
            "profile_name": "Distributor Profile",
            "roles": ["Consumer", "Sales Person"]
        },
        {
            "profile_name": "Manufacturer Profile",
            "roles": ["Campaign Manager"]
        }
    ]
    
    for profile in profiles:
        if not frappe.db.exists("Role Profile", profile["profile_name"]):
            role_profile = frappe.new_doc("Role Profile")
            role_profile.role_profile = profile["profile_name"]
            for role in profile["roles"]:
                role_profile.append("roles", {"role": role})
            role_profile.insert(ignore_permissions=True)

def create_app_folders():
    # Create folders with absolute paths to avoid timing issues
    frappe.call('frappe.core.api.file.create_new_folder', "Voucher Templates", "Home")
    
    # Create subfolders using absolute paths
    frappe.call('frappe.core.api.file.create_new_folder', "Website Popups", "Home/Voucher Templates")
    frappe.call('frappe.core.api.file.create_new_folder', "Instruction Thumbnails", "Home/Voucher Templates")
    frappe.call('frappe.core.api.file.create_new_folder', "Website Headers", "Home/Voucher Templates")
    frappe.call('frappe.core.api.file.create_new_folder', "Print Templates", "Home/Voucher Templates")
    
    frappe.call('frappe.core.api.file.create_new_folder', "Payout Images", "Home")
    frappe.call('frappe.core.api.file.create_new_folder', "Invoice Uploads", "Home")
