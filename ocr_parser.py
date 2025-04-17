import os
import pytesseract
from pdf2image import convert_from_path
from PIL import Image
import tempfile

def parse_attachments(emails, download_dir="attachments"):
    """
    Приймає список email-об'єктів (з PDF-вкладеннями), розпізнає текст і повертає результат.
    """

    extracted_texts = []

    if not os.path.exists(download_dir):
        os.makedirs(download_dir)

    for i, email in enumerate(emails):
        for attachment in getattr(email, "attachments", []):
            filename = attachment.name.lower()
            if filename.endswith(".pdf"):
                file_path = os.path.join(download_dir, f"{i}_{filename}")
                with open(file_path, "wb") as f:
                    f.write(attachment.content)

                # Конвертуємо PDF у зображення
                with tempfile.TemporaryDirectory() as temp_dir:
                    images = convert_from_path(file_path, output_folder=temp_dir)
                    text_all_pages = []
                    for image in images:
                        text = pytesseract.image_to_string(image, lang="uk+eng")
                        text_all_pages.append(text)

                full_text = "\n".join(text_all_pages)
                extracted_texts.append({
                    "file": filename,
                    "text": full_text
                })

    return extracted_texts# OCR logic goes here
