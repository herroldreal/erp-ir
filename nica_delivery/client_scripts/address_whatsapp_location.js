frappe.ui.form.on("Address", {
	extract_coordinates_button: function (frm) {
		const url = (frm.doc.whatsapp_location_url || "").trim();
		if (!url) {
			frappe.msgprint("Pega primero la URL de WhatsApp o Google Maps");
			return;
		}

		const coords = extract_coordinates_from_any_url(url);

		if (coords && coords.lat && coords.lng) {
			frm.set_value({
				latitude: coords.lat.toFixed(6),
				longitude: coords.lng.toFixed(6)
			}).then(() => {
				frappe.msgprint({
					title: "¡Ubicación extraída correctamente!",
					message: `Lat: ${coords.lat.toFixed(6)} | Lng: ${coords.lng.toFixed(6)}`,
					indicator: "green"
				});
			});
		} else {
			frappe.throw("No se pudo reconocer la ubicación. Copia y pega directamente el enlace que envía WhatsApp o Google Maps.");
		}
	}
});

function extract_coordinates_from_any_url(text) {
	// 1. WhatsApp Nicaragua (el más común)
	let m = text.match(/text=([-\d.]+)%2C([-\d.]+)/);
	if (m) return {lat: parseFloat(m[1]), lng: parseFloat(m[2])};

	// 2. Google Maps @lat,lng (el que acabas de enviar)
	m = text.match(/@([-\d.]+),([-\d.]+)/);
	if (m) return {lat: parseFloat(m[1]), lng: parseFloat(m[2])};

	// 3. Google Maps /place/ con grados°min'seg"
	// Ej: 12°04'26.3"N 86°11'11.4"W
	const dms = text.match(/(\d+)°(\d+)'([\d.]+)"N.*?(\d+)°(\d+)'([\d.]+)"W/);
	if (dms) {
		const lat = parseInt(dms[1]) + parseInt(dms[2]) / 60 + parseFloat(dms[3]) / 60;
		const lng = -(parseInt(dms[4]) + parseInt(dms[5]) / 60 + parseFloat(dms[6]) / 60);
		return {lat: lat, lng: lng};
	}

	// 4. Google Maps data=!3dLAT!4dLNG
	m = text.match(/!3d([-\d.]+).*?!4d([-\d.]+)/);
	if (m) return {lat: parseFloat(m[1]), lng: parseFloat(m[2])};

	// 5. Coordenadas directas sueltas
	m = text.match(/([-\d.]{6,})\s*[, ]\s*([-\d.]{6,})/);
	if (m) return {lat: parseFloat(m[1]), lng: parseFloat(m[2])};

	return null;
}
