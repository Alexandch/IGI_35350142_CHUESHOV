# matrix_analyzer.py
import numpy as np

class MatrixAnalyzer:
    """Class to analyze a NumPy matrix."""
    def __init__(self, n, m):
        self.matrix = np.random.randint(0, 11, size=(n, m))

    def min_elements(self):
        """Find count and indices of minimum elements."""
        min_val = np.min(self.matrix)
        indices = np.where(self.matrix == min_val)
        return min_val, len(indices[0]), list(zip(indices[0], indices[1]))

    def std_dev(self):
        """Compute standard deviation two ways."""
        std_np = np.std(self.matrix)
        mean = np.mean(self.matrix)
        variance_manual = np.sum((self.matrix - mean)**2) / self.matrix.size
        std_manual = np.sqrt(variance_manual)
        return std_np, std_manual

# main.py
def main():
    analyzer = MatrixAnalyzer(5, 5)
    print("Matrix:\n", analyzer.matrix)
    min_val, count, indices = analyzer.min_elements()
    print(f"Min value: {min_val}, Count: {count}, Indices: {indices}")
    std_np, std_manual = analyzer.std_dev()
    print(f"Std Dev (NumPy): {std_np:.2f}, Std Dev (Manual): {std_manual:.2f}")

if __name__ == "__main__":
    main()