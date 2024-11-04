from pyzbar.pyzbar import decode
from PIL import Image

def scan_barcode(image_path):
    """
    Scans the barcode from the given image path and returns the decoded data.
    """
    image = Image.open(image_path)
    decoded_objects = decode(image)
    for obj in decoded_objects:
        return obj.data.decode('utf-8')
    return None
