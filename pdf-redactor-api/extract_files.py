import fitz                      # pip install pymupdf
from PIL import Image           # pip install Pillow
import io
import pytesseract              # pip install pytesseract

async def extract_layout(pdf_path):
    """
    Returns list of {page, text, bbox:[x0,y0,x1,y1]} for every
    text span (or OCR word) in the PDF.
    """
    doc = fitz.open(pdf_path)
    layout = []

    for page_index, page in enumerate(doc, start=1):
        # first try native text extraction
        text_dict = page.get_text("dict")
        spans = []
        for block in text_dict["blocks"]:
            if block["type"] != 0:           # 0 = text block; 1 = image
                continue
            for line in block["lines"]:
                for span in line["spans"]:
                    spans.append({
                        "page": page_index,
                        "text": span["text"],
                        "bbox": span["bbox"]     # [x0, y0, x1, y1]
                    })

        # if no text found, do OCR
        if not spans:
            # render page to an image
            pix = page.get_pixmap(alpha=False)
            img = Image.open(io.BytesIO(pix.tobytes()))
            # use pytesseract to get word-level boxes
            ocr_data = pytesseract.image_to_data(img, output_type=pytesseract.Output.DICT)
            n = len(ocr_data["text"])
            for i in range(n):
                word = ocr_data["text"][i].strip()
                if not word:
                    continue
                x, y, w, h = (ocr_data["left"][i],
                              ocr_data["top"][i],
                              ocr_data["width"][i],
                              ocr_data["height"][i])
                spans.append({
                    "page": page_index,
                    "text": word,
                    "bbox": [x, y, x + w, y + h]
                })

        layout.extend(spans)

    return layout
