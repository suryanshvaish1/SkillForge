from __future__ import annotations

import io
from pathlib import Path

from loguru import logger


def extract_text_from_pdf(file_bytes: bytes) -> str:
    """Extract text from a PDF file using pdfplumber (falls back to PyPDF2)."""
    text = ""
    try:
        import pdfplumber
        with pdfplumber.open(io.BytesIO(file_bytes)) as pdf:
            for i, page in enumerate(pdf.pages):
                page_text = page.extract_text() or ""
                text += page_text + "\n"
                logger.debug("PDF page {} extracted {} chars", i + 1, len(page_text))
    except Exception as e:
        logger.warning("pdfplumber failed ({}), trying PyPDF2", e)
        try:
            from PyPDF2 import PdfReader
            reader = PdfReader(io.BytesIO(file_bytes))
            for i, page in enumerate(reader.pages):
                page_text = page.extract_text() or ""
                text += page_text + "\n"
                logger.debug("PyPDF2 page {} extracted {} chars", i + 1, len(page_text))
        except Exception as e2:
            logger.error("Both PDF extractors failed: {}", e2)
            raise ValueError(f"Failed to extract text from PDF: {e2}") from e2

    text = text.strip()
    logger.info("PDF extraction complete — {} total chars", len(text))
    return text


def extract_text_from_docx(file_bytes: bytes) -> str:
    """Extract text from a DOCX file."""
    try:
        from docx import Document
        doc = Document(io.BytesIO(file_bytes))
        paragraphs = [p.text for p in doc.paragraphs if p.text.strip()]
        text = "\n".join(paragraphs)
        logger.info("DOCX extraction complete — {} paragraphs, {} chars", len(paragraphs), len(text))
        return text
    except Exception as e:
        logger.error("DOCX extraction failed: {}", e)
        raise ValueError(f"Failed to extract text from DOCX: {e}") from e


def extract_text_from_file(filename: str, file_bytes: bytes) -> str:
    """Route extraction based on file extension."""
    suffix = Path(filename).suffix.lower()
    logger.info("Extracting text from '{}' (type={})", filename, suffix)

    if suffix == ".pdf":
        return extract_text_from_pdf(file_bytes)
    elif suffix in (".docx", ".doc"):
        return extract_text_from_docx(file_bytes)
    elif suffix in (".txt", ".md", ".text"):
        text = file_bytes.decode("utf-8", errors="replace").strip()
        logger.info("TXT extraction complete — {} chars", len(text))
        return text
    else:
        raise ValueError(f"Unsupported file type: {suffix}. Use PDF, DOCX, or TXT.")
