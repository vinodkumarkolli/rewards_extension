# Copyright (c) 2025, Vinod Kumar K and contributors
# For license information, please see license.txt

import frappe


def execute(filters=None):
	filters = frappe._dict(filters or {})
	columns = get_columns(filters)
	data = []
	
	# Build query with dynamic filters
	conditions = []
	if filters.get("campaign"):
		conditions.append("gv.campaign = %(campaign)s")
	if filters.get("beneficiary_type"):
		conditions.append("p.beneficiary_type = %(beneficiary_type)s")
	if filters.get("beneficiary"):
		conditions.append("p.beneficiary = %(beneficiary)s")
	if filters.get("from_date"):
		conditions.append("p.payout_date >= %(from_date)s")
	if filters.get("to_date"):
		conditions.append("p.payout_date <= %(to_date)s")
	
	where_condition = "WHERE " + " AND ".join(conditions) if conditions else ""
	
	query = f"""
		SELECT
			gv.campaign AS campaign,
			vc.campaign_name AS campaign_name,
			p.beneficiary_type AS beneficiary_type,
			p.beneficiary AS beneficiary,
			SUM(p.payout_amount) AS payout_amount,
			SUM(COALESCE(IF(p.payout_status = 'Under Process', p.payout_amount, 0), 0)) AS underprocess_amount,
			SUM(COALESCE(IF(p.payout_status = 'Withheld', p.payout_amount, 0), 0)) AS withheld_amount,
			SUM(COALESCE(p.transaction_amount, 0)) AS settled_amount
		FROM `tabPayout` p
		INNER JOIN `tabGift Voucher` gv
			ON p.payout_source_link = gv.name
			AND p.payout_source_type = 'Gift Voucher'
		INNER JOIN `tabVoucher Campaign` vc ON gv.campaign = vc.name
		{where_condition}
		GROUP BY gv.campaign, vc.campaign_name, p.beneficiary_type, p.beneficiary
	"""
	
	data = frappe.db.sql(query, filters, as_dict=True)
	
	return columns, data

def get_columns(filters):
	columns = [
		{
			'fieldname':'campaign',
			'label':'Campaign',
			'fieldtype':'Link',
			'options':'Voucher Campaign',
			'default': ''
		},
		{
			'fieldname':'campaign_name',
			'label':'Campaign Name',
			'fieldtype':'Data',
			'default': ''
		},
		{
		"fieldname": "beneficiary_type",
		"fieldtype": "Link",
		"label": "Beneficiary Type",
		"link_filters": "[[\"DocType\",\"name\",\"in\",[\"Master Retail Profile\",\"Customer Profile\",\"Sales Person Profile\",\"Distributor Profile\"]]]",
		"options": "DocType"
		},
		{
			'fieldname':'beneficiary',
			'label':'Beneficiary',
			'fieldtype':'Dynamic Link',
			'options':'beneficiary_type',
			'default': ''
		},
		{
			'fieldname':'payout_amount',
			'label':'Requested Amount',
			'fieldtype':'Float',
			'precision':2,
			'default': 0.00
		},
		{
			'fieldname':'underprocess_amount',
			'label':'Underprocess Amount',
			'fieldtype':'Float',
			'precision':2,
			'default': 0.00
		},
		{
			'fieldname':'withheld_amount',
			'label':'Withheld Amount',
			'fieldtype':'Float',
			'precision':2,
			'default': 0.00
		},
		{
			'fieldname':'settled_amount',
			'label':'Settled Amount',
			'fieldtype':'Float',
			'precision':2,
			'default': 0.00
		}
	]
	return columns

