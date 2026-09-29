"""
UPI URI builder + QR code generator.

Returns:
    - build_upi_uri()      -> str   (the "upi://pay?...&..." URI)
    - build_qr_png_bytes() -> bytes (PNG image data of the QR)
"""
from io import BytesIO
from urllib.parse import urlencode

import qrcode
from flask import current_app


def build_upi_uri(amount_paise: int, note: str = '', txn_ref: str = '') -> str:
    """
    Build a standard UPI payment URI.

    Format: upi://pay?pa=<vpa>&pn=<name>&am=<amount>&cu=INR&tn=<note>&tr=<txnref>
    """
    amount = f'{amount_paise / 100:.2f}'

    params = {
        'pa': current_app.config.get('UPI_ID', 'gym@upi'),
        'pn': current_app.config.get('UPI_PAYEE_NAME', 'Gym Management'),
        'am': amount,
        'cu': 'INR',
    }
    if note:
        params['tn'] = note[:50]
    if txn_ref:
        params['tr'] = txn_ref[:35]

    return 'upi://pay?' + urlencode(params)


def build_qr_png_bytes(data: str) -> bytes:
    """Generate a QR code PNG in memory from the given payload."""
    qr = qrcode.QRCode(
        version=None,
        error_correction=qrcode.constants.ERROR_CORRECT_M,
        box_size=8,
        border=2,
    )
    qr.add_data(data)
    qr.make(fit=True)

    img = qr.make_image(fill_color='black', back_color='white')
    buf = BytesIO()
    img.save(buf, format='PNG')
    return buf.getvalue()