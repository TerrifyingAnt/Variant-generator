import json
import os
import numpy as np
from reportlab.lib.pagesizes import letter, A4
from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from PIL import Image
from TransportTaskScene import generate_transport_task_image
from LPProblemScene import generate_lp_problem_image

# Регистрация шрифта Arial, который поддерживает кириллицу
try:
    pdfmetrics.registerFont(TTFont('Arial', 'arial.ttf'))
    font_name = 'Arial'
except:
    # Если Arial не найден, используем стандартный шрифт
    font_name = 'Helvetica'

def create_variants_pdf(variants_data, output_dir="variants_pdf"):
    """
    Создает PDF-файлы с вариантами заданий.
    
    Параметры:
    variants_data (dict): Данные вариантов с задачами
    output_dir (str): Директория для сохранения PDF-файлов
    """
    # Создаем директорию для PDF, если она не существует
    os.makedirs(output_dir, exist_ok=True)
    # Создаем директорию для изображений, если она не существует
    os.makedirs("task_images", exist_ok=True)
    
    variants = variants_data["variants"]
    
    for variant in variants:
        variant_number = variant["variant_number"]
        pdf_path = f"{output_dir}/Вариант_{variant_number}.pdf"
        
        # Создаем PDF для текущего варианта
        c = canvas.Canvas(pdf_path, pagesize=A4)
        width, height = A4
        y = height - 50  # Начальная позиция Y
        
        # Заголовок варианта
        c.setFont(font_name, 14)
        title_text = f"Контрольная работа. Вариант {variant_number}"
        c.drawString(70, y, title_text)  # Увеличиваем отступ с 50 до 70
        y -= 40  # Увеличиваем отступ с 30 до 40
        
        # Обрабатываем задачи в варианте
        for task in variant["tasks"]:
            task_number = task["task_number"]
            task_data = task["task_data"]
            task_type = task_data["type"]
            
            # Заголовок задачи
            c.setFont(font_name, 12)
            c.drawString(70, y, f"Задача {task_number}.")  # Увеличиваем отступ с 50 до 70
            y -= 20
            
            if task_type == "transport_task":
                # Генерируем изображение для транспортной задачи
                image_path = f"task_{variant_number}_{task_number}_transport.png"
                generate_transport_task_image(task_data, image_path)
                c.drawString(70, y - 15, "Для производства трех партий смартфонов используются батареи четырех")
                c.drawString(70, y - 30, "производителей. Запасы батарей каждого производителя (аi), потребности")
                c.drawString(70, y - 45, "в батареях для производства каждой партии смартфонов (bi) и стоимости")
                c.drawString(70, y - 60, "заданы матрицей. Составить план покупки батарей, при котором потребности")
                c.drawString(70, y - 75, "в них каждой партии смартфонов были бы удовлетворены при наименьшей общей")
                c.drawString(70, y - 90, "стоимости. Решить задачу методом потенциалов.(5 баллов)")  # Перемещаем текст с изображения в PDF
                y -= 260
                
                # Добавляем изображение
                img_path = os.path.join("task_images", image_path)
                if os.path.exists(img_path):
                    img = Image.open(img_path)
                    img_width, img_height = img.size
                    
                    # Масштабируем изображение, уменьшая размер
                    display_width = min(width - 140, 250)  # Уменьшаем с 300 до 250 и увеличиваем отступы
                    display_height = img_height * (display_width / img_width)
                    
                    # Проверяем, поместится ли изображение на текущей странице
                    if y - display_height < 70:  # Увеличиваем нижний отступ с 50 до 70
                        c.showPage()
                        y = height - 70  # Увеличиваем верхний отступ с 50 до 70
                    
                    # Рисуем изображение с увеличенным левым отступом
                    c.drawImage(img_path, 70, y - display_height, width=display_width, preserveAspectRatio=True)
                else:
                    c.drawString(70, y, "Изображение не найдено")  # Увеличиваем отступ с 50 до 70

                                
                y -= 20  # Увеличиваем отступ между задачами с 15 до 20
                
            elif task_type == "lp_problem":
                # Генерируем изображение для задачи ЛП
                image_path = f"task_{variant_number}_{task_number}_lp.png"
                generate_lp_problem_image(task_data, image_path)
                
                # Добавляем описание задачи
                c.setFont(font_name, 12)  
                c.drawString(70, y, "Задача линейного программирования:")  # Увеличиваем отступ с 50 до 70
                y -= 125
                
                # Добавляем изображение
                img_path = os.path.join("task_images", image_path)
                if os.path.exists(img_path):
                    img = Image.open(img_path)
                    img_width, img_height = img.size
                    
                    # Масштабируем изображение, уменьшая размер
                    display_width = min(width - 140, 250)  # Уменьшаем с 300 до 250 и увеличиваем отступы
                    display_height = img_height * (display_width / img_width)
                    
                    # Проверяем, поместится ли изображение на текущей странице
                    if y - display_height < 70:  # Увеличиваем нижний отступ с 50 до 70
                        c.showPage()
                        y = height - 70  # Увеличиваем верхний отступ с 50 до 70
                    
                    # Рисуем изображение с увеличенным левым отступом
                    c.drawImage(img_path, 70, y - display_height, width=display_width, preserveAspectRatio=True)
                else:
                    c.drawString(70, y, "Изображение не найдено")  # Увеличиваем отступ с 50 до 70
                y -= 30
                
                # Добавляем задание
                c.setFont(font_name, 12)  # Уменьшаем шрифт с 10 до 9
                task_text = [
                    "a) Решить задачу линейного программирования графически. (3 балла)",
                    "b) Записать задачу ЛП, двойственную данной. (2 балла)",
                    "c) Решить задачу ЛП симплекс-методом. (5 баллов)"
                ]
                for line in task_text:
                    c.drawString(70, y, line)  # Увеличиваем отступ с 50 до 70
                    y -= 15
                
                y -= 20  # Увеличиваем отступ между задачами с 15 до 20
        
        # Сохраняем PDF
        c.save()
        print(f"Создан PDF-файл варианта {variant_number}: {pdf_path}")

def generate_variants_pdf(variants_json_path, output_dir="variants_pdf"):
    """
    Генерирует PDF-файлы для всех вариантов из JSON-файла.
    
    Параметры:
    variants_json_path (str): Путь к JSON-файлу с вариантами
    output_dir (str): Директория для сохранения PDF-файлов
    """
    try:
        with open(variants_json_path, 'r', encoding='utf-8') as f:
            variants_data = json.load(f)
        
        create_variants_pdf(variants_data, output_dir)
        print(f"Успешно сгенерированы PDF-файлы вариантов в директории {output_dir}")
        
    except FileNotFoundError:
        print(f"Ошибка: файл {variants_json_path} не найден")
    except json.JSONDecodeError:
        print(f"Ошибка: не удалось декодировать JSON из файла {variants_json_path}")
    except Exception as e:
        print(f"Произошла ошибка: {e}")

if __name__ == "__main__":
    # Пример использования
    generate_variants_pdf("variants.json", "variants_pdf") 