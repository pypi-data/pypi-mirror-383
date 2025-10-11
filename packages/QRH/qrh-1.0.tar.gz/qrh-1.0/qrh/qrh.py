import qrcode
from fpdf import FPDF
import os

def generate_qr(data, file_format, output_name):
    # Create QR Code
    qr = qrcode.QRCode(
        version=1,
        box_size=10,
        border=5
    )
    qr.add_data(data)
    qr.make(fit=True)
    img = qr.make_image(fill_color='black', back_color='white')

    # Save according to selected format
    if file_format.lower() in ['png', 'jpg', 'jpeg']:
        filename = f"{output_name}.{file_format}"
        img.save(filename)
        print(f"✅ QR code saved as {filename}")

    elif file_format.lower() == 'pdf':
        temp_img = "temp_qr.png"
        img.save(temp_img)
        pdf = FPDF()
        pdf.add_page()
        pdf.image(temp_img, x=50, y=50, w=100)
        pdf.output(f"{output_name}.pdf")
        os.remove(temp_img)
        print(f"✅ QR code saved as {output_name}.pdf")

    elif file_format.lower() == 'html':
        filename = f"{output_name}.html"
        img_file = f"{output_name}.png"
        img.save(img_file)
        with open(filename, "w") as f:
            f.write(f"<html><body><h3>QR Code Output</h3><img src='{img_file}'></body></html>")
        print(f"✅ QR code saved as {filename}")

    else:
        print("❌ Unsupported file format!")

def main():
    print("=== QRCX: Simple QR Code Generator ===")
    print("Options: link | text | image | javascript | payload | other")
    option = input("Enter type: ").strip().lower()

    if option == "link":
        data = input("Enter URL: ")
    elif option == "text":
        data = input("Enter text: ")
    elif option == "image":
        data = input("Enter image path: ")
    elif option == "javascript":
        data = input("Enter JavaScript code: ")
    elif option == "payload":
        data = input("Enter payload text: ")
    else:
        data = input("Enter your custom data: ")

    output_name = input("Enter project/output name (default 'qrcode'): ") or "qrcode"
    file_format = input("Enter output format (png/jpg/pdf/html): ").strip().lower()

    generate_qr(data, file_format, output_name)
    print("Created by Babar Ali Jamali")

if __name__ == "__main__":
    main()
