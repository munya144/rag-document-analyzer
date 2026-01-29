import traceback
from pathlib import Path
from typing import Tuple, List

import PyPDF2


def extract_metadata(pdf_path: str) -> dict:
    """Extract PDF metadata (author, title, pages, etc.)"""
    metadata = {
        "title": "",
        "creation_date": "",
        "modification_date": "",
        "pages": 0,
        "file_size": 0,
        "file_name": Path(pdf_path).name,
    }

    try:
        # Get file size
        file_size_bytes = Path(pdf_path).stat().st_size
        metadata["file_size"] = file_size_bytes

        # Extract PDF metadata
        with open(pdf_path, "rb") as file:
            pdf_reader = PyPDF2.PdfReader(file)

            # Get number of pages
            metadata["pages"] = len(pdf_reader.pages)

            # Get document info (metadata)
            if pdf_reader.metadata:
                info = pdf_reader.metadata
                metadata["title"] = info.get("/Title", "")
                metadata["creation_date"] = info.get("/CreationDate", "")
                metadata["modification_date"] = info.get("/ModDate", "")

    except Exception as e:
        # В случае ошибки возвращаем хотя бы базовую информацию
        metadata["error"] = f"Ошибка при извлечении метаданных: {str(e)}"
        print(f"Error extracting metadata from {pdf_path}: {traceback.format_exc()}")

    return metadata


class SimpleFileValidator:
    MAX_SIZE_MB: int = 10
    ALLOWED_EXTENSIONS: List[str] = [".pdf"]

    @staticmethod
    def validate_file(file_path: str) -> Tuple[bool, str]:
        """
        Validate uploaded file (simpler version without pdfplumber).

        Args:
            file_path: Путь к файлу для валидации

        Returns:
            Tuple[bool, str]: (is_valid, error_message)
        """
        path: Path = Path(file_path)

        # 1) Check file exists
        if not path.exists():
            return False, "Файл не найден"

        if not path.is_file():
            return False, "Это не файл"

        # 2) Check extension is .pdf
        if path.suffix.lower() not in SimpleFileValidator.ALLOWED_EXTENSIONS:
            return (
                False,
                f"Неверный формат файла. Разрешены только: {', '.join(SimpleFileValidator.ALLOWED_EXTENSIONS)}",
            )

        # 3) Check file size < MAX_SIZE_MB
        file_size_mb: float = path.stat().st_size / (1024 * 1024)
        if file_size_mb > SimpleFileValidator.MAX_SIZE_MB:
            return (
                False,
                f"Файл слишком большой. Максимальный размер: {SimpleFileValidator.MAX_SIZE_MB}MB",
            )

        # 4) Check file is not empty
        if path.stat().st_size == 0:
            return False, "Файл пустой"

        # 5) Basic PDF check (check magic bytes)
        try:
            with open(file_path, "rb") as f:
                header: bytes = f.read(5)
                if header != b"%PDF-":
                    return False, "Файл не является валидным PDF"
        except Exception as e:
            return False, f"Ошибка при чтении файла: {str(e)}"

        return True, ""
