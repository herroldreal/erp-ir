# apps/nica_delivery/nica_delivery/patches/add_whatsapp_fields_final.py
import frappe
from frappe.custom.doctype.custom_field.custom_field import create_custom_fields


def execute():
	print("Ejecutando patch v15_999_add_whatsapp_fields...")

	custom_fields = {
		"Address": [
			{
				"fieldname": "whatsapp_location_section",
				"fieldtype": "Section Break",
				"label": "Ubicación por WhatsApp",
				"insert_after": "address_line2",
				"collapsible": 1
			},
			{
				"fieldname": "whatsapp_location_url",
				"label": "URL de Ubicación (WhatsApp / Google Maps)",
				"fieldtype": "Long Text",  # ← Long Text, no Link
				"insert_after": "whatsapp_location_section",
				"description": "Pega aquí el enlace completo que envía el cliente por WhatsApp o Google Maps",
				"translatable": 0
			},
			{
				"fieldname": "extract_coordinates_button",
				"label": "Extraer Latitud y Longitud",
				"fieldtype": "Button",
				"insert_after": "whatsapp_location_url"
			},
			{
				"fieldname": "whatsapp_column_break",
				"fieldtype": "Column Break",
				"insert_after": "extract_coordinates_button"
			}
		]
	}

	# Esta función es la oficial y NUNCA falla
	create_custom_fields(custom_fields, ignore_validate=True)
	frappe.clear_cache()
