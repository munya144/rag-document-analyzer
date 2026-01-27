from pathlib import Path
import pdfplumber


def load_pdf(file_path: str) -> dict:
    """
    Загружает PDF и извлекает текст по страницам.

    Аргументы:
        file_path: Путь к PDF файлу

    Возвращает:
        dict: Всегда содержит ключи:
            - "success": bool (успешно ли выполнено)
            - "file_path": str
            - "total_pages": int
            - "pages": list
            - "error": str (только если success=False)
    """
    # Всегда возвращаем структуру с одинаковыми ключами
    base_structure = {
        "success": False,
        "file_path": file_path,
        "total_pages": 0,
        "pages": [],
        "error": ""
    }

    # Проверяем, существует ли файл
    path = Path(file_path)
    if not path.exists():
        base_structure["error"] = f"Файл не найден: {file_path}"
        return base_structure

    # Проверяем, что это файл (не директория)
    if not path.is_file():
        base_structure["error"] = f"Это не файл, а директория: {file_path}"
        return base_structure

    try:
        # Открываем PDF
        with pdfplumber.open(file_path) as pdf:
            total_pages = len(pdf.pages)
            pages_data = []

            # Читаем каждую страницу
            for i in range(total_pages):
                page_num = i + 1
                try:
                    page = pdf.pages[i]
                    text = page.extract_text()

                    # Если текст None или пустой
                    if text is None:
                        text = ""

                    pages_data.append({
                        "page_num": page_num,
                        "text": text
                    })

                except Exception as e:
                    # Ошибка на конкретной странице - добавляем пустую страницу
                    pages_data.append({
                        "page_num": page_num,
                        "text": f"[Ошибка чтения страницы: {str(e)}]"
                    })

            # Успешный результат
            return {
                "success": True,
                "file_path": str(path.absolute()),
                "total_pages": total_pages,
                "pages": pages_data,
                "error": ""
            }

    except Exception as e:
        # Ошибка при открытии файла
        base_structure["error"] = f"Ошибка при чтении PDF: {str(e)}"
        return base_structure

