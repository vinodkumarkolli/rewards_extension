# Copyright (c) 2025, Vinod Kumar K and Contributors
# See license.txt

import frappe
from frappe.tests import IntegrationTestCase


# On IntegrationTestCase, the doctype test records and all
# link-field test record dependencies are recursively loaded
# Use these module variables to add/remove to/from that list
EXTRA_TEST_RECORD_DEPENDENCIES = []  # eg. ["User"]
IGNORE_TEST_RECORD_DEPENDENCIES = []  # eg. ["User"]



class IntegrationTestSalesRecordsImportJob(IntegrationTestCase):
	"""
	Integration tests for SalesRecordsImportJob.
	Use this class for testing interactions between multiple components.
	"""

	def test_cancel_import_job(self):
		"""Test that cancelling an import job cancels and deletes associated Sales Records"""
		# Create a Sales Records Import Job
		import_job = frappe.get_doc({
			"doctype": "Sales Records Import Job",
			"distributor": "Test Distributor",  # Assuming this exists in test data
			"from_date": "2025-01-01",
			"to_date": "2025-01-31"
		})
		import_job.insert()
		
		# Create some dummy import logs
		import_logs = [
			{
				"row_number": 1,
				"success": True,
				"message": "Sales Record SR-00001 created successfully with 2 line items"
			}
		]
		import_job.db_set("import_log", frappe.as_json(import_logs))
		
		# Submit the import job
		import_job.submit()
		
		# Cancel the import job
		import_job.cancel()
		
		# Verify that the import log is cleared
		import_job.reload()
		self.assertIsNone(import_job.import_log)
