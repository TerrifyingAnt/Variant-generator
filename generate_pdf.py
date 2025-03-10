import json
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from ProblemScene import *

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
        image_path = f"problem_{idx}.png"
        scene = ProblemScene()
        scene.construct(el, image_path)

        # Вставка изображения
        c.drawImage("task_images/" + image_path, 50, 440, width=200, preserveAspectRatio=True)
        y -= 145  # Adjust the position for the next element

        # Добавление текста после изображения
        tasks = [
            "a) Решить задачу линейного программирования графически. Составить эквивалентную ",
            "    каноническую задачу. (3 балла)",
            "b) Записать задачу ЛП, двойственную данной. (2 балла)",
            "c) Решить задачу ЛП симплекс-методом. (5 баллов)"
        ]
        c.setFont("Arial", 12)  # Установка шрифта Arial для текста заданий
        for task in tasks:
            c.drawString(50, y, task)
            y -= 20
        y -= 30  # Additional space between sections

        c.save()

with open('lp_problems.json', 'r') as file:
    data = json.load(file)
    create_pdf(data)