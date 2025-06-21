# job_hunter/resume/pdf_to_text.py
from pathlib import Path
from pdfminer.high_level import extract_text


def pdf_to_txt(pdf_path: Path, txt_path: Path) -> None:
    """Extract text from a PDF and save to a .txt file."""
    text = extract_text(pdf_path)
    txt_path.write_text(text, encoding="utf-8")
    print(f"✅ Wrote {txt_path} ({len(text.split())} words)")


if __name__ == "__main__":
    here = Path(__file__).parent
    pdf  = here / "resume.pdf"
    txt  = here / "resume.txt"
    pdf_to_txt(pdf, txt)
