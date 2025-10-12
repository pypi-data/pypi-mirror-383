# CliSelf/modules/text_manager.py

import os
from ..core.logger import get_logger

logger = get_logger("text")

class TextManager:
    """
    TextManager
    ------------
    مدیریت فایل متنی برای ذخیره، حذف و پاک‌سازی خطوط
    و مدیریت کپشن (caption).
    """

    def __init__(self, text_path: str = "downloads/text.txt"):
        self.text_path = text_path
        self.caption = ""
        os.makedirs(os.path.dirname(self.text_path), exist_ok=True)
        if not os.path.exists(self.text_path):
            open(self.text_path, "w", encoding="utf-8").close()
        logger.info(f"TextManager initialized at {self.text_path}")

    # -------------------------------
    # افزودن یک خط جدید
    # -------------------------------
    async def add_text(self, text: str):
        if not text.strip():
            logger.warning("Attempted to add empty text.")
            raise ValueError("❌ متنی وارد نشده.")
        with open(self.text_path, "a", encoding="utf-8") as f:
            f.write(text.strip() + "\n")
        logger.info(f"✅ Added line: {text.strip()}")
        return "✅ متن ذخیره شد."

    # -------------------------------
    # افزودن چند خط به صورت یکجا
    # -------------------------------
    async def add_all_text(self, text_block: str):
        lines = [ln.strip() for ln in text_block.splitlines() if ln.strip()]
        if not lines:
            logger.warning("Attempted to add empty multi-line text block.")
            raise ValueError("❌ متنی برای ذخیره وجود ندارد.")
        with open(self.text_path, "a", encoding="utf-8") as f:
            for line in lines:
                f.write(line + "\n")
        logger.info(f"✅ Added {len(lines)} lines.")
        return f"✅ {len(lines)} خط ذخیره شد."

    # -------------------------------
    # حذف خط مشخص از فایل
    # -------------------------------
    async def delete_text(self, target: str):
        if not target.strip():
            logger.warning("Attempted to delete empty target.")
            raise ValueError("❌ متنی برای حذف وارد نشده.")
        with open(self.text_path, "r", encoding="utf-8") as f:
            lines = [ln for ln in f.read().splitlines()]
        kept = [ln for ln in lines if ln != target.strip()]
        removed = len(lines) - len(kept)
        with open(self.text_path, "w", encoding="utf-8") as f:
            f.write("\n".join(kept) + ("\n" if kept else ""))
        logger.info(f"🗑️ Deleted {removed} line(s) matching '{target.strip()}'")
        return f"🗑️ {removed} خط حذف شد."

    # -------------------------------
    # پاکسازی کل فایل متن
    # -------------------------------
    async def clear_text(self):
        with open(self.text_path, "w", encoding="utf-8") as f:
            f.write("")
        logger.info("🧹 Cleared all text lines.")
        return "متن پاکسازی شد."

    # -------------------------------
    # تنظیم کپشن
    # -------------------------------
    async def set_caption(self, caption: str):
        if not caption.strip():
            logger.warning("Attempted to set empty caption.")
            raise ValueError("❌ کپشن خالی است.")
        self.caption = caption.strip()
        logger.info(f"📝 Caption set: {self.caption}")
        return "کپشن ذخیره شد."

    # -------------------------------
    # پاکسازی کپشن
    # -------------------------------
    async def clear_caption(self):
        self.caption = ""
        logger.info("🧹 Caption cleared.")
        return "کپشن پاکسازی شد."
