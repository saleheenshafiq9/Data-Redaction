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
    redaction_slots = []
    for span in layout_info:
        text = span["text"].strip()
        if not text:
            continue

        entities = ner_pipe(text)
        for ent in entities:
            # pull the score out as a native float
            score = float(ent["score"])
            if score < score_threshold:
                continue

            redaction_slots.append({
                "page":  int(span["page"]),        # ensure native int
                "bbox":  [float(x) for x in span["bbox"]],  # native floats
                "label": ent["entity_group"],
                "text":  ent["word"],
                "score": score
            })

    return redaction_slots
