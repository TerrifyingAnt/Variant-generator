import json
import random
import os
from typing import Dict, List, Any, Union

def generate_transport_task(suppliers_count: int, consumers_count: int, 
                            min_supply: int = 10, max_supply: int = 100,
                            min_cost: int = 1, max_cost: int = 20,
                            output_file: str = "transport_task.json",
                            tasks_count: int = 1) -> str:
    """
    Генерирует условие транспортной задачи закрытого типа.
    
    Параметры:
    suppliers_count (int): Количество поставщиков
    consumers_count (int): Количество потребителей
    min_supply (int): Минимальное значение предложения/спроса
    max_supply (int): Максимальное значение предложения/спроса
    min_cost (int): Минимальная стоимость перевозки единицы товара
    max_cost (int): Максимальная стоимость перевозки единицы товара
    output_file (str): Имя выходного файла JSON
    tasks_count (int): Количество задач для генерации
    
    Возвращает:
    str: Путь к сгенерированному JSON-файлу
    """
    
    if tasks_count <= 0:
        raise ValueError("Количество задач должно быть положительным числом")
    
    # Список для хранения сгенерированных задач
    tasks = []
    
    # Генерируем необходимое количество задач
    for i in range(tasks_count):
        task_data = _generate_single_task(
            suppliers_count, consumers_count, 
            min_supply, max_supply, 
            min_cost, max_cost
        )
        tasks.append(task_data)
    
    # Формируем итоговую структуру данных
    result_data = {
        "tasks": tasks,
        "count": tasks_count
    }
    
    # Создаем директорию, если она не существует
    os.makedirs(os.path.dirname(output_file) if os.path.dirname(output_file) else '.', exist_ok=True)
    
    # Сохраняем все задачи в один JSON файл
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(result_data, f, ensure_ascii=False, indent=4)
    
    return output_file

def _generate_single_task(suppliers_count: int, consumers_count: int, 
                         min_supply: int, max_supply: int,
                         min_cost: int, max_cost: int) -> Dict[str, Any]:
    """
    Генерирует одну транспортную задачу закрытого типа.
    
    Возвращает:
    Dict[str, Any]: Данные сгенерированной задачи
    """
    # Генерируем мощности поставщиков (случайные числа)
    suppliers = {}
    for i in range(1, suppliers_count + 1):
        suppliers[f"A{i}"] = random.randint(min_supply, max_supply)
    
    # Сначала сгенерируем временные значения для потребителей
    temp_consumers = {}
    for j in range(1, consumers_count + 1):
        temp_consumers[f"B{j}"] = random.randint(min_supply, max_supply)
    
    # Рассчитаем общий объем предложения
    total_supply = sum(suppliers.values())
    
    # Рассчитаем коэффициент для корректировки спроса, чтобы сделать задачу закрытой
    temp_total_demand = sum(temp_consumers.values())
    adjustment_factor = total_supply / temp_total_demand
    
    # Скорректируем спрос, чтобы общий объем спроса был равен общему объему предложения
    consumers = {}
    remaining_supply = total_supply
    
    for j, consumer in enumerate(temp_consumers, 1):
        if j == consumers_count:  # Последний потребитель получает остаток
            consumers[consumer] = remaining_supply
        else:
            # Округляем до целого числа
            adjusted_demand = int(temp_consumers[consumer] * adjustment_factor)
            consumers[consumer] = adjusted_demand
            remaining_supply -= adjusted_demand
    
    # Проверка, что суммы равны
    assert sum(suppliers.values()) == sum(consumers.values()), "Сумма предложения должна быть равна сумме спроса"
    
    # Генерируем стоимости перевозок
    costs = {}
    for supplier in suppliers:
        costs[supplier] = {}
        for consumer in consumers:
            costs[supplier][consumer] = random.randint(min_cost, max_cost)
    
    # Формируем данные задачи
    task_data = {
        "suppliers": suppliers,
        "consumers": consumers,
        "costs": costs,
        "total_supply": total_supply,
        "total_demand": sum(consumers.values())
    }
    
    return task_data

if __name__ == "__main__":
    # Пример использования для генерации одной задачи
    output_file = generate_transport_task(
        suppliers_count=3,
        consumers_count=4,
        output_file="transport_task.json"
    )
    print(f"Задача сгенерирована и сохранена в файл: {output_file}")
    
    # Пример использования для генерации нескольких задач
    output_file = generate_transport_task(
        suppliers_count=3,
        consumers_count=4,
        output_file="multiple_transport_tasks.json",
        tasks_count=3
    )
    print(f"Сгенерировано несколько задач и сохранены в файл: {output_file}") 