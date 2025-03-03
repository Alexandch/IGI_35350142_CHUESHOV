import os
import time
from geometric_lib.circle import area

radius = float(os.getenv("RADIUS", 5))  # Значение по умолчанию 5
circle_area = area(radius)
print(f"Площадь круга с радиусом {radius} равна {circle_area}")
while True:
    time.sleep(60)