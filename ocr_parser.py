from pathlib import Path

def parse_file(file_path):
    text_path = Path("parsed_attachments") / (Path(file_path).stem + ".txt")
    text_path.write_text(f"📝 Parsed: {file_path}")
    return text_path