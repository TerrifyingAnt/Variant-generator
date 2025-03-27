import json
import random
import os
import numpy as np
from typing import Dict, List, Any, Union, Tuple

def generate_transport_task(suppliers_count: int, consumers_count: int, 
                            min_supply: int = 10, max_supply: int = 100,
                            min_cost: int = 1, max_cost: int = 20) -> Dict[str, Any]:
    """
    Генерирует условие транспортной задачи закрытого типа.
    
    Параметры:
    suppliers_count (int): Количество поставщиков
    consumers_count (int): Количество потребителей
    min_supply (int): Минимальное значение предложения/спроса
    max_supply (int): Максимальное значение предложения/спроса
    min_cost (int): Минимальная стоимость перевозки единицы товара
    max_cost (int): Максимальная стоимость перевозки единицы товара
    
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
        "type": "transport_task",
        "suppliers": suppliers,
        "consumers": consumers,
        "costs": costs,
        "total_supply": total_supply,
        "total_demand": sum(consumers.values())
    }
    
    return task_data

def generate_lp_problem(num_variables: int = 2, 
                        num_constraints: int = 3,
                        integer_coefficients: bool = True,
                        seed: int = None) -> Dict[str, Any]:
    """
    Генерирует задачу линейного программирования.
    
    Параметры:
    num_variables (int): Количество переменных
    num_constraints (int): Количество ограничений
    integer_coefficients (bool): Если True, генерирует целочисленные коэффициенты
    seed (int): Зерно для воспроизводимости результатов
    
    Возвращает:
    Dict[str, Any]: Данные сгенерированной задачи
    """
    if seed is not None:
        np.random.seed(seed)
        random.seed(seed)
    
    # Решаем, максимизация или минимизация
    maximize = random.choice([True, False])
    
    # Генерируем коэффициенты целевой функции
    if integer_coefficients:
        c = np.random.randint(-10, 11, size=num_variables).tolist()
    else:
        c = (np.random.rand(num_variables) * 20 - 10).tolist()
    
    # Генерируем коэффициенты ограничений
    if integer_coefficients:
        A = np.random.randint(-5, 11, size=(num_constraints, num_variables)).tolist()
    else:
        A = (np.random.rand(num_constraints, num_variables) * 15).tolist()
    
    # Генерируем положительные значения правых частей ограничений
    if integer_coefficients:
        b = np.random.randint(1, 31, size=num_constraints).tolist()
    else:
        b = (np.random.rand(num_constraints) * 30 + 1).tolist()
    
    return {
        "type": "lp_problem",
        "c": c,
        "A": A,
        "b": b,
        "maximize": maximize,
        "num_variables": num_variables,
        "num_constraints": num_constraints
    }

def generate_variant(transport_task_params: Dict = None, 
                     lp_problem_params: Dict = None, 
                     variant_number: int = None) -> Dict[str, Any]:
    """
    Генерирует вариант, содержащий две задачи: транспортную и ЛП.
    
    Параметры:
    transport_task_params (Dict): Параметры для генерации транспортной задачи
    lp_problem_params (Dict): Параметры для генерации задачи ЛП
    variant_number (int): Номер варианта
    
    Возвращает:
    Dict[str, Any]: Вариант с двумя задачами
    """
    # Используем параметры по умолчанию, если не указаны
    if transport_task_params is None:
        transport_task_params = {
            "suppliers_count": 3,
            "consumers_count": 4,
            "min_supply": 10,
            "max_supply": 100,
            "min_cost": 1,
            "max_cost": 20
        }
    
    if lp_problem_params is None:
        lp_problem_params = {
            "num_variables": 2,
            "num_constraints": 3,
            "integer_coefficients": True,
            "seed": variant_number  # Используем номер варианта как seed для воспроизводимости
        }
    elif variant_number is not None and "seed" not in lp_problem_params:
        lp_problem_params["seed"] = variant_number
    
    # Генерируем задачи
    transport_task = generate_transport_task(**transport_task_params)
    lp_problem = generate_lp_problem(**lp_problem_params)
    
    # Формируем вариант
    variant = {
        "variant_number": variant_number if variant_number is not None else "unknown",
        "tasks": [
            {
                "task_number": 1,
                "task_data": transport_task
            },
            {
                "task_number": 2,
                "task_data": lp_problem
            }
        ]
    }
    
    return variant

def generate_variants_set(variants_count: int = 10,
                          transport_task_params: Dict = None,
                          lp_problem_params: Dict = None,
                          output_file: str = "variants.json") -> str:
    """
    Генерирует набор вариантов и сохраняет их в JSON файл.
    
    Параметры:
    variants_count (int): Количество вариантов для генерации
    transport_task_params (Dict): Параметры для генерации транспортной задачи
    lp_problem_params (Dict): Параметры для генерации задачи ЛП
    output_file (str): Имя выходного файла
    
    Возвращает:
    str: Путь к сгенерированному файлу
    """
    if variants_count <= 0:
        raise ValueError("Количество вариантов должно быть положительным числом")
    
    # Список для хранения сгенерированных вариантов
    variants = []
    
    # Генерируем необходимое количество вариантов
    for i in range(1, variants_count + 1):
        variant = generate_variant(
            transport_task_params=transport_task_params,
            lp_problem_params=lp_problem_params,
            variant_number=i
        )
        variants.append(variant)
    
    # Формируем итоговую структуру данных
    result_data = {
        "variants": variants,
        "count": variants_count
    }
    
    # Создаем директорию, если она не существует
    os.makedirs(os.path.dirname(output_file) if os.path.dirname(output_file) else '.', exist_ok=True)
    
    # Сохраняем все варианты в один JSON файл
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(result_data, f, ensure_ascii=False, indent=4)
    
    return output_file

if __name__ == "__main__":
    # Пример использования
    output_file = generate_variants_set(
        variants_count=5,  # Генерируем 5 вариантов
        transport_task_params={
            "suppliers_count": 3,
            "consumers_count": 4,
            "min_supply": 10,
            "max_supply": 50,
            "min_cost": 1,
            "max_cost": 10
        },
        lp_problem_params={
            "num_variables": 2,
            "num_constraints": 3,
            "integer_coefficients": True
        },
        output_file="variants.json"
    )
    print(f"Набор вариантов сгенерирован и сохранен в файл: {output_file}") 