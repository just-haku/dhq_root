import math
import numpy as np

def test_arc_issue():
    # Simulate the SVG arc scaling issue
    # If starting at (0, 0) and ending at (10, 0) and r = 4.9
    # The SVG renderer will scale r to 5 and the center becomes (5, 0)
    pass
