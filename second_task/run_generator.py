#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Скрипт для генерации вариантов заданий и создания PDF-файлов.
"""

import os
import argparse
from combined_task_generator import generate_variants_set
from generate_pdf import generate_variants_pdf

def main():
    """
    Основная функция для генерации вариантов и PDF.
    """
    # Создаем парсер аргументов командной строки
    parser = argparse.ArgumentParser(
        description="Генерация вариантов заданий и создание PDF-файлов"
    )
    
    # Добавляем аргументы
    parser.add_argument(
        "-n", "--num-variants", 
        type=int, 
        default=10, 
        help="Количество вариантов (по умолчанию: 10)"
    )
    
    parser.add_argument(
        "-s", "--suppliers", 
        type=int, 
        default=3, 
        help="Количество поставщиков для транспортной задачи (по умолчанию: 3)"
    )
    
    parser.add_argument(
        "-c", "--consumers", 
        type=int, 
        default=4, 
        help="Количество потребителей для транспортной задачи (по умолчанию: 4)"
    )
    
    parser.add_argument(
        "-v", "--variables", 
        type=int, 
        default=2, 
        help="Количество переменных для задачи ЛП (по умолчанию: 2)"
    )
    
    parser.add_argument(
        "-k", "--constraints", 
        type=int, 
        default=3, 
        help="Количество ограничений для задачи ЛП (по умолчанию: 3)"
    )
    
    parser.add_argument(
        "-o", "--output-dir", 
        type=str, 
        default="variants_pdf", 
        help="Директория для сохранения PDF-файлов (по умолчанию: variants_pdf)"
    )
    
    parser.add_argument(
        "-j", "--json-file", 
        type=str, 
        default="variants.json", 
        help="Имя JSON-файла для сохранения вариантов (по умолчанию: variants.json)"
    )
    
    # Парсим аргументы
    args = parser.parse_args()
    
    # Выводим информацию о запуске
    print(f"Запуск генератора вариантов:")
    print(f"Количество вариантов: {args.num_variants}")
    print(f"Транспортная задача: {args.suppliers} поставщиков, {args.consumers} потребителей")
    print(f"Задача ЛП: {args.variables} переменных, {args.constraints} ограничений")
    print(f"JSON-файл: {args.json_file}")
    print(f"Директория для PDF: {args.output_dir}")
    print("\n" + "-" * 50 + "\n")
    
    # Шаг 1: Генерируем варианты заданий и сохраняем в JSON
    print("Шаг 1: Генерация вариантов заданий...")
    json_path = generate_variants_set(
        variants_count=args.num_variants,
        transport_task_params={
            "suppliers_count": args.suppliers,
            "consumers_count": args.consumers,
            "min_supply": 10,
            "max_supply": 50,
            "min_cost": 1,
            "max_cost": 10
        },
        lp_problem_params={
            "num_variables": args.variables,
            "num_constraints": args.constraints,
            "integer_coefficients": True
        },
        output_file=args.json_file
    )
    print(f"Готово. Варианты сохранены в файл: {json_path}")
    print("\n" + "-" * 50 + "\n")
    
    # Шаг 2: Создаем PDF-файлы вариантов
    print("Шаг 2: Создание PDF-файлов...")
    generate_variants_pdf(args.json_file, args.output_dir)
    print(f"Готово. PDF-файлы сохранены в директории: {args.output_dir}")
    print("\n" + "-" * 50 + "\n")
    
    # Выводим итоговую информацию
    pdf_files = [f for f in os.listdir(args.output_dir) if f.endswith('.pdf')]
    print(f"Итоги: создано {len(pdf_files)} PDF-файлов вариантов")
    print("Процесс завершен успешно!")

if __name__ == "__main__":
    main() 