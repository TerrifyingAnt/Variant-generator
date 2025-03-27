from manim import *
import numpy as np
from PIL import Image, ImageChops

config.background_color = WHITE
config.pixel_height = 720
config.pixel_width = 720
config.frame_height = 7
config.frame_width = 7

class ProblemScene(Scene):
    def construct(self, problem_data, image_path):
        # Format number to remove unnecessary decimal points
        def format_number(num):
            # Convert to float first to handle both integers and floats
            num_float = float(num)
            # Check if it's a whole number
            if num_float.is_integer():
                return str(int(num_float))
            else:
                return str(num_float)

        # Create a group to hold all elements for centering
        all_elements = VGroup()

        # Build objective function with proper formatting
        obj_terms = []
        # First term handling
        if problem_data['c'][0] != 0:
            obj_terms.append(f"{format_number(problem_data['c'][0])}x_1")
        
        # Second term handling
        if problem_data['c'][1] != 0:
            if problem_data['c'][1] > 0:
                prefix = "+ " if obj_terms else ""  # Only add + if not the first term
                obj_terms.append(f"{prefix}{format_number(problem_data['c'][1])}x_2")
            else:
                obj_terms.append(f"- {format_number(abs(problem_data['c'][1]))}x_2")
                
        # # Third term handling
        # if problem_data['c'][2] != 0:
        #     if problem_data['c'][2] > 0:
        #         prefix = "+ " if obj_terms else ""  # Only add + if not the first term
        #         obj_terms.append(f"{prefix}{format_number(problem_data['c'][2])}x_3")
        #     else:
        #         obj_terms.append(f"- {format_number(abs(problem_data['c'][2]))}x_3")
        
        # Handle edge case where all coefficients are zero
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

        # Format constraints with proper signs
        constraints = VGroup()
        for i, row in enumerate(problem_data['A']):
            # Build constraint terms with proper formatting
            constraint_terms = []
            
            # First term handling
            if row[0] != 0:
                constraint_terms.append(f"{format_number(row[0])}x_1")
            
            # Second term handling
            if row[1] != 0:
                if row[1] > 0:
                    prefix = "+ " if constraint_terms else ""  # Only add + if not the first term
                    constraint_terms.append(f"{prefix}{format_number(row[1])}x_2")
                else:
                    constraint_terms.append(f"- {format_number(abs(row[1]))}x_2")
                    
            # Third term handling
            # if row[2] != 0:
            #     if row[2] > 0:
            #         prefix = "+ " if constraint_terms else ""  # Only add + if not the first term
            #         constraint_terms.append(f"{prefix}{format_number(row[2])}x_3")
            #     else:
            #         constraint_terms.append(f"- {format_number(abs(row[2]))}x_3")
            
            # Handle edge case where all coefficients are zero
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
        
        # Add curly brace to the left of constraints
        brace = Brace(constraints, direction=LEFT)
        brace.color = BLACK
        
        # Group brace and constraints together
        brace_with_constraints = VGroup(brace, constraints)
        all_elements.add(brace_with_constraints)

        nonnegativity = MathTex("x_1", "\\geq", "0,", "x_2", "\\geq", "0,", "x_3", "\\geq", "0.")
        nonnegativity.color = BLACK
        all_elements.add(nonnegativity)

        # Arrange all elements vertically
        all_elements.arrange(DOWN, center=True, buff=0.3)
        
        # Center the entire group on the screen
        all_elements.move_to(ORIGIN)
        
        # Add all elements to the scene
        self.add(all_elements)

        # This will capture the image
        self.renderer.camera.capture_mobjects(self.mobjects)
        temp_path = "temp_" + image_path
        self.renderer.camera.get_image().save(temp_path)
        
        # Crop the image to remove empty space
        crop_image(temp_path, image_path)

# Function to crop image to only include content
def crop_image(input_path, output_path, border=10):
    # Open the image
    img = Image.open(input_path)
    
    # Convert to RGB if it's not already
    if img.mode != 'RGB':
        img = img.convert('RGB')
    
    # Get the background color (assuming it's the corner pixel)
    bg_color = img.getpixel((0, 0))
    
    # Create a mask where True is content and False is background
    mask = np.array(img) != bg_color
    mask = mask.any(axis=2)
    
    # Find content boundaries
    rows = np.any(mask, axis=1)
    cols = np.any(mask, axis=0)
    
    # Get the non-empty areas
    y_min, y_max = np.where(rows)[0][[0, -1]]
    x_min, x_max = np.where(cols)[0][[0, -1]]
    
    # Add a small border
    y_min = max(0, y_min - border)
    y_max = min(img.height, y_max + border)
    x_min = max(0, x_min - border)
    x_max = min(img.width, x_max + border)
    
    # Crop the image
    cropped_img = img.crop((x_min, y_min, x_max, y_max))
    
    # Save the cropped image
    cropped_img.save("task_images/" + output_path)
    
    # Clean up the temporary file
    import os
    os.remove(input_path)

# Example usage
def generate_problem_image(problem_data, output_path):
    config.output_file = output_path
    # Set the preview to False to avoid opening window
    config.preview = False
    
    scene = ProblemScene()
    scene.construct(problem_data, output_path)
    
# Sample usage
if __name__ == "__main__":
    problem_data = {
        'name': '1',
        'c': [2.0, 0, 4],  # Second coefficient is zero
        'A': [[1, -2.0, 0], [0, 0, -2.25], [1.5, 0, -5]],  # Various zero coefficients
        'b': [8, 12.5, 10.0],
        'maximize': True
    }
    generate_problem_image(problem_data, "task_images/problem_image.png")