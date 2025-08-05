// Copyright (c) 2025, Vinod Kumar K and contributors
// For license information, please see license.txt

frappe.ui.form.on("Payout", {
	refresh(frm) {
        frm.add_custom_button(__('Upload Receipts'),function(){
                uploadReceiptsPopup(frm)
        })
        frm.add_custom_button(__('Generate Reports'),function(){},__('Reports'))
	},
});
function uploadReceiptsPopup(frm){
    d = new frappe.ui.Dialog({
        'title': __('Upload Payment Details'),
        'fields':[
            {fieldname:'transaction_id',
                label:'Transaction ID',
                fieldtype:'Data',
                reqd:1},
            {fieldname:'transaction_amount',
                label:'Transaction Amount',
                fieldtype:'Float',
                reqd:1},
            {fieldname:'transaction_date',
                label:'Transaction Date',
                fieldtype:'Date',
                reqd:1},
            {fieldname:'transaction_image',
                label:'Transaction Image',
                fieldtype: 'Attach',
                options: 'image/*',
                on_attach: function(file_url, file_name) {
                    // This function is called when a file is attached
                    frappe.call({
                        method:'rewards_extension.utils.move_file',
                        args:{
                            file_path:file_url,
                            target_folder:"Home/Payout Images"
                        },
                        callback:function(r){
                            if(!r.exc){
                                //refresh_field('status');
                                // console.log(r.message);
                            }
                        }
                    })
                    // console.log('Attached file:', file_name, file_url);
                    // You can perform further actions here, e.g., update another field
                },
                reqd:1}],
        primary_action_label: 'Upload and Approve',
        primary_action:function(){
            var transactionId = d.get_value('transaction_id');
            var transactionAmount = d.get_value('transaction_amount');
            var transactionDate = d.get_value('transaction_date');
            var transactionImage = d.get_value('transaction_image');
            // console.log(transactionImage)
            frappe.call({
            method:'rewards_extension.rewards_extension.doctype.payout.payout.approve_payout',
            args:{
                payout_id:frm.doc.name,
                trx_id: transactionId,
                trx_amt: transactionAmount,
                trx_date: transactionDate,
                trx_image: transactionImage
            },
            callback:function(r){
                if(!r.exc){
                    //refresh_field('status');
                    // console.log(r.message);
                    d.hide()
                }
            }
            })
            // alert('Creating '+count+' vouchers')
        }
    })
    d.show()
}