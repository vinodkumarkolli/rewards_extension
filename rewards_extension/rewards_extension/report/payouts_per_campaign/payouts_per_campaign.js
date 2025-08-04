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
		}
	]
};
