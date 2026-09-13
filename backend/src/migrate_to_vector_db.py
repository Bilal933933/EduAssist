"""
Script لهجرة البيانات من الملفات المحلية (chunks.json, vectors.npy) إلى قاعدة البيانات المتجهية.
استخدم هذا السكريبت مرة واحدة فقط بعد إعداد قاعدة البيانات.
"""
import os
import sys
import json
import numpy as np

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding='utf-8')
    sys.stderr.reconfigure(encoding='utf-8')

from dotenv import load_dotenv
from knowledge.vector_service import VectorService

load_dotenv()

# مسارات الملفات المحلية
STORE_DIR = os.path.join(os.path.dirname(__file__), "..", "store")
CHUNKS_PATH = os.path.join(STORE_DIR, "chunks.json")
VECTORS_PATH = os.path.join(STORE_DIR, "vectors.npy")


def migrate():
    """هجرة البيانات من الملفات المحلية إلى قاعدة البيانات المتجهية."""
    if not (os.path.exists(CHUNKS_PATH) and os.path.exists(VECTORS_PATH)):
        print("ملفات الفهرسة المحلية غير موجودة. تأكد من وجود chunks.json و vectors.npy في مجلد store/")
        return
    
    # تحميل البيانات المحلية
    print("جاري تحميل البيانات المحلية...")
    with open(CHUNKS_PATH, "r", encoding="utf-8") as f:
        chunks = json.load(f)
    vectors = np.load(VECTORS_PATH)
    
    print(f"تم تحميل {len(chunks)} قطعة و {len(vectors)} متجه.")
    
    # تهيئة خدمة قاعدة البيانات المتجهية
    vector_service = VectorService()
    
    # هجرة البيانات
    print("جاري هجرة البيانات إلى قاعدة البيانات...")
    for i, (chunk, vector) in enumerate(zip(chunks, vectors)):
        try:
            vector_service.upsert(chunk, vector.tolist())
            print(f"  هجرة القطعة {i+1}/{len(chunks)}", end="\r")
        except Exception as e:
            print(f"\nخطأ في هجرة القطعة {i+1}: {e}")
            continue
    
    print(f"\nتمت هجرة {vector_service.count()} قطعة بنجاح.")
    print("يمكنك الآن حذف الملفات المحلية (chunks.json, vectors.npy) إذا كنت تريد.")


if __name__ == "__main__":
    migrate()
