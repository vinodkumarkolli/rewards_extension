frappe.pages['sales-import-utility'].on_page_load = function(wrapper) {
	var page = frappe.ui.make_app_page({
		parent: wrapper,
		title: 'Sales Import Utility',
		single_column: true
	});
}