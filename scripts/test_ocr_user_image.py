import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

from PIL import Image
from desktop.core.ocr_engine import ocr_engine
from desktop.core.question_parser import question_parser
import json

img_path = r'C:\Users\tejag\.gemini\antigravity\brain\1302c8fb-64ee-459c-9abd-9e636bfd2cc5\.user_uploaded\media_1793885082870_0ff1229a.png'
img = Image.open(img_path)
res = ocr_engine.extract_text(img)
print(f"Total lines extracted: {len(res['lines'])}")
for idx, item in enumerate(res['lines']):
    text = item['text']
    if any(k in text for k in ["BTB", "Branch", "fetch", "instruction", "points", "1."]):
        print(f"Line {idx}: {text}")

parsed = question_parser.parse_from_lines(res['lines'])
print("\nCurrent Parser Output:")
print("Question:", parsed.get("question"))
print("Options:", json.dumps(parsed.get("options"), indent=2, ensure_ascii=False))
