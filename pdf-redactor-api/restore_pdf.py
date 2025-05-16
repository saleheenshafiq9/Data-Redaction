import fitz  # PyMuPDF

def restore_pdf_by_uuid(redacted_pdf_path, sidecar_records, output_path=None):
    """
    sidecar_records: dict mapping uuid -> { 'image_path':..., ... }
    """
    doc = fitz.open(redacted_pdf_path)

    for page in doc:
        annot = page.firstAnnot
        while annot:
            info = annot.info
            rid  = info.get("id")
            # if this annotation has an ID we recognize
            if rid and rid in sidecar_records:
                rec   = sidecar_records[rid]
                rect  = annot.rect
                img_p = rec["image_path"]

                # delete the black-box annotation
                next_annot = annot.next
                page.deleteAnnot(annot)
                annot = next_annot

                # insert the original PNG back at exactly that rect
                page.insert_image(
                    rect,
                    filename=img_p,
                    keep_proportion=False
                )
                continue

            # otherwise, move to the next annotation
            annot = annot.next

    out = output_path or redacted_pdf_path.replace(".pdf", "_restored.pdf")
    doc.save(out, deflate=True)
    doc.close()
    return out
