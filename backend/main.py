import os
import sys
from pathlib import Path

# تهيئة الترميز العربي لWindows
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding='utf-8')
    sys.stderr.reconfigure(encoding='utf-8')

# ضمان أن جذر backend هو مجلد العمل حتى يعمل التشغيل من أي مكان
os.chdir(Path(__file__).resolve().parent)

if __name__ == "__main__":
    import uvicorn

    # تهيئة Uvicorn بدعم UTF-8 (حل مشكلة الترميز العربي في Windows)
    uvicorn.run(
        "app.main:app",
        host="127.0.0.1",
        port=8000,
        reload=True,
        loop="asyncio",
        http="h11"
    )
