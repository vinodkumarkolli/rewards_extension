# The authentication module for frappe-ui based Single Page Applications
import frappe
@frappe.whitelist(allow_guest=True)
def check_existing_username(mobile):
    return {'staus':'exist'}
def signup_user(mobile):
    pass