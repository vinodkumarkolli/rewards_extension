// https://docs.frappe.io/framework/v13/user/en/api/list#standard-list-js
frappe.listview_settings['Gift Voucher'] = {
    add_fields: [
		"name",
		"secret_code",
		"batch_id",
		"campaign",
		"created_on",
		"activated_on",
	],
    get_indicator: function(doc){
        if(!doc.activated_on && doc.voucher_status == 'Active'){
            return [__("Pending Activation"), "orange"];
        } else if (!doc.activated_on && doc.voucher_status != 'Active') {
            return [__(`${doc.voucher_status}`), "red"];
        } else if (doc.activated_on) {
            return [__("Activated"), "green"];
        }
    },
    right_column: "voucher_status",
    onload: function (listview) {
        listview.page.add_action_item(__("Print Vouchers"), () => {
            frappe.msgprint("Printing Vouchers");
        });
    }
}