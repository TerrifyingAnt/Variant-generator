from manim import *
import numpy as np
from PIL import Image

config.background_color = WHITE
config.pixel_height = 720
config.pixel_width = 2500  # Оставляем большую ширину для полного отображения таблицы
config.frame_height = 7
config.frame_width = 20  # Увеличиваем ширину кадра для лучшего отображения

class TransportTaskScene(Scene):
    def construct(self, transport_task, image_path):
        """
        Создает визуализацию транспортной задачи с помощью Manim.
        
        Параметры:
        transport_task (dict): Данные транспортной задачи
        image_path (str): Путь для сохранения изображения
        """
        # Группа для всех элементов
        all_elements = VGroup()
        
        # Извлекаем данные
        suppliers = transport_task["suppliers"]
        consumers = transport_task["consumers"]
        costs = transport_task["costs"]
        
        # Создаем таблицу поставщиков и потребителей
        table_group = self.create_transport_table(suppliers, consumers, costs)
        all_elements.add(table_group)
        
        # Выравниваем по центру экрана
        #all_elements.move_to(ORIGIN)
        
        # Добавляем все элементы на сцену
        self.add(all_elements)

        # Сохраняем изображение
        self.renderer.camera.capture_mobjects(self.mobjects)
        temp_path = "temp_" + image_path
        self.renderer.camera.get_image().save(temp_path)
        
        self.crop_image(temp_path, image_path)
    
    def create_transport_table(self, suppliers, consumers, costs):
        """
        Создает таблицу с данными транспортной задачи.
        
        Параметры:
        suppliers (dict): Словарь поставщиков и их запасов
        consumers (dict): Словарь потребителей и их потребностей
        costs (dict): Словарь стоимостей перевозок
        
        Возвращает:
        VGroup: Группа Manim-объектов, составляющих таблицу
        """
        table_group = VGroup()
        
        # Количество строк и столбцов для таблицы
        rows = len(suppliers) + 1  # +1 для заголовка потребителей
        cols = len(consumers) + 2  # +2 для поставщиков и их запасов
        
        # Создаем сетку для таблицы
        cell_width = 1.2
        cell_height = 0.8
        grid = []
        
        for i in range(rows):
            grid_row = []
            for j in range(cols):
                cell = Rectangle(width=cell_width, height=cell_height, color=BLACK, fill_opacity=0)
                cell.move_to([j * cell_width - (cols-1) * cell_width / 2, 
                             -i * cell_height + (rows-1) * cell_height / 2, 0])
                grid_row.append(cell)
                table_group.add(cell)
            grid.append(grid_row)
        
        # Добавляем заголовки для потребителей
        for j, consumer in enumerate(consumers.keys(), 1):
            consumer_text = Text(consumer, font="Arial", color=BLACK, font_size=24)
            consumer_text.move_to(grid[0][j].get_center())
            table_group.add(consumer_text)
        
        # # Добавляем заголовок "Запас" в последний столбец
        # supply_text = Text("Запас", font="Arial", color=BLACK, font_size=24)
        # supply_text.move_to(grid[0][cols-1].get_center())
        # table_group.add(supply_text)
        
        # Добавляем заголовки для поставщиков и их запасы
        for i, supplier in enumerate(suppliers.keys(), 1):
            supplier_text = Text(supplier, font="Arial", color=BLACK, font_size=24)
            supplier_text.move_to(grid[i][0].get_center())
            table_group.add(supplier_text)
            
            # Добавляем запасы поставщиков
            supply = suppliers[supplier]
            supply_text = Text(str(supply), font="Arial", color=BLACK, font_size=24)
            supply_text.move_to(grid[i][cols-1].get_center())
            table_group.add(supply_text)
            
            # Добавляем стоимости перевозок
            for j, consumer in enumerate(consumers.keys(), 1):
                cost = costs[supplier][consumer]
                cost_text = Text(str(cost), font="Arial", color=BLACK, font_size=24)
                cost_text.move_to(grid[i][j].get_center())
                table_group.add(cost_text)
        
        # Добавляем последнюю строку с потребностями
        bottom_row = Rectangle(
            width=cell_width * (cols-1), 
            height=cell_height, 
            color=BLACK, 
            fill_opacity=0
        )
        bottom_row.next_to(grid[rows-1][0], DOWN, buff=0)
        table_group.add(bottom_row)
        
        # Добавляем текст "Потребность" в первую ячейку последней строки
        # need_label = Text("Потребность", font="Arial", color=BLACK, font_size=24)
        # need_label.move_to(grid[rows-1][0].get_center() + DOWN * cell_height)
        # table_group.add(need_label)

        # Добавляем значения потребностей
        for j, consumer in enumerate(consumers.keys(), 1):
            demand = consumers[consumer]
            demand_cell = Rectangle(
                width=cell_width, 
                height=cell_height, 
                color=BLACK, 
                fill_opacity=0
            )
            demand_cell.move_to(grid[rows-1][j].get_center() + DOWN * cell_height)
            table_group.add(demand_cell)
            
            demand_text = Text(str(demand), font="Arial", color=BLACK, font_size=24)
            demand_text.move_to(demand_cell.get_center())
            table_group.add(demand_text)
        
        return table_group
    
    def crop_image(self, input_path, output_path, border=50):  # Увеличиваем отступ до 50
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
        import os
        os.makedirs("task_images", exist_ok=True)
        
        # Сохраняем обрезанное изображение
        cropped_img.save("task_images/" + output_path)
        
        # Удаляем временный файл
        os.remove(input_path)

# Функция для генерации изображения транспортной задачи
def generate_transport_task_image(transport_task, output_path):
    """
    Генерирует изображение транспортной задачи.
    
    Параметры:
    transport_task (dict): Данные транспортной задачи
    output_path (str): Путь для сохранения изображения
    """
    config.output_file = output_path
    # Отключаем предпросмотр, чтобы избежать открытия окна
    config.preview = False
    
    scene = TransportTaskScene()
    scene.construct(transport_task, output_path)

# Пример использования
if __name__ == "__main__":
    # Пример данных транспортной задачи
    transport_task = {
        "suppliers": {
            "A1": 50,
            "A2": 75,
            "A3": 25
        },
        "consumers": {
            "B1": 30,
            "B2": 40,
            "B3": 50,
            "B4": 30
        },
        "costs": {
            "A1": {
                "B1": 5,
                "B2": 10,
                "B3": 3,
                "B4": 7
            },
            "A2": {
                "B1": 8,
                "B2": 4,
                "B3": 6,
                "B4": 9
            },
            "A3": {
                "B1": 2,
                "B2": 7,
                "B3": 12,
                "B4": 5
            }
        },
        "total_supply": 150,
        "total_demand": 150
    }
    generate_transport_task_image(transport_task, "transport_task.png") 