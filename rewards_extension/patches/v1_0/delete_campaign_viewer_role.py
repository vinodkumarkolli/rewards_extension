import frappe

def execute():
    role = "Campaign Viewer"
    
    # 1. Remove from Reports
    reports = frappe.get_all("Report", filters={"disabled": 0})
    for report in reports:
        try:
            doc = frappe.get_doc("Report", report.name)
            original_len = len(doc.roles)
            doc.roles = [d for d in doc.roles if d.role != role]
            if len(doc.roles) != original_len:
                doc.save(ignore_permissions=True)
        except Exception:
            pass

    # 2. Remove from Workspaces
    workspaces = frappe.get_all("Workspace")
    for ws in workspaces:
        try:
            doc = frappe.get_doc("Workspace", ws.name)
            original_len = len(doc.roles)
            doc.roles = [d for d in doc.roles if d.role != role]
            if len(doc.roles) != original_len:
                doc.save(ignore_permissions=True)
        except Exception:
            pass

    # 3. Remove from Role Profiles
    role_profiles = frappe.get_all("Role Profile")
    for rp in role_profiles:
        try:
            doc = frappe.get_doc("Role Profile", rp.name)
            original_len = len(doc.roles)
            doc.roles = [d for d in doc.roles if d.role != role]
            if len(doc.roles) != original_len:
                doc.save(ignore_permissions=True)
        except Exception:
            pass

    # 4. Remove Custom DocPerms (Permissions)
    frappe.db.delete("Custom DocPerm", {"role": role})
    
    # NOTE: We DO NOT delete the Role or User assignments.
    # install.py will update the Role properties and re-add permissions.
