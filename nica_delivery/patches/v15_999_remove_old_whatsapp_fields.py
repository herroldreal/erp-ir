import frappe


def execute():
	field = frappe.db.exists("Custom Field", {"dt": "Address", "fieldname": "delivery_location"})

	if field:
		frappe.delete_doc("Custom Field", field, force=1, ignore_permissions=True)
		frappe.db.commit()
		print("Campo Geolocation eliminado")
