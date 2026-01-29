from pathlib import Path

class SimpleFileValidator:
    MAX_SIZE_MB = 10
    ALLOWED_EXTENSIONS = ['.pdf']

    @staticmethod
    def validate_file(file_path: str) -> tuple[bool, str]:
        """
        Validate uploaded file (simpler version without pdfplumber).
        """
        path = Path(file_path)

        # 1) Check file exists
        if not path.exists():
            return False, "Файл не найден"

        if not path.is_file():
            return False, "Это не файл"

        # 2) Check extension is .pdf
        if path.suffix.lower() not in SimpleFileValidator.ALLOWED_EXTENSIONS:
            return False, f"Неверный формат файла. Разрешены только: {', '.join(SimpleFileValidator.ALLOWED_EXTENSIONS)}"

        # 3) Check file size < MAX_SIZE_MB
        file_size_mb = path.stat().st_size / (1024 * 1024)
        if file_size_mb > SimpleFileValidator.MAX_SIZE_MB:
            return False, f"Файл слишком большой. Максимальный размер: {SimpleFileValidator.MAX_SIZE_MB}MB"

        # 4) Check file is not empty
        if path.stat().st_size == 0:
            return False, "Файл пустой"

        # 5) Basic PDF check (check magic bytes)
        try:
            with open(file_path, 'rb') as f:
                header = f.read(5)
                if header != b'%PDF-':
                    return False, "Файл не является валидным PDF"
        except Exception as e:
            return False, f"Ошибка при чтении файла: {str(e)}"

        return True, ""