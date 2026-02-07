import re
from pathlib import Path
from typing import List, Dict, Any

import PyPDF2
from transformers import AutoTokenizer


class PDFTokenizer:
    """
    Класс для токенизации текста из PDF файлов
    """

    def __init__(self, model_name: str = "bert-base-multilingual-cased"):
        """
        Инициализация токенизатора

        Args:
            model_name: название модели для токенизации
        """
        self.tokenizer = AutoTokenizer.from_pretrained(model_name)
        print(f"Загружен токенизатор: {model_name}")
        print(f"Размер словаря: {self.tokenizer.vocab_size}")

    def extract_text_from_pdf(self, pdf_path: str) -> str:
        """
        Извлечение текста из PDF файла

        Args:
            pdf_path: путь к PDF файлу

        Returns:
            str: извлеченный текст
        """
        text = ""

        try:
            with open(pdf_path, "rb") as file:
                pdf_reader = PyPDF2.PdfReader(file)

                for page_num, page in enumerate(pdf_reader.pages, 1):
                    page_text = page.extract_text()
                    if page_text:
                        text += page_text + "\n\n"

            print(f"Извлечено {len(pdf_reader.pages)} страниц из {pdf_path}")

        except Exception as e:
            print(f"Ошибка при чтении PDF {pdf_path}: {str(e)}")
            return ""

        return text

    def clean_text(self, text: str) -> str:
        """
        Очистка текста (базовая)

        Args:
            text: исходный текст

        Returns:
            str: очищенный текст
        """
        # Убираем лишние пробелы
        text = re.sub(r"\s+", " ", text)
        # Убираем специальные символы (оставляем только буквы, цифры, пунктуацию)
        text = re.sub(r"[^\w\s.,!?-]", " ", text)

        return text.strip()

    def tokenize_pdf(self, pdf_path: str, max_tokens: int = None) -> Dict[str, Any]:
        """
        Токенизация текста из PDF

        Args:
            pdf_path: путь к PDF файлу
            max_tokens: максимальное количество токенов (если нужно обрезать)

        Returns:
            Dict с результатами токенизации
        """
        # 1. Проверяем файл
        if not Path(pdf_path).exists():
            return {"error": f"Файл {pdf_path} не найден"}

        # 2. Извлекаем текст
        raw_text = self.extract_text_from_pdf(pdf_path)
        if not raw_text:
            return {"error": f"Не удалось извлечь текст из {pdf_path}"}

        # 3. Очищаем текст
        cleaned_text = self.clean_text(raw_text)

        # 4. Токенизируем
        tokens = self.tokenizer.tokenize(cleaned_text)
        token_ids = self.tokenizer.encode(cleaned_text)

        # 5. Обрезаем если нужно
        if max_tokens and len(tokens) > max_tokens:
            tokens = tokens[:max_tokens]
            token_ids = token_ids[:max_tokens]

        # 6. Собираем статистику
        stats = {
            "file_name": Path(pdf_path).name,
            "raw_text_length": len(raw_text),
            "cleaned_text_length": len(cleaned_text),
            "num_tokens": len(tokens),
            "num_token_ids": len(token_ids),
            "tokens": tokens,
            "token_ids": token_ids,
            "sample_tokens": tokens[:50],  # первые 50 токенов для примера
            "sample_text": (
                cleaned_text[:500] + "..." if len(cleaned_text) > 500 else cleaned_text
            ),
        }

        return stats

    def batch_tokenize(
            self, pdf_paths: List[str], max_tokens: int = None
    ) -> List[Dict[str, Any]]:
        """
        Токенизация нескольких PDF файлов

        Args:
            pdf_paths: список путей к PDF файлам
            max_tokens: максимальное количество токенов на файл

        Returns:
            List[Dict]: результаты для каждого файла
        """
        results = []

        for pdf_path in pdf_paths:
            print(f"\nОбрабатываю: {pdf_path}")
            result = self.tokenize_pdf(pdf_path, max_tokens)
            results.append(result)

        return results

    def save_tokens_to_file(self, tokens_data: Dict[str, Any], output_file: str):
        """
        Сохранение токенов в файл

        Args:
            tokens_data: результат токенизации
            output_file: путь к выходному файлу
        """
        if "error" in tokens_data:
            print(f"Ошибка: {tokens_data['error']}")
            return

        with open(output_file, "w", encoding="utf-8") as f:
            f.write(f"Файл: {tokens_data['file_name']}\n")
            f.write(f"Длина текста: {tokens_data['cleaned_text_length']} символов\n")
            f.write(f"Количество токенов: {tokens_data['num_tokens']}\n")
            f.write(f"\nТокены:\n")

            # Записываем токены группами по 20
            for i in range(0, len(tokens_data["tokens"]), 20):
                f.write(" ".join(tokens_data["tokens"][i: i + 20]) + "\n")


def test_tokenizer():
    """
    Тестирование токенизатора
    """
    # Создаем токенизатор
    tokenizer = PDFTokenizer()

    # Тестовый PDF
    pdf_file = r"C:\Users\6muni\Documents\sample.pdf"

    if Path(pdf_file).exists():
        # Токенизируем
        result = tokenizer.tokenize_pdf(pdf_file, max_tokens=200)

        if "error" not in result:
            print("\n=== Результаты токенизации ===")
            print(f"Файл: {result['file_name']}")
            print(f"Длина текста: {result['cleaned_text_length']} символов")
            print(f"Количество токенов: {result['num_tokens']}")
            print(f"\nПервые 20 токенов: {' '.join(result['tokens'][:20])}")
            print(f"\nОбразец текста:\n{result['sample_text']}")

            # Сохраняем в файл
            tokenizer.save_tokens_to_file(result, "tokens_output.txt")
            print("\nРезультаты сохранены в tokens_output.txt")
    else:
        print(f"Файл {pdf_file} не найден. Создай тестовый PDF или укажи путь.")

        # Тест на примере текста
        test_text = "Это тестовый текст для проверки токенизатора из PDF."
        tokens = tokenizer.tokenizer.tokenize(test_text)
        print(f"\nТестовый текст: {test_text}")
        print(f"Токены: {tokens}")
        print(f"ID токенов: {tokenizer.tokenizer.encode(test_text)}")


if __name__ == "__main__":
    test_tokenizer()
