import numpy as np
from typing import Tuple, List, Optional

class SimplexSolver:
    def __init__(self):
        self.A = None  # Constraint coefficients
        self.b = None  # Constraint values
        self.c = None  # Objective function coefficients
        self.tableau = None
        self.basic_vars = None
        self.num_constraints = 0
        self.num_variables = 0
        
    def setup_problem(self, c: np.ndarray, A: np.ndarray, b: np.ndarray):
        """
        Set up the initial tableau for the simplex method
        
        Parameters:
        - c: coefficients of the objective function to maximize
        - A: constraint coefficients matrix
        - b: constraint values vector
        """
        self.num_constraints, self.num_variables = A.shape
        self.A = A
        self.b = b.reshape(-1, 1)  # Ensure column vector
        self.c = c
        
        # Check if all b values are non-negative (required for standard form)
        if np.any(self.b < 0):
            raise ValueError("All constraint values must be non-negative for standard form")
        
        # Create the initial tableau
        # Format of tableau:
        # [  b  | A  | I  ]
        # [ -z  | c  | 0  ]
        
        # Initialize basic variables (slack variables)
        self.basic_vars = list(range(self.num_variables, self.num_variables + self.num_constraints))
        
        # Create tableau
        self.tableau = np.zeros((self.num_constraints + 1, 1 + self.num_variables + self.num_constraints))
        
        # Set up the constraint rows
        self.tableau[:self.num_constraints, 0] = self.b.flatten()  # b values
        self.tableau[:self.num_constraints, 1:self.num_variables+1] = self.A  # A matrix
        
        # Set up identity matrix for slack variables
        self.tableau[:self.num_constraints, self.num_variables+1:] = np.eye(self.num_constraints)
        
        # Set up objective function row (z = c^T x)
        self.tableau[self.num_constraints, 0] = 0  # Initial z value
        self.tableau[self.num_constraints, 1:self.num_variables+1] = -self.c  # Negative c for minimization
    
    def is_optimal(self) -> bool:
        """Check if the current solution is optimal"""
        return np.all(self.tableau[-1, 1:] >= 0)
    
    def select_entering_var(self) -> int:
        """Select the entering variable using the most negative coefficient rule"""
        coefs = self.tableau[-1, 1:]
        if np.all(coefs >= 0):
            return -1  # No entering variable (optimal solution found)
        
        return np.argmin(coefs) + 1  # +1 for tableau indexing
    
    def select_leaving_var(self, entering_col: int) -> Tuple[int, float]:
        """
        Select the leaving variable using the minimum ratio test
        Returns row index and the minimum ratio
        """
        ratios = []
        for i in range(self.num_constraints):
            if self.tableau[i, entering_col] <= 0:
                ratios.append(float('inf'))
            else:
                ratios.append(self.tableau[i, 0] / self.tableau[i, entering_col])
        
        if all(r == float('inf') for r in ratios):
            raise ValueError("Problem is unbounded")
        
        leaving_row = np.argmin(ratios)
        return leaving_row, ratios[leaving_row]
    
    def pivot(self, row: int, col: int):
        """Perform pivoting operation"""
        # Get the pivot element
        pivot_element = self.tableau[row, col]
        
        # Scale the pivot row
        self.tableau[row] = self.tableau[row] / pivot_element
        
        # Update all other rows
        for i in range(self.tableau.shape[0]):
            if i != row:
                self.tableau[i] = self.tableau[i] - self.tableau[i, col] * self.tableau[row]
        
        # Update basic variables
        self.basic_vars[row] = col - 1  # -1 to adjust for tableau indexing
    
    def solve(self, c: np.ndarray, A: np.ndarray, b: np.ndarray, 
              max_iterations: int = 100, verbose: bool = False) -> dict:
        """
        Solve a linear programming problem using the simplex method
        
        Parameters:
        - c: coefficients of the objective function to maximize
        - A: constraint coefficients matrix
        - b: constraint values vector
        - max_iterations: maximum number of iterations
        - verbose: print intermediate steps
        
        Returns:
        - Dictionary containing the solution, objective value, and status
        """
        # Set up the initial tableau
        self.setup_problem(c, A, b)
        
        iteration = 0
        while not self.is_optimal() and iteration < max_iterations:
            if verbose:
                print(f"\nIteration {iteration}")
                print(self.tableau)
            
            # Select entering variable
            entering_col = self.select_entering_var()
            if entering_col == -1:
                break  # Optimal solution found
                
            # Select leaving variable
            try:
                leaving_row, min_ratio = self.select_leaving_var(entering_col)
                if verbose:
                    print(f"Entering col: {entering_col}, Leaving row: {leaving_row}, Ratio: {min_ratio}")
            except ValueError as e:
                return {"status": "unbounded", "message": str(e)}
            
            # Pivot
            self.pivot(leaving_row, entering_col)
            
            iteration += 1
        
        # Extract solution
        solution = np.zeros(self.num_variables)
        for i, var in enumerate(self.basic_vars):
            if 0 <= var < self.num_variables:  # Check if it's an original variable
                solution[var] = self.tableau[i, 0]
        
        objective_value = -self.tableau[-1, 0]  # Negative because we use -c in the tableau
        
        if iteration >= max_iterations:
            return {
                "status": "iteration_limit",
                "solution": solution,
                "objective_value": objective_value,
                "iterations": iteration
            }
        
        return {
            "status": "optimal",
            "solution": solution,
            "objective_value": objective_value,
            "iterations": iteration
        }


def solve_lp(c: List[float], A: List[List[float]], b: List[float], 
            maximize: bool = True, verbose: bool = False) -> dict:
    """
    Convenience function to solve linear programming problem
    
    Parameters:
    - c: objective function coefficients
    - A: constraint coefficients matrix
    - b: constraint values
    - maximize: True if maximizing, False if minimizing
    - verbose: print intermediate steps
    
    Returns:
    - Dictionary with solution details
    """
    c_arr = np.array(c, dtype=float)
    A_arr = np.array(A, dtype=float)
    b_arr = np.array(b, dtype=float)
    
    # If minimizing, negate the objective function
    if not maximize:
        c_arr = -c_arr
    
    solver = SimplexSolver()
    result = solver.solve(c_arr, A_arr, b_arr, verbose=verbose)
    
    # Adjust objective value for minimization
    if not maximize and result["status"] in ["optimal", "iteration_limit"]:
        result["objective_value"] = -result["objective_value"]
    
    return result


# Example usage
if __name__ == "__main__":
    # Example: Maximize 3x + 4y subject to:
    # x + 2y ≤ 8
    # 3x + 2y ≤ 12
    # x, y ≥ 0
    
    c = [3, 4]  # Objective function coefficients
    A = [
        [1, 2],  # Constraints coefficients
        [3, 2]
    ]
    b = [8, 12]  # Constraint values
    
    result = solve_lp(c, A, b, maximize=True, verbose=True)
    
    print("\nFinal result:")
    print(f"Status: {result['status']}")
    if result['status'] in ['optimal', 'iteration_limit']:
        print(f"Optimal solution: {result['solution']}")
        print(f"Objective value: {result['objective_value']}")
        print(f"Iterations: {result['iterations']}")