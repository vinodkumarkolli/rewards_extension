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
	columns = get_columns()
	data = get_data(filters)

	return columns, data


def get_columns() -> list[dict]:
	"""Return columns for the report.

	One field definition per column, just like a DocType field definition.
	"""
	columns =[
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
			"label":_("Coupon Used Date"),
			"fieldname":"blocked_date",
			"fieldtype":"Date"
		},
		{
			"label": _("Coupon Status"),
			"fieldname":"voucher_status",
			"fieldtype":"Data"
		},
		{
			"label":_("Beneficiary Type"),
			"fieldname":"beneficiary_type",
			"fieldtype":"Data"
		},
		{
			"label":_("Beneficiary Name"),
			"fieldname":"beneficiary",
			"fieldtype":"Data"
		},
		{
			"label":_("Quiz"),
			"fieldname":"quiz",
			"fieldtype":"Link",
			"options":"Quiz Transcript"
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
		},
		{
			"label":_("Payout"),
			"fieldname":"payout",
			"fieldtype":"Link",
			"options":"Payout"
		}
	]
	return columns


def get_data(filters: dict) -> list[list]:
	"""Return data for the report.

	The report data is a list of rows, with each row being a list of cell values.
	"""
	if not filters.get("mobile_no"):
		return []

	mobile_no_without_prefix = filters.get("mobile_no")
	mobile_no = mobile_no_without_prefix
	if not mobile_no.startswith("+91"):
		mobile_no = f"+91{mobile_no}"

	data = frappe.db.sql(
		"""
		SELECT
			u.mobile_no,
			gv.blocked_by_user,
			CONCAT(u.first_name, ' ', u.last_name),
			gv.name,
			gv.blocked_date,
			gv.voucher_status,
			gv.beneficiary_type,
			gv.beneficiary,
			gv.quiz,
			gv.payout_mode,
			gv.beneficiary_upi_details,
			p.name
		FROM
			`tabGift Voucher` as gv
		JOIN
			`tabUser` as u ON gv.blocked_by_user = u.name
		LEFT JOIN
			`tabPayout` as p ON p.payout_source_link = gv.name AND p.payout_source_type = 'Gift Voucher'
		WHERE
			u.mobile_no = %(mobile_no)s
		UNION
		SELECT
			u.mobile_no,
			gv.blocked_by_user,
			CONCAT(u.first_name, ' ', u.last_name),
			gv.name,
			gv.blocked_date,
			gv.voucher_status,
			gv.beneficiary_type,
			gv.beneficiary,
			gv.quiz,
			gv.payout_mode,
			gv.beneficiary_upi_details,
			p.name
		FROM
			`tabGift Voucher` as gv
		JOIN
			`tabUser` as u ON gv.blocked_by_user = u.name
		LEFT JOIN
			`tabPayout` as p ON p.payout_source_link = gv.name AND p.payout_source_type = 'Gift Voucher'
		WHERE
			gv.beneficiary_upi_details LIKE CONCAT('%%', %(mobile_no_without_prefix)s)
			AND LENGTH(%(mobile_no_without_prefix)s) = 10
			AND u.mobile_no != %(mobile_no)s
	""",
		{"mobile_no": mobile_no, "mobile_no_without_prefix": mobile_no_without_prefix},
		as_list=True,
	)
	return data
