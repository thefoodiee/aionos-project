# rag/parser.py
import io
import mimetypes
from pathlib import Path
from typing import Dict, Any, Optional

class ResumeParser:
    """
    Unified Resume Parser supporting:
    - PDF (via PyMuPDF / fitz)
    - DOCX / DOC (via python-docx)
    - Images (.png, .jpg, .jpeg, .webp via Gemini multimodal & Pillow)
    - Plain text / Markdown
    """

    IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png", ".webp", ".bmp"}
    DOCX_EXTENSIONS = {".docx", ".doc"}
    PDF_EXTENSIONS = {".pdf"}
    TEXT_EXTENSIONS = {".txt", ".md", ".rtf"}

    @classmethod
    def get_mime_type(cls, filename: str) -> str:
        mime, _ = mimetypes.guess_type(filename)
        if mime:
            return mime
        ext = Path(filename).suffix.lower()
        if ext in (".jpg", ".jpeg"):
            return "image/jpeg"
        elif ext == ".png":
            return "image/png"
        elif ext == ".webp":
            return "image/webp"
        elif ext == ".pdf":
            return "application/pdf"
        elif ext == ".docx":
            return "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
        return "text/plain"

    @classmethod
    def parse_pdf(cls, content_bytes: bytes, filename: str = "resume.pdf") -> str:
        """Extract text from PDF using PyMuPDF (fitz)."""
        try:
            import fitz
            doc = fitz.open(stream=content_bytes, filetype="pdf")
            pages_text = []
            for page_num in range(len(doc)):
                page = doc[page_num]
                text = page.get_text()
                if text.strip():
                    pages_text.append(text.strip())
            doc.close()
            if pages_text:
                return "\n\n".join(pages_text)
        except Exception as e:
            # Fallback to pypdf if fitz fails
            try:
                import pypdf
                reader = pypdf.PdfReader(io.BytesIO(content_bytes))
                texts = [page.extract_text() for page in reader.pages if page.extract_text()]
                if texts:
                    return "\n\n".join(texts)
            except Exception:
                pass
            raise ValueError(f"Failed to extract text from PDF '{filename}': {str(e)}")

        return ""

    @classmethod
    def parse_docx(cls, content_bytes: bytes, filename: str = "resume.docx") -> str:
        """Extract text from Word .docx file using python-docx."""
        try:
            import docx
            doc = docx.Document(io.BytesIO(content_bytes))
            parts = []
            for paragraph in doc.paragraphs:
                if paragraph.text.strip():
                    parts.append(paragraph.text.strip())
            for table in doc.tables:
                for row in table.rows:
                    row_data = [cell.text.strip() for cell in row.cells if cell.text.strip()]
                    if row_data:
                        parts.append(" | ".join(row_data))
            return "\n".join(parts)
        except Exception as e:
            # Fallback: scan printable strings
            try:
                decoded = content_bytes.decode("utf-8", errors="ignore")
                printable = "".join(ch for ch in decoded if ch.isprintable() or ch in "\n\r\t")
                if len(printable.strip()) > 60:
                    return printable.strip()
            except Exception:
                pass
            raise ValueError(f"Failed to extract text from DOCX '{filename}': {str(e)}")

    @classmethod
    def parse_image_with_gemini(cls, content_bytes: bytes, filename: str, api_key: str, model_name: str = "gemini-2.5-flash") -> str:
        """Extract resume text from image using Gemini Multimodal Vision API."""
        try:
            from google import genai
            from google.genai import types
            
            client = genai.Client(api_key=api_key)
            mime_type = cls.get_mime_type(filename)
            part = types.Part.from_bytes(data=content_bytes, mime_type=mime_type)
            
            prompt = (
                "You are an OCR and document extraction engine. "
                "Transcribe all text from this resume image verbatim, maintaining sections, titles, and bullet points. "
                "Output ONLY the extracted resume text without any conversational remarks."
            )
            response = client.models.generate_content(
                model=model_name,
                contents=[part, prompt]
            )
            if response.text:
                return response.text.strip()
        except Exception as e:
            print(f"Notice: Gemini image OCR failed ({e}). Attempting image verification...")
        
        # Verify image format using Pillow
        try:
            from PIL import Image
            img = Image.open(io.BytesIO(content_bytes))
            return f"[Resume Image: {filename} ({img.format}, {img.size[0]}x{img.size[1]}px) - Visual CV]"
        except Exception:
            return f"[Resume Image: {filename}]"

    @classmethod
    def extract_text(cls, content_bytes: bytes, filename: str, gemini_api_key: Optional[str] = None, gemini_model: str = "gemini-2.5-flash") -> Dict[str, Any]:
        """
        Main extraction entry point. Returns dictionary with text and metadata.
        """
        ext = Path(filename).suffix.lower()
        mime_type = cls.get_mime_type(filename)

        if ext in cls.PDF_EXTENSIONS:
            text = cls.parse_pdf(content_bytes, filename)
            mode = "pdf"
        elif ext in cls.DOCX_EXTENSIONS:
            text = cls.parse_docx(content_bytes, filename)
            mode = "docx"
        elif ext in cls.IMAGE_EXTENSIONS:
            if gemini_api_key:
                text = cls.parse_image_with_gemini(content_bytes, filename, gemini_api_key, gemini_model)
            else:
                text = f"[Image Resume: {filename} - Gemini API key required for vision OCR]"
            mode = "image"
        else:
            text = content_bytes.decode("utf-8", errors="ignore")
            mode = "text"

        return {
            "filename": filename,
            "mime_type": mime_type,
            "mode": mode,
            "text": text.strip(),
            "byte_size": len(content_bytes),
        }
