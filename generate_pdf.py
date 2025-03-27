import json
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from ProblemScene import *
from PIL import Image
import os

# Регистрация шрифта Arial, который поддерживает кириллицу
pdfmetrics.registerFont(TTFont('Arial', 'arial.ttf'))

def create_pdf(data):
    for idx, el in enumerate(data):
        c = canvas.Canvas(f"vars/Вариант {idx+1}.pdf", pagesize=letter)
        width, height = letter
        y = height - 50 
        
        # Заголовок
        title_text = f"Контрольная работа номер 1, вариант {idx + 1}"
        c.setFont("Arial", 14)  # Установка шрифта Arial
        c.drawString(50, y, title_text)
        y -= 20
        c.drawString(50, y, "Задача №1")
        y -= 20  # Space before image
        
        # Generate the image
        image_path = f"problem_{idx}.png"
        scene = ProblemScene()
        scene.construct(el, image_path)
        
        # Get the image dimensions
        img_path = os.path.join("task_images", image_path)
        if os.path.exists(img_path):
            img = Image.open(img_path)
            img_width, img_height = img.size
            
            # Calculate the height in PDF points (maintaining aspect ratio)
            display_width = 200  # Width we want to display in PDF
            display_height = img_height * (display_width / img_width)
            
            # Draw the image
            c.drawImage(img_path, 50, 470, width=200, preserveAspectRatio=True)

            y -= (img_height * 200) / img_width

            
            # Update y position based on actual image height
            #y -= (display_height + 20)  # Image height plus some padding
        else:
            # Fallback if image doesn't exist
            c.drawString(50, y - 80, "Изображение отсутствует")
            y -= 40  # Default offset if no image

        # Добавление текста после изображения
        tasks = [
            "a) Решить задачу линейного программирования графически. Составить эквивалентную ",
            "    каноническую задачу. (3 балла)",
            "b) Записать задачу ЛП, двойственную данной. (2 балла)",
            "c) Решить задачу ЛП симплекс-методом. (5 баллов)"
        ]
        c.setFont("Arial", 12)  # Установка шрифта Arial для текста заданий
        for task in tasks:
            c.drawString(50, y - 20, task)
            y -= 20
        y -= 30  # Additional space between sections

        c.save()

with open('lp_problems.json', 'r') as file:
    data = json.load(file)
    create_pdf(data)