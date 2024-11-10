import pyotp
import qrcode
from priv_sets import SECRET_KEY,QR_CODE_DESCRIPTION,QR_CODE_ISSUER

print(f"SECRET_KEY: {SECRET_KEY}")

totp = pyotp.TOTP(SECRET_KEY)
uri = totp.provisioning_uri(name=QR_CODE_DESCRIPTION, issuer_name=QR_CODE_ISSUER)
qrcode.make(uri).save('qrcode.png')