import numpy as np
import random
from typing import Dict, Tuple, List
from simplex_solver import *
import os
from pathlib import Path
import json

def generate_random_lp_problem(num_variables: int = 2, 
                              num_constraints: int = 3,
                              integer_coefficients: bool = True,
                              seed: int = None) -> Dict:
    """
    Generate a random linear programming problem.
    
    Parameters:
    -----------
    num_variables : int
        Number of decision variables
    num_constraints : int
        Number of constraints
    integer_coefficients : bool
        If True, generates integer coefficients, otherwise uses floating point
    seed : int
        Random seed for reproducibility
    
    Returns:
    --------
    Dict containing:
        - c: objective function coefficients
        - A: constraint coefficients matrix
        - b: constraint right-hand side values
        - maximize: boolean indicating if it's a maximization problem
    """
    if seed is not None:
        np.random.seed(seed)
        random.seed(seed)
    
    # Decide if it's a maximization or minimization problem
    maximize = random.choice([True, False])
    
    # Generate objective function coefficients
    if integer_coefficients:
        c = np.random.randint(-10, 11, size=num_variables).tolist()
    else:
        c = (np.random.rand(num_variables) * 20 - 10).tolist()
    
    # Generate constraint coefficients
    if integer_coefficients:
        A = np.random.randint(-5, 11, size=(num_constraints, num_variables)).tolist()
    else:
        A = (np.random.rand(num_constraints, num_variables) * 15).tolist()
    
    # Generate positive right-hand side values for constraints
    if integer_coefficients:
        b = np.random.randint(1, 31, size=num_constraints).tolist()
    else:
        b = (np.random.rand(num_constraints) * 30 + 1).tolist()
    
    return {
        "c": c,
        "A": A,
        "b": b,
        "maximize": maximize
    }

def prepare_problem_for_simplex(problem: Dict) -> Dict:
    """
    Prepare a problem for the simplex solver by ensuring all RHS values are non-negative.
    
    Parameters:
    -----------
    problem : Dict
        The problem dictionary
    
    Returns:
    --------
    Dict
        The prepared problem dictionary
    """
    # Create a copy of the problem to avoid modifying the original
    prepared = {
        "c": problem["c"].copy(),
        "A": [row.copy() for row in problem["A"]],
        "b": problem["b"].copy(),
        "maximize": problem["maximize"]
    }
    
    # Handle negative RHS values by multiplying both sides of the constraint by -1
    for i in range(len(prepared["b"])):
        if prepared["b"][i] < 0:
            prepared["b"][i] = -prepared["b"][i]
            prepared["A"][i] = [-coef for coef in prepared["A"][i]]
    
    if "name" in problem:
        prepared["name"] = problem["name"]
    if "description" in problem:
        prepared["description"] = problem["description"]
    
    return prepared

def create_problem_batch(num_random: int = 3, num_constraints: int = 3) -> List[Dict]:
    """
    Create a batch of LP problems with both random and structured instances.
    
    Parameters:
    -----------
    num_random : int
        Number of random problems to generate
    
    Returns:
    --------
    List of problem dictionaries
    """
    problems = []
    
    # Add random problems
    for i in range(num_random):
        problem = generate_random_lp_problem(num_variables=2, num_constraints=num_constraints, seed=i)
        problem["name"] = f"Random Problem {i+1}"
        problem["description"] = f"Randomly generated {'maximization' if problem['maximize'] else 'minimization'} problem with 3 variables"
        problems.append(problem)
        
    return problems

