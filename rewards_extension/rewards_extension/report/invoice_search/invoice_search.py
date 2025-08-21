# Copyright (c) 2025, Vinod Kumar K and contributors
# For license information, please see license.txt

import frappe
from frappe import _


def execute(filters: dict | None = None):
	"""Return columns and data for the report.

	This is the main entry point for the report. It accepts the filters as a
	dictionary and should return columns and data. It is called by the framework
	every time the report is refreshed or a filter is updated.
	"""
	columns = get_columns(filters)
	data = get_data(filters)

	return columns, data


def get_columns(filters):
	"""Return columns for the report.

	One field definition per column, just like a DocType field definition.
	"""
	columns = [
		{
			"label": _("User Mobile"),
			"fieldname": "mobile_no",
			"fieldtype": "Data",
		},
		{
			"label": _("User Email"),
			"fieldname":"email",
			"fieldtype":"Data"
		},
		{
			"label": _("User Name"),
			"fieldname": "user_name",
			"fieldtype": "Data",
		},
		{
			"label":_("Coupon Serial No"),
			"fieldname":"serial_no",
			"fieldtype":"Link",
			"options":"Gift Voucher"
		},
		{
			"label":_("Voucher Status"),
			"fieldname":"voucher_status",
			"fieldtype":"Data"
		},
		{
			"label":_("Quiz"),
			"fieldname":"quiz",
			"fieldtype":"Link",
			"options":"Quiz Transcript"
		},
		{
			"label":_("Quiz Date"),
			"fieldname":"quiz_date",
			"fieldtype":"Date"
		},
		{
			"label":_("Quizzer Type"),
			"fieldname":"quizzer_type",
			"fieldtype":"Data"
		},
		{
			"label":_("Quizzer"),
			"fieldname":"quizzer",
			"fieldtype":"Data"
		},
		{
			"label":_("Quiz Transcript"),
			"fieldname":"transcript",
			"fieldtype":"Small Text"
		},
		{
			"label":_("Payout Mode"),
			"fieldname":"payout_mode",
			"fieldtype":"Data"
		},
		{
			"label":_("Payout Beneficiary GPay or UPI ID"),
			"fieldname":"beneficiary_details",
			"fieldtype":"Data"
		}
	]
	return columns


def get_data(filters) -> list[list]:
	"""Return data for the report.

	The report data is a list of rows, with each row being a list of cell values.
	"""
	conditions = ["qt.quizzer_type = 'Customer Profile'"]
	if filters.get("inv_no"):
		conditions.append("qt.transcript LIKE %(inv_no)s")
		filters["inv_no"] = f"%{filters['inv_no']}%"

	where_condition = "WHERE " + " AND ".join(conditions) if conditions else ""

	sql = f"""
		SELECT
			u.mobile_no,
			CONCAT(u.first_name, ' ', u.last_name) as user_name,
			qt.quiz_user as email,
			gv.name as serial_no,
			gv.voucher_status,
			qt.name as quiz,
			qt.quiz_date,
			gv.payout_mode,
			gv.beneficiary_upi_details as beneficiary_details,
			qt.transcript,
			qt.quizzer_type,
			qt.quizzer
		FROM
			`tabUser` u
		JOIN
			`tabQuiz Transcript` qt ON u.name = qt.quiz_user
		LEFT JOIN
			`tabGift Voucher` gv ON qt.name = gv.quiz
		{where_condition}
	"""
	data = frappe.db.sql(sql, filters, as_dict=True)
	return data

