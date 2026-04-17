"""OCR 引擎：基于 PaddleOCR，支持图片和扫描 PDF"""
from __future__ import annotations

import logging
from pathlib import Path

logger = logging.getLogger(__name__)

_ocr_instance = None


def _get_ocr():
    global _ocr_instance
    if _ocr_instance is None:
        from paddleocr import PaddleOCR
        _ocr_instance = PaddleOCR(use_angle_cls=True, lang="ch", show_log=False)
    return _ocr_instance


def ocr_image(image_path: str | Path) -> str:
    """识别单张图片中的文字"""
    ocr = _get_ocr()
    result = ocr.ocr(str(image_path), cls=True)
    lines = []
    if result:
        for page in result:
            if page:
                for line in page:
                    text = line[1][0] if line[1] else ""
                    if text.strip():
                        lines.append(text.strip())
    return "\n".join(lines)


def ocr_pdf(pdf_path: str | Path) -> str:
    """将 PDF 每页转为图片后 OCR"""
    import fitz
    doc = fitz.open(str(pdf_path))
    all_text = []
    for page_num in range(len(doc)):
        page = doc[page_num]
        pix = page.get_pixmap(dpi=200)
        img_bytes = pix.tobytes("png")

        import tempfile, os
        with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as tmp:
            tmp.write(img_bytes)
            tmp_path = tmp.name
        try:
            text = ocr_image(tmp_path)
            if text:
                all_text.append(f"--- 第 {page_num + 1} 页 ---\n{text}")
        finally:
            os.unlink(tmp_path)
    doc.close()
    return "\n\n".join(all_text)
