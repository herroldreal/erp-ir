import frappe
from nica_delivery.utils.distance import haversine


@frappe.whitelist()
def create_task_from_invoice(doc, method):
	task = frappe.new_doc("Nica Delivery Task")
	task.customer = doc.customer
	task.invoice = doc.name
	task.address = doc.customer_address
	task.latitude = frappe.db.get_value("Address", doc.customer_address, "latitude") or 0
	task.longitude = frappe.db.get_value("Address", doc.customer_address, "longitude") or 0
	task.status = "Pending"
	task.insert()


@frappe.whitelist()
def create_task_from_delivery_note(doc, method):
	task = frappe.new_doc("Nica Delivery Task")
	task.customer = doc.customer
	task.invoice = doc.reference_name if doc.reference_doctype == "Sales Invoice" else ""
	task.address = doc.shipping_address
	task.latitude = frappe.db.get_value("Address", doc.shipping_address_name, "latitude") or 0
	task.longitude = frappe.db.get_value("Address", doc.shipping_address_name, "longitude") or 0
	task.status = "Pending"
	task.insert()


@frappe.whitelist(allow_guest=True)
def update_location(employee, latitude, longitude):
	employee_doc = frappe.get_doc("Employee", employee)

	loc = frappe.new_doc("Driver Location")
	loc.employee = employee
	loc.latitude = float(latitude)
	loc.longitude = float(longitude)
	loc.insert(ignore_permissions=True)

	return {"status": "ok", "timestamp": loc.timestamp}


@frappe.whitelist()
def calculate_shipping_cost(doc, method=None):
	if doc.docstatus != 0: return

	settings = frappe.get_single("Delivery Settings")
	address = doc.customer_address or doc.shipping_address_name
	if not address: return

	lat = frappe.db.get_value("Address", address, "latitude")
	lng = frappe.db.get_value("Address", address, "longitude")
	if not (lat and lng): return

	zone = None
	zones = frappe.get_all("Shipping Zone", fields=["name", "center_latitude", "center_longitude",
													"maximum_distance_km", "shipping_cost"])
	for z in zones:
		dist = haversine(lat, lng, z.center_latitude, z.center_longitude)
		if dist <= z.maximum_distance_km:
			zone = z
			break

	cost = zone.shipping_cost if zone else settings.default_shipping_cost

	# Borra envío anterior
	doc.items = [i for i in doc.items if i.item_code == settings.shipping_item]

	# Añade el nuevo
	doc.append("items", {
		"item_code": settings.shipping_item,
		"qty": 1,
		"rate": cost,
		"income_account": settings.income_account,
		"cost_center": settings.cost_center,
		"description": f"Envío - {zone.name if zone else 'Fuera de zona'}"
	})
	doc.run_method("calculate_taxes_and_totals")


@frappe.whitelist()
def create_delivery_task(doc, method=None):
	if doc.docstatus != 1: return
	if not frappe.get_single("Delivery Settings").enable_auto_task: return
	if frappe.db.exists("Nica Delivery Task", {"invoice": doc.name}): return

	address = doc.customer_address or doc.shipping_address_name
	if not address: return
	lat = frappe.db.get_value("Address", address, "latitude")
	lng = frappe.db.get_value("Address", address, "longitude")
	if not (lat and lng): return

	task = frappe.new_doc("Nica Delivery Task")
	task.customer = doc.customer
	task.invoice = doc.name
	task.address = address
	task.latitude = lat
	task.longitude = lng
	task.status = "Pendiente"
	task.insert(ignore_permissions=True)