def solve_lp_with_steps(c: List[float], A: List[List[float]], b: List[float], 
                       maximize: bool = True) -> dict:
    """
    Solve a linear programming problem and record all solution steps
    
    Parameters:
    -----------
    c: objective function coefficients
    A: constraint coefficients matrix
    b: constraint values
    maximize: True if maximizing, False if minimizing
    
    Returns:
    --------
    Dictionary with complete solution details including all steps
    """
    c_arr = np.array(c, dtype=float)
    A_arr = np.array(A, dtype=float)
    b_arr = np.array(b, dtype=float)
    
    # If minimizing, negate the objective function
    if not maximize:
        c_arr = -c_arr
    
    # Handle negative RHS values by multiplying the corresponding constraints by -1
    constraint_transformations = []
    for i in range(len(b_arr)):
        if b_arr[i] < 0:
            b_arr[i] = -b_arr[i]
            A_arr[i] = -A_arr[i]
            constraint_transformations.append({
                "constraint_index": int(i),
                "transformation": "negated",
                "original_b": float(-b_arr[i]),
                "transformed_b": float(b_arr[i])
            })
    
    solver = SimplexSolver()
    
    # Modified version of the solver code to capture all steps
    # Set up the initial tableau
    solver.setup_problem(c_arr, A_arr, b_arr)
    
    # Store solution steps
    solution_steps = []
    
    # Record any constraint transformations
    if constraint_transformations:
        solution_steps.append({
            "phase": "preprocessing",
            "constraint_transformations": constraint_transformations,
            "message": "Negative RHS values were transformed by multiplying constraints by -1"
        })
    
    # Store initial tableau
    solution_steps.append({
        "iteration": 0,
        "tableau": solver.tableau.tolist(),
        "basic_vars": [int(x) for x in solver.basic_vars],
        "status": "initial"
    })
    
    iteration = 0
    max_iterations = 100
    
    while not solver.is_optimal() and iteration < max_iterations:
        iteration += 1
        
        # Select entering variable
        entering_col = solver.select_entering_var()
        if entering_col == -1:
            solution_steps.append({
                "iteration": iteration,
                "status": "optimal",
                "message": "Optimal solution found"
            })
            break  # Optimal solution found
            
        # Select leaving variable
        try:
            leaving_row, min_ratio = solver.select_leaving_var(entering_col)
            pivot_info = {
                "entering_col": int(entering_col),
                "entering_var": int(entering_col - 1),  # Adjust for tableau indexing
                "leaving_row": int(leaving_row),
                "leaving_var": int(solver.basic_vars[leaving_row]),
                "min_ratio": float(min_ratio)
            }
        except ValueError as e:
            solution_steps.append({
                "iteration": iteration,
                "status": "unbounded",
                "message": str(e)
            })
            return {
                "status": "unbounded", 
                "message": str(e),
                "steps": solution_steps
            }
        
        # Record pre-pivot state
        solution_steps.append({
            "iteration": iteration,
            "tableau": solver.tableau.tolist(),
            "basic_vars": [int(x) for x in solver.basic_vars],
            "pivot": pivot_info,
            "status": "pre_pivot"
        })
        
        # Pivot
        solver.pivot(leaving_row, entering_col)
        
        # Record post-pivot state
        solution_steps.append({
            "iteration": iteration,
            "tableau": solver.tableau.tolist(),
            "basic_vars": [int(x) for x in solver.basic_vars],
            "status": "post_pivot"
        })
    
    # Extract solution
    solution = np.zeros(solver.num_variables)
    for i, var in enumerate(solver.basic_vars):
        if 0 <= var < solver.num_variables:  # Check if it's an original variable
            solution[var] = solver.tableau[i, 0]
    
    objective_value = -solver.tableau[-1, 0]  # Negative because we use -c in the tableau
    
    # Adjust objective value for minimization
    if not maximize:
        objective_value = -objective_value
    
    if iteration >= max_iterations:
        status = "iteration_limit"
    else:
        status = "optimal"
    
    return {
        "status": status,
        "solution": solution.tolist(),
        "objective_value": float(objective_value),
        "iterations": iteration,
        "steps": solution_steps,
        "final_tableau": solver.tableau.tolist(),
        "final_basic_vars": solver.basic_vars,
        "constraint_transformations": constraint_transformations if constraint_transformations else None
    }

def save_problems_and_detailed_solutions(problems: List[Dict], 
                                       problems_file: str = "lp_problems.json",
                                       solutions_file: str = "lp_detailed_solutions.json") -> Tuple[str, str]:
    """
    Save LP problems and their detailed solutions with all steps to separate JSON files.
    """
    # Prepare problems for JSON serialization
    serializable_problems = []
    for problem in problems:
        # Convert NumPy arrays to lists if present
        serializable_problem = {
            "name": problem.get("name", "Unnamed Problem"),
            "description": problem.get("description", ""),
            "c": [float(x) for x in problem["c"]],
            "A": [[float(x) for x in row] for row in problem["A"]],
            "b": [float(x) for x in problem["b"]],
            "maximize": problem["maximize"],
            "original_format": {
                "c": [float(x) for x in problem["c"]],
                "A": [[float(x) for x in row] for row in problem["A"]],
                "b": [float(x) for x in problem["b"]],
            }
        }
        serializable_problems.append(serializable_problem)
    
    # Solve problems with detailed steps
    detailed_results = []
    for problem in problems:
        try:
            result = solve_lp_with_steps(
                problem["c"], 
                problem["A"], 
                problem["b"], 
                maximize=problem["maximize"]
            )
            
            # Ensure all numpy types are converted to Python native types
            result = convert_numpy_to_python_types(result)
            result["problem_name"] = problem.get("name", "Unnamed Problem")
            result["problem_description"] = problem.get("description", "")
        except Exception as e:
            # Handle any errors during solving
            result = {
                "status": "error",
                "message": str(e),
                "problem_name": problem.get("name", "Unnamed Problem"),
                "problem_description": problem.get("description", "")
            }
            
        detailed_results.append(result)
    
    # Save problems to JSON file
    with open(problems_file, 'w') as f:
        json.dump(serializable_problems, f, indent=2)
    
    # Save detailed solutions to JSON file
    with open(solutions_file, 'w') as f:
        json.dump(detailed_results, f, indent=2)
    
    return problems_file, solutions_file

def convert_numpy_to_python_types(obj):
    """
    Recursively convert numpy types to Python native types for JSON serialization.
    """
    if isinstance(obj, dict):
        return {k: convert_numpy_to_python_types(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [convert_numpy_to_python_types(item) for item in obj]
    elif isinstance(obj, (np.int_, np.intc, np.intp, np.int8, np.int16, np.int32, np.int64,
                         np.uint8, np.uint16, np.uint32, np.uint64)):
        return int(obj)
    elif isinstance(obj, (np.float64, np.float16, np.float32, np.float64)):
        return float(obj)
    elif isinstance(obj, (np.bool_)):
        return bool(obj)
    elif isinstance(obj, np.ndarray):
        return convert_numpy_to_python_types(obj.tolist())
    else:
        return obj

# Example usage that integrates with prepare_problem_for_simplex
if __name__ == "__main__":
    # Generate and solve problems
    problems = create_problem_batch(num_random=3)
    
    # Save to JSON files with detailed solutions
    problems_file, solutions_file = save_problems_and_detailed_solutions(problems)
    
    print(f"Saved {len(problems)} problems to {problems_file}")
    print(f"Saved {len(problems)} detailed solutions to {solutions_file}")

    
    
