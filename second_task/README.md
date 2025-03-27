# Генератор вариантов с задачами по исследованию операций

Этот проект содержит скрипты для генерации вариантов заданий по исследованию операций, включая транспортные задачи закрытого типа и задачи линейного программирования, а также их визуализацию и создание PDF-файлов.

## Содержимое проекта

- `combined_task_generator.py` - генерирует наборы вариантов с задачами транспортной задачи и задачи ЛП
- `TransportTaskScene.py` - визуализация транспортной задачи с помощью manim
- `LPProblemScene.py` - визуализация задачи линейного программирования с помощью manim
- `generate_pdf.py` - создание PDF-файлов с вариантами
- `run_generator.py` - скрипт для удобного запуска всего процесса

## Установка зависимостей

```bash
pip install -r requirements.txt
```

## Быстрый запуск

Для генерации вариантов и создания PDF-файлов можно использовать скрипт `run_generator.py`:

```bash
python run_generator.py
```

По умолчанию это создаст 10 вариантов и сохранит их в директории `variants_pdf`.

### Опции командной строки

```
usage: run_generator.py [-h] [-n NUM_VARIANTS] [-s SUPPLIERS] [-c CONSUMERS]
                         [-v VARIABLES] [-k CONSTRAINTS] [-o OUTPUT_DIR]
                         [-j JSON_FILE]

Генерация вариантов заданий и создание PDF-файлов

options:
  -h, --help            показать это сообщение и выйти
  -n NUM_VARIANTS, --num-variants NUM_VARIANTS
                        Количество вариантов (по умолчанию: 10)
  -s SUPPLIERS, --suppliers SUPPLIERS
                        Количество поставщиков для транспортной задачи (по умолчанию: 3)
  -c CONSUMERS, --consumers CONSUMERS
                        Количество потребителей для транспортной задачи (по умолчанию: 4)
  -v VARIABLES, --variables VARIABLES
                        Количество переменных для задачи ЛП (по умолчанию: 2)
  -k CONSTRAINTS, --constraints CONSTRAINTS
                        Количество ограничений для задачи ЛП (по умолчанию: 3)
  -o OUTPUT_DIR, --output-dir OUTPUT_DIR
                        Директория для сохранения PDF-файлов (по умолчанию: variants_pdf)
  -j JSON_FILE, --json-file JSON_FILE
                        Имя JSON-файла для сохранения вариантов (по умолчанию: variants.json)
```

## Пример

Создание 5 вариантов с 2 поставщиками и 3 потребителями для транспортной задачи:

```bash
python run_generator.py -n 5 -s 2 -c 3
```

## Генератор вариантов (combined_task_generator.py)

Этот скрипт создает набор вариантов, каждый из которых содержит два задания:
1. Транспортная задача закрытого типа
2. Задача линейного программирования

### Использование генератора вариантов в своем коде

```python
from combined_task_generator import generate_variants_set

# Генерация набора из 5 вариантов
output_file = generate_variants_set(
    variants_count=5,  # Количество вариантов
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
```

## Визуализация задач

### Визуализация транспортной задачи

```python
from TransportTaskScene import generate_transport_task_image

transport_task = {
    "suppliers": {"A1": 50, "A2": 75},
    "consumers": {"B1": 30, "B2": 40, "B3": 55},
    "costs": {
        "A1": {"B1": 5, "B2": 3, "B3": 7},
        "A2": {"B1": 2, "B2": 8, "B3": 4}
    }
}

generate_transport_task_image(transport_task, "transport_task.png")
```

### Визуализация задачи линейного программирования

```python
from LPProblemScene import generate_lp_problem_image

lp_problem = {
    "c": [2, -3],
    "A": [[1, 2], [2, 1], [1, -1]],
    "b": [10, 12, 4],
    "maximize": True
}

generate_lp_problem_image(lp_problem, "lp_problem.png")
```

## Генерация PDF

```python
from generate_pdf import generate_variants_pdf

# Генерация PDF-файлов из JSON-файла с вариантами
generate_variants_pdf("variants.json", "output_pdf_directory")
```

## Формат выходного JSON-файла для вариантов

```json
{
    "variants": [
        {
            "variant_number": 1,
            "tasks": [
                {
                    "task_number": 1,
                    "task_data": {
                        "type": "transport_task",
                        "suppliers": {
                            "A1": 45,
                            "A2": 30,
                            "A3": 25
                        },
                        "consumers": {
                            "B1": 20,
                            "B2": 30,
                            "B3": 35,
                            "B4": 15
                        },
                        "costs": {
                            "A1": {
                                "B1": 3,
                                "B2": 7,
                                "B3": 2,
                                "B4": 8
                            },
                            "A2": {
                                "B1": 5,
                                "B2": 4,
                                "B3": 6,
                                "B4": 3
                            },
                            "A3": {
                                "B1": 2,
                                "B2": 6,
                                "B3": 9,
                                "B4": 5
                            }
                        },
                        "total_supply": 100,
                        "total_demand": 100
                    }
                },
                {
                    "task_number": 2,
                    "task_data": {
                        "type": "lp_problem",
                        "c": [5, -3],
                        "A": [
                            [2, 1],
                            [1, 3],
                            [-1, 1]
                        ],
                        "b": [10, 15, 4],
                        "maximize": true,
                        "num_variables": 2,
                        "num_constraints": 3
                    }
                }
            ]
        }
    ],
    "count": 1
}
``` 