import transformers
from transformers import AutoTokenizer, AutoModelForTokenClassification, pipeline

# 1) Load the PII model once at startup
PII_MODEL = "ab-ai/pii_model"
tokenizer = AutoTokenizer.from_pretrained(PII_MODEL)
model     = AutoModelForTokenClassification.from_pretrained(PII_MODEL)
ner_pipe  = pipeline(
    "ner",
    model=model,
    tokenizer=tokenizer,
    aggregation_strategy="simple"
)

async def detect_pii(layout_info, score_threshold=0.8):
    """
    layout_info: list of {"page","text","bbox"}
    Returns spans labeled as PII with score >= threshold.
    """
    redaction_slots = []
    for span in layout_info:
        text = span["text"].strip()
        if not text:
            continue

        # 2) Run the NER pipeline on this snippet
        entities = ner_pipe(text)
        for ent in entities:
            # 3) Only keep high-confidence predictions
            if ent["score"] < score_threshold:
                continue
            redaction_slots.append({
                "page":  span["page"],
                "bbox":  span["bbox"],
                "label": ent["entity_group"],  # e.g. "EMAIL", "NAME"
                "text":  ent["word"],
                "score": ent["score"]
            })

    # 4) You now have a list of {page,bbox,label,text,score}
    return redaction_slots
