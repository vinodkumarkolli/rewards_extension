// Copyright (c) 2025, Vinod Kumar K and contributors
// For license information, please see license.txt

frappe.query_reports["Payouts per Campaign"] = {
	"filters": [
		{
			'fieldname':'campaign',
			'label':'Campaign',
			'fieldtype':'Link',
			'options':'Voucher Campaign',
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
			'fieldname':'campaign_status',
			'label':'Campaign Status',
			'fieldtype':'Select',
			'options':['Active','Held','Expired'],
			'default':'Active'
		},
		{
			'fieldname':'from_date',
			'label':'From Date',
			'fieldtype':'Date',
			'default':frappe.datetime.month_start(),
			'required':1
		},
		{
			'fieldname':'to_date',
			'label':'To Date',
			'fieldtype':'Date',
			'default':frappe.datetime.month_end(),
			'required':1
		}
	]
};
