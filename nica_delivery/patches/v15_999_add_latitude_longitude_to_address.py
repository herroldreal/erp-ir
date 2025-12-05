import frappe


def execute():
	fields = [
		{
			"doctype": "Custom Field",
			"dt": "Address",
			"fieldname": "latitude",
			"label": "Latitude",
			"fieldtype": "Float",
			"insert_after": "pincode"
		},
		{
			"doctype": "Custom Field",
			"dt": "Address",
			"fieldname": "longitude",
			"label": "Longitude",
			"fieldtype": "Float",
			"insert_after": "latitude"
		}
	]
	for field in fields:
		if not frappe.db.exists("Custom Field",
								{"dt": field["dt"], "fieldname": field["fieldname"]}):
			frappe.get_doc(field).insert()
