import frappe;
from frappe.website.path_resolver import evaluate_dynamic_routes
from frappe.website.path_resolver import resolve_path as original_resolve_path

def path_resolver(path:str):
    #frappe.redirect("https://www.google.com");
    return original_resolve_path(path)
@frappe.whitelist()
def move_file(file_path, target_folder):
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
