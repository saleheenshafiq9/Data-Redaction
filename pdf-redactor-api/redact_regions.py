import os
import uuid
import fitz  # PyMuPDF

async def redact_and_extract_regions(pdf_path, pii_spans, output_dir="redactions"):
    os.makedirs(output_dir, exist_ok=True)

    orig    = fitz.open(pdf_path)
    red_doc = fitz.open(pdf_path)
    records = []

    for span in pii_spans:
        page_no = span["page"] - 1
        rect    = fitz.Rect(span["bbox"])
        rid     = uuid.uuid4().hex

        # 1) crop & save the original region as PNG
        pix = orig[page_no].get_pixmap(clip=rect, dpi=150)
        img_path = os.path.join(output_dir, f"{rid}.png")
        pix.save(img_path)

        # 2) annotate that same rect with a redaction annotation
        rpage = red_doc[page_no]
        annot = rpage.add_redact_annot(rect, fill=(0, 0, 0))
        # **Embed the UUID and original text in the annotation metadata**
        annot.set_info({
            "id":           rid,
            "original_txt": span["text"]
        })

        records.append({
            **span,
            "uuid":       rid,
            "image_path": img_path
        })

    # 3) apply all redactions (paints black boxes)
    for rpage in red_doc:
        try:
            rpage.apply_redactions()
        except AttributeError:
            rpage.apply_redact()

    # 4) save the redacted PDF
    out_pdf = pdf_path.replace(".pdf", "_redacted.pdf")
    red_doc.save(out_pdf, deflate=True)

    orig.close()
    red_doc.close()
    return {"redacted_pdf": out_pdf, "regions": records}
