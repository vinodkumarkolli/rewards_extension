# Copyright (c) 2025, Vinod Kumar K and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe.utils import now

class QuizTranscript(Document):
	pass

@frappe.whitelist()
def submit_quiz_answers(questions, answers, profile,user,source):
	"""
	Submit user's answers for a quiz and process the results.
	
	Args:
		questions (list): List of question objects or identifiers from the quiz
		answers (list): User's answers in {question_id: answer} format
		profile (object): User profile identifier (e.g., user ID or quizzer doctype, quizzer name)
		user: is the session email
		source (object): Quiz is usually triggered from Gift Voucher, Customer Profile or Sales Profile or so on. After 
	Returns:
		dict: Result of quiz submission containing status and score
	"""
	# Generate formatted transcript
	# Generate formatted transcript
	transcript = "Quiz Started\n\n"
	for i in range(len(questions)):
		# Access 'main' property from question and answer dictionaries
		transcript += f"Q) {questions[i]}\n"
		transcript += f"A) {answers[i]['main']}\n\n"
		transcript += "=" * 20 + "\n\n"  # Separator for readability
	transcript += "End of Quiz"
	quiz = frappe.get_doc({
		"doctype": "Quiz Transcript",
		"transcript": transcript,
		"quiz_user": user,
		"quiz_date": now(),
		"quizzer_type": profile.get("doctype"),
		"quizzer": profile.get("name")
	})
	quiz.insert(ignore_permissions=True)
	quiz.submit()
	if source.get("doctype") == "Gift Voucher":
		try:
			update_quiz_in_gift_voucher(source.get("name"),quiz)
			return {
				"status": "success",
				"quiz": quiz.as_dict()
			}
		except Exception as e:
			return {
				"status": "error",
				"message": str(e)
			}
	else:
		return {
		"status": "success",
		"quiz": quiz.as_dict()
		}
	
def update_quiz_in_gift_voucher(voucher_name,quiz):
	voucher_doc = frappe.get_doc("Gift Voucher", voucher_name)
	voucher_doc.quiz = quiz.name
	voucher_doc.save(ignore_permissions=True)
	return {
		"status": "success",
	}