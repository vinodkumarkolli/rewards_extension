import frappe;
from frappe.website.path_resolver import evaluate_dynamic_routes
from frappe.website.path_resolver import resolve_path as original_resolve_path
import urllib.parse
import requests
def path_resolver(path:str):
    #frappe.redirect("https://www.google.com");
    return original_resolve_path(path)
@frappe.whitelist()
def add_app_name():
	frappe.db.set_value('System Settings', None, 'app_name', 'Quadra')
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

@frappe.whitelist()
def geocode_address(address,method):
	addr_parts = []
	if hasattr(address, 'address_line1') and address.address_line1:
		addr_parts.append(address.address_line1)
	if hasattr(address, 'address_line2') and address.address_line2:
		addr_parts.append(address.address_line2)
	if hasattr(address, 'city') and address.city:
		addr_parts.append(address.city)
	if hasattr(address, 'state') and address.state:
		addr_parts.append(address.state)
	if hasattr(address, 'country') and address.country:
		addr_parts.append(address.country)
	if hasattr(address, 'pincode') and address.pincode:
		addr_parts.append(address.pincode)
	addr = ','.join(addr_parts)
	# url = f"https://nominatim.openstreetmap.org/search?q="+urllib.parse.quote(addr)+"&format=json"
	url = f"https://geocode.maps.co/search?q="+urllib.parse.quote(addr)+f"&api_key=6890ec6cddc3d030521403lmnf792de"
	
	# Set custom headers to comply with Nominatim usage policy
	headers = {
		'User-Agent': 'Rewards Extension (contact: rewards@example.com)'
	}
	
	try:
		response = requests.get(url, headers=headers)
		response.raise_for_status()  # Raise an exception for HTTP errors (4xx or 5xx)
		data = response.json()

		# Check if results were found
		if data:
			# Extract latitude and longitude from the first result
			latitude = data[0]["lat"]
			longitude = data[0]["lon"]
			print(f"Address: {addr}")
			print(f"Latitude: {latitude}")
			print(f"Longitude: {longitude}")
		else:
			print(f"No results found for {address}")

	except requests.exceptions.RequestException as e:
		print(f"An error occurred: {e}")