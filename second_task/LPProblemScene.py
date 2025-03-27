from manim import *
import numpy as np
from PIL import Image
import os

config.background_color = WHITE
config.pixel_height = 720
config.pixel_width = 720
config.frame_height = 7
config.frame_width = 7

class LPProblemScene(Scene):
    def construct(self, problem_data, image_path):
        """
        Создает визуализацию задачи линейного программирования с помощью Manim.
        
        Параметры:
        problem_data (dict): Данные задачи линейного программирования
        image_path (str): Путь для сохранения изображения
        """
        # Форматирование числа для удаления лишних десятичных знаков
        def format_number(num):
            # Преобразуем в float для обработки целых и дробных чисел
            num_float = float(num)
            # Проверяем, является ли число целым
            if num_float.is_integer():
                return str(int(num_float))
            else:
                return str(num_float)

        # Группа для всех элементов
        all_elements = VGroup()

        # Строим целевую функцию с правильным форматированием
        obj_terms = []
        
        # Обработка первого члена
        if problem_data['c'][0] != 0:
            obj_terms.append(f"{format_number(problem_data['c'][0])}x_1")
        
        # Обработка второго члена
        if problem_data['c'][1] != 0:
            if problem_data['c'][1] > 0:
                prefix = "+ " if obj_terms else ""  # Добавляем "+" только если не первый член
                obj_terms.append(f"{prefix}{format_number(problem_data['c'][1])}x_2")
            else:
                obj_terms.append(f"- {format_number(abs(problem_data['c'][1]))}x_2")
        
        # Обработка крайнего случая, когда все коэффициенты равны нулю
        if not obj_terms:
            obj_terms.append("0")
            
        objective_function = " ".join(obj_terms)
        
        objective_text = MathTex(
            f"f(x) = {objective_function}",
            "\\rightarrow",
            "\\max" if problem_data['maximize'] else "\\min"
        )
        objective_text.color = BLACK
        all_elements.add(objective_text)

        # Форматирование ограничений с правильными знаками
        constraints = VGroup()
        for i, row in enumerate(problem_data['A']):
            # Построение членов ограничения с правильным форматированием
            constraint_terms = []
            
            # Обработка первого члена
            if row[0] != 0:
                constraint_terms.append(f"{format_number(row[0])}x_1")
            
            # Обработка второго члена
            if row[1] != 0:
                if row[1] > 0:
                    prefix = "+ " if constraint_terms else ""  # Добавляем "+" только если не первый член
                    constraint_terms.append(f"{prefix}{format_number(row[1])}x_2")
                else:
                    constraint_terms.append(f"- {format_number(abs(row[1]))}x_2")
            
            # Обработка крайнего случая, когда все коэффициенты равны нулю
            if not constraint_terms:
                constraint_terms.append("0")
                
            constraint_equation = " ".join(constraint_terms)
            
            constraint = MathTex(
                f"{constraint_equation}",
                "\\leq",
                f"{format_number(problem_data['b'][i])}"
            )
            constraints.add(constraint)
        
        constraints.arrange(DOWN)
        constraints.color = BLACK
        
        # Добавляем фигурную скобку слева от ограничений
        brace = Brace(constraints, direction=LEFT)
        brace.color = BLACK
        
        # Группируем скобку и ограничения вместе
        brace_with_constraints = VGroup(brace, constraints)
        all_elements.add(brace_with_constraints)

        # Добавляем условия неотрицательности переменных
        nonnegativity = MathTex("x_1", "\\geq", "0,", "\\quad", "x_2", "\\geq", "0")
        nonnegativity.color = BLACK
        all_elements.add(nonnegativity)

        # Располагаем все элементы вертикально
        all_elements.arrange(DOWN, center=True, buff=0.3)
        
        # Выравниваем всю группу по центру экрана
        all_elements.move_to(ORIGIN)
        
        # Добавляем все элементы на сцену
        self.add(all_elements)

        # Сохраняем изображение
        self.renderer.camera.capture_mobjects(self.mobjects)
        temp_path = "temp_" + image_path
        self.renderer.camera.get_image().save(temp_path)
        
        # Обрезаем изображение, чтобы убрать пустое пространство
        self.crop_image(temp_path, image_path)
    
    def crop_image(self, input_path, output_path, border=30):  # Увеличиваем отступ с 10 до 30
        """
        Обрезает изображение, чтобы убрать пустое пространство.
        
        Параметры:
        input_path (str): Путь к исходному изображению
        output_path (str): Путь для сохранения обрезанного изображения
        border (int): Отступ от содержимого в пикселях
        """
        # Открываем изображение
        img = Image.open(input_path)
        
        # Преобразуем в RGB, если это не так
        if img.mode != 'RGB':
            img = img.convert('RGB')
        
        # Получаем цвет фона (предполагается, что это цвет угловой точки)
        bg_color = img.getpixel((0, 0))
        
        # Создаем маску, где True - это содержимое, а False - фон
        mask = np.array(img) != bg_color
        mask = mask.any(axis=2)
        
        # Находим границы содержимого
        rows = np.any(mask, axis=1)
        cols = np.any(mask, axis=0)
        
        # Проверяем, есть ли содержимое на изображении
        if not np.any(rows) or not np.any(cols):
            print("Внимание: изображение пустое или полностью одного цвета")
            # Сохраняем исходное изображение без обрезки
            img.save("task_images/" + output_path)
            return
        
        # Получаем непустые области
        y_min, y_max = np.where(rows)[0][[0, -1]]
        x_min, x_max = np.where(cols)[0][[0, -1]]
        
        # Добавляем отступ
        y_min = max(0, y_min - border)
        y_max = min(img.height, y_max + border)
        x_min = max(0, x_min - border)
        x_max = min(img.width, x_max + border)
        
        # Обрезаем изображение
        cropped_img = img.crop((x_min, y_min, x_max, y_max))
        
        # Создаем директорию, если её нет
        os.makedirs("task_images", exist_ok=True)
        
        # Сохраняем обрезанное изображение
        cropped_img.save("task_images/" + output_path)
        
        # Удаляем временный файл
        os.remove(input_path)

# Функция для генерации изображения задачи ЛП
def generate_lp_problem_image(problem_data, output_path):
    """
    Генерирует изображение задачи линейного программирования.
    
    Параметры:
    problem_data (dict): Данные задачи линейного программирования
    output_path (str): Путь для сохранения изображения
    """
    config.output_file = output_path
    # Отключаем предпросмотр, чтобы избежать открытия окна
    config.preview = False
    
    scene = LPProblemScene()
    scene.construct(problem_data, output_path)

# Пример использования
if __name__ == "__main__":
    # Пример данных задачи линейного программирования
    problem_data = {
        "c": [2, -3],
        "A": [
            [1, 2],
            [2, 1],
            [1, -1]
        ],
        "b": [10, 12, 4],
        "maximize": True,
        "num_variables": 2,
        "num_constraints": 3
    }
    generate_lp_problem_image(problem_data, "lp_problem.png") 