# geometry.py
from abc import ABC, abstractmethod
import math
import matplotlib.pyplot as plt

class GeometricFigure(ABC):
    @abstractmethod
    def area(self):
        pass

class Color:
    """Class to manage figure color."""
    def __init__(self, color):
        self._color = color

    @property
    def color(self):
        return self._color

    @color.setter
    def color(self, value):
        self._color = value

class Triangle(GeometricFigure):
    """Triangle class with area calculation."""
    name = "Triangle"

    def __init__(self, a, b, C, color):
        super().__init__()  # Call parent constructor
        self.a = a
        self.b = b
        self.C = C  # degrees
        self.color_obj = Color(color)

    def area(self):
        """Calculate area using two sides and included angle."""
        return 0.5 * self.a * self.b * math.sin(math.radians(self.C))

    def __str__(self):
        return f"Triangle with sides {self.a}, {self.b}, angle {self.C}°, color {self.color_obj.color}, area {self.area():.2f}"

    @classmethod
    def get_name(cls):
        return cls.name

# main.py
def main():
    while True:
        try:
            a = float(input("Enter side a: "))
            b = float(input("Enter side b: "))
            C = float(input("Enter angle C (degrees): "))
            color = input("Enter color: ")
            if a <= 0 or b <= 0 or C <= 0 or C >= 180:
                raise ValueError("Sides must be positive, angle between 0 and 180.")
            triangle = Triangle(a, b, C, color)
            print(triangle)

            # Plot triangle
            x1, y1 = 0, 0
            x2, y2 = a, 0
            C_rad = math.radians(C)
            x3 = b * math.cos(C_rad)
            y3 = b * math.sin(C_rad)
            plt.fill([x1, x2, x3], [y1, y2, y3], color=color)
            plt.text(x1, y1, "A")
            plt.text(x2, y2, "B")
            plt.text(x3, y3, "C")
            plt.title("Triangle")
            plt.savefig("triangle.png")
            plt.show()
            break
        except ValueError as e:
            print(f"Error: {e}")

if __name__ == "__main__":
    main()