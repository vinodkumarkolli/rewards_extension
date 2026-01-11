import frappe
import os
import json
from frappe.core.doctype.user.user import generate_keys
from frappe.permissions import add_permission, update_permission_property

def after_install():
    create_app_roles()
    create_app_folders()
    create_module_profiles()
    setup_permissions()
    assign_module_profile()
    
    if frappe.db.exists("Role", "Campaign Viewer"):
        print("SUCCESS: Campaign Viewer role verified in DB.")
    else:
        print("ERROR: Campaign Viewer role NOT found in DB after creation!")


def create_app_roles():
    print("Creating App Roles...")
    roles = [
        "Campaign Manager",
        "Manufacturer",
        "Consumer",
        "Sales Person",
        "Campaign Viewer"
    ]
    for role in roles:
        if not frappe.db.exists("Role", role):
            print(f"Creating role: {role}")
            new_role = frappe.new_doc("Role")
            new_role.role_name = role
            new_role.desk_access = 0
            if role in ["Campaign Manager", "Manufacturer", "Campaign Viewer"]:
                new_role.desk_access = 1
            new_role.insert(ignore_permissions=True)
        else:
            print(f"Role exists: {role}")
            # Ensure desk_access is correct even if role exists
            if role in ["Campaign Manager", "Manufacturer", "Campaign Viewer"]:
                doc = frappe.get_doc("Role", role)
                if not doc.desk_access:
                    print(f"Updating desk_access for {role}")
                    doc.desk_access = 1
                    doc.save(ignore_permissions=True)
    
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
    folders = [
        ("Voucher Templates", "Home"),
        ("Instruction Thumbnails", "Home/Voucher Templates"),
        ("Website Headers", "Home/Voucher Templates"),
        ("Print Templates", "Home/Voucher Templates"),
        ("Payout Images", "Home"),
        ("Invoice Uploads", "Home"),
        ("Sales Records Uploads", "Home")
    ]
    
    for folder, parent in folders:
        # Check if folder exists to avoid errors during migration
        if not frappe.db.exists("File", {"file_name": folder, "is_folder": 1}):
            try:
                frappe.call('frappe.core.api.file.create_new_folder', folder, parent)
            except Exception:
                pass

def create_module_profiles():
    profile_name = "Rewards Extension Only"
    if not frappe.db.exists("Module Profile", profile_name):
        doc = frappe.new_doc("Module Profile")
        doc.module_profile_name = profile_name
        
        # Get all modules
        all_modules = frappe.get_all("Module Def", pluck="name")
        
        # Block everything EXCEPT "Rewards Extension"
        modules_to_block = [m for m in all_modules if m != "Rewards Extension"]
        
        for mod in modules_to_block:
            doc.append("block_modules", {"module": mod})
            
        # Avoid DocumentLockedError during migration by forcing immediate execution
        original_in_install = frappe.flags.in_install
        frappe.flags.in_install = True
        try:
            doc.insert(ignore_permissions=True)
        finally:
            frappe.flags.in_install = original_in_install

def setup_permissions():
    # Define DocType Permissions
    # Format: Doctype, Role, Perm Level, {Action: Value}
    perms = [
        ("Distributor Profile", {"read": 1, "email": 1, "print": 1, "export": 1, "report": 1, "share": 1}),
        ("Gift Voucher", {"read": 1, "write": 1, "email": 1, "print": 1, "export": 1, "report": 1, "share": 1}),
        ("Master Retail Profile", {"read": 1, "write": 1, "create": 1, "email": 1, "print": 1, "export": 1, "report": 1, "share": 1}),
        ("Payout", {"read": 1, "write": 1, "email": 1, "print": 1, "export": 1, "report": 1, "share": 1}),
        ("Quiz Transcript", {"read": 1, "email": 1, "print": 1, "export": 1, "report": 1, "share": 1}),
        ("Sales Record", {"read": 1, "email": 1, "print": 1, "export": 1, "report": 1, "share": 1}),
        ("Voucher Campaign", {"read": 1, "email": 1, "print": 1, "export": 1, "report": 1, "share": 1}),
        # User Doctype (from custom_docperm)
        ("User", {"read": 1, "select": 1, "export": 1}), 
    ]

    for doctype, perm_dict in perms:
        # Check if permission already exists to avoid duplicates
        if not frappe.db.exists("Custom DocPerm", {"parent": doctype, "role": "Campaign Viewer"}):
            add_permission(doctype, "Campaign Viewer", 0)
            # Update specific actions
            for action, value in perm_dict.items():
                update_permission_property(doctype, "Campaign Viewer", 0, action, value)

    # Add Roles to Reports
    reports = [
        "Active Campaign Links", "Agent Sales", "Distributor Sales", 
        "Distributor Sales Overview By Retailer", "Invoice Search", 
        "Last Order Since Days", "Mobile Search", "Sales Records for Retailer"
    ]
    
    for report_name in reports:
        if frappe.db.exists("Report", report_name):
            doc = frappe.get_doc("Report", report_name)
            # Check if role exists in table
            if not any(d.role == "Campaign Viewer" for d in doc.roles):
                doc.append("roles", {"role": "Campaign Viewer"})
                doc.save(ignore_permissions=True)

    # Add Role to Workspace
    if frappe.db.exists("Workspace", "Validate Requests"):
        doc = frappe.get_doc("Workspace", "Validate Requests")
        if not any(d.role == "Campaign Viewer" for d in doc.roles):
            doc.append("roles", {"role": "Campaign Viewer"})
            doc.save(ignore_permissions=True)

def assign_module_profile():
    profile_name = "Rewards Extension Only"
    roles = ["Campaign Manager", "Campaign Viewer"]
    
    # Find users with these roles (ensure parenttype is User to avoid Role Profiles)
    users = frappe.get_all("Has Role", filters={"role": ["in", roles], "parenttype": "User"}, pluck="parent", distinct=True)
    
    for user in users:
        if user in ["Administrator", "Guest"]: continue
        
        user_doc = frappe.get_doc("User", user)
        if user_doc.module_profile != profile_name:
            user_doc.module_profile = profile_name
            user_doc.save(ignore_permissions=True)
