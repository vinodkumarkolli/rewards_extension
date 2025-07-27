import frappe
import os
import json
from frappe.core.doctype.user.user import generate_keys

def after_install():
    create_app_roles()
    create_app_folders()
    create_pwdless_user()

def create_pwdless_user():
    # Check if user already exists
    if not frappe.db.exists("User", "pwdless@sravie.in"):
        # Create user using Frappe's document creation method
        user_doc = frappe.get_doc({
            "doctype": "User",
            "email": "pwdless@sravie.in",
            "first_name": "Passwordless Tenant",
            "enabled": 1,
            "user_type": "Website User"
        })
        user_doc.insert(ignore_permissions=True)
        #Disable pwdless@sravie.in from becoming Administrator
        # Add Passwordless Helper role to the user
        user_doc.add_roles("Passwordless Helper")

        # Prevent pwdless@sravie.in from becoming Administrator
        roles_to_add = ["Passwordless Helper"]  # Start with the default role

        # Check if System Manager role exists and explicitly exclude it
        if frappe.db.exists("Role", "System Manager"):
            frappe.msgprint("System Manager role exists, but will not be added to pwdless@sravie.in")

        # Add roles to the user
        user_doc.add_roles(roles_to_add)

        # Generate API key and secret for the user
        keys_result = generate_keys("pwdless@sravie.in")

        # Get the API key from the user document
        api_key = frappe.db.get_value("User", "pwdless@sravie.in", "api_key")
        api_secret = keys_result.get("api_secret")

        # Save keys to bootuser.json file in vouchers module directory
        save_keys_to_env(api_key, api_secret, "pwdless@sravie.in")

        frappe.db.commit()
        frappe.msgprint(f"Created user 'pwdless@sravie.in' with API keys and saved to bootuser.json")
    else:
        frappe.msgprint("User 'pwdless@sravie.in' already exists")

def create_app_roles():
    roles = [
        "Passwordless Helper",
        "Campaign Manager",
        "Manufacturer",
        "Consumer",
        "Sales Person"
    ]
    for role in roles:
        if not frappe.db.exists("Role", role):
            new_role = frappe.new_doc("Role")
            new_role.role_name = role
            #Only if role is "Manufacturer", allow desk access and for other roles no desk access
            new_role.insert(ignore_permissions=True)

    # Set docperms for Passwordless Helper role
    if not frappe.db.exists("DocType", "User"):
        frappe.msgprint("User DocType does not exist. Please create it first.")
        return
    new_docperm = frappe.new_doc("DocPerm")
    new_docperm.parent = "User"
    new_docperm.parenttype = "DocType"
    new_docperm.parentfield = "permissions"
    new_docperm.role = "Passwordless Helper"
    new_docperm.permlevel = 0
    new_docperm.read = 1
    new_docperm.write = 1
    new_docperm.create = 1
    new_docperm.delete = 1
    new_docperm.submit = 0
    new_docperm.cancel = 0
    new_docperm.amend = 0
    new_docperm.ignore_user_permissions = 0
    new_docperm.apply_user_permissions = 0
    new_docperm.insert(ignore_permissions=True)

def create_app_folders():
    frappe.call('frappe.core.api.file.create_new_folder',"Voucher Templates","Home")
    frappe.call('frappe.core.api.file.create_new_folder',"Payout Images","Home")
    frappe.call('frappe.core.api.file.create_new_folder',"Invoice Uploads","Home")

def save_keys_to_env(api_key, api_secret, email):
    """Save API keys to bootuser.json file in vouchers module directory"""
    try:
        # Get the path to the vouchers module directory
        app_path = frappe.get_app_path("rewards_extension")
        vouchers_path = os.path.join(app_path, "..", "vouchers")
        env_file_path = os.path.join(vouchers_path, "bootuser.json")
        # Create the env content
        env_content = {
            "API_KEY": api_key,
            "API_SECRET": api_secret,
            "EMAIL": email
        }

        # Write to the file
        with open(env_file_path, 'w') as f:
            #clear content before writing new content
            json.dump(env_content, f, indent=4)

        frappe.msgprint(f"API keys saved to {env_file_path}")

    except Exception as e:
        frappe.log_error(f"Failed to save keys to bootuser.json: {str(e)}")
        frappe.msgprint(f"Warning: Could not save keys to bootuser.json - {str(e)}")