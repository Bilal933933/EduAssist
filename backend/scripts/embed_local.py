"""تضمين محلي بـ bge-m3 (1024 بُعد) — بديل جميني، بلا حدود API.

- يملي الصفوف ذات embedding IS NULL فقط (مستأنف تلقائيًا).
- دفعات محلية على CPU مع حفظ تقدم كل دفعة.
- نص التضمين غني بالسلسلة: مادة | مرحلة | صف | وحدة | درس + عنوان + نص.

الاستخدام:
    cd backend && python scripts/embed_local.py --batch 8 --limit 5   # تجربة
    cd backend && python scripts/embed_local.py --batch 8             # الكل
"""
import argparse
import os
import sys

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

MODEL_PATH = r"D:\Offline-600GB\07-RAG\models\e5-small"
MODEL_DIM = 384  # بدّله لـ 1024 مع bge-m3 قبل الإطلاق
PASSAGE_PREFIX = "passage: "  # بروتوكول e5؛ وعند البحث تُسبق الاستعلامات بـ query:

def embedding_text(row) -> str:
    labels = [row.subject, row.stage, row.grade, row.branch, row.unit, row.lesson]
    context = " | ".join(str(x).strip() for x in labels if x and str(x).strip())
    title = row.title or ""
    prefix = f"{context}\n{title}".strip() if context else title
    return f"{PASSAGE_PREFIX}{prefix}\n{row.text or ''}".strip()


def main() -> int:
    parser = argparse.ArgumentParser(description="تضمين محلي مستأنف")
    parser.add_argument("--batch", type=int, default=8)
    parser.add_argument("--limit", type=int, default=0, help="0 = الكل")
    args = parser.parse_args()

    from sqlalchemy import select
    import torch
    import torch.nn.functional as F
    from transformers import AutoModel, AutoTokenizer
    from app.db.session import get_engine
    from sqlalchemy.orm import sessionmaker
    from app.models.knowledge_chunk import KnowledgeChunk

    print(f"تحميل النموذج: {MODEL_PATH}", flush=True)
    tokenizer = AutoTokenizer.from_pretrained(MODEL_PATH, trust_remote_code=False)
    model = AutoModel.from_pretrained(MODEL_PATH, trust_remote_code=False)
    model.eval()
    print(f"النموذج جاهز ({MODEL_DIM} بُعد)", flush=True)

    @torch.no_grad()
    def encode(texts: list[str]):
        tok = tokenizer(texts, padding=True, truncation=True, max_length=512, return_tensors="pt")
        out = model(**tok).last_hidden_state
        mask = tok["attention_mask"].unsqueeze(-1).expand(out.size()).float()
        summed = (out * mask).sum(1)
        counts = mask.sum(1).clamp(min=1e-9)
        return F.normalize(summed / counts, p=2, dim=1).tolist()

    engine = get_engine()
    Session = sessionmaker(bind=engine)
    session = Session()
    try:
        q = select(KnowledgeChunk).where(KnowledgeChunk.embedding.is_(None)).order_by(KnowledgeChunk.id)
        if args.limit:
            q = q.limit(args.limit)
        rows = session.execute(q).scalars().all()
        print(f"صفوف ناقصة: {len(rows)}", flush=True)
        for i in range(0, len(rows), args.batch):
            batch = rows[i:i + args.batch]
            texts = [embedding_text(r) for r in batch]
            vecs = encode(texts)
            for r, v in zip(batch, vecs):
                assert len(v) == MODEL_DIM, f"بُعد غير متوقع: {len(v)}"
                r.embedding = [float(x) for x in v]
            session.commit()
            print(f"  تقدم: {min(i + args.batch, len(rows))}/{len(rows)}", flush=True)
    finally:
        session.close()
    print("تم", flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
