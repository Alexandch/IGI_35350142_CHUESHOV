# series_approximator.py
import math
import matplotlib.pyplot as plt
import statistics

class ExponentialSeries:
    """Class to approximate e^x using Taylor series."""
    def __init__(self):
        self.table = []

    @staticmethod
    def factorial(k):
        return math.factorial(k)

    def compute_partial_sum(self, x, n):
        """Compute partial sum of e^x series up to n terms."""
        return sum(x**k / self.factorial(k) for k in range(n + 1))

    def compute_exact(self, x):
        """Compute exact e^x using math module."""
        return math.exp(x)

    def generate_table(self, x_values, n_values):
        """Generate table of values."""
        self.table = [
            {'x': x, 'n': n, 'F(x)': self.compute_partial_sum(x, n), 
             'Math F(x)': self.compute_exact(x), 'eps': abs(self.compute_partial_sum(x, n) - self.compute_exact(x))}
            for x in x_values for n in n_values
        ]
        return self.table

    def compute_statistics(self, x_values, n):
        """Compute statistics of errors."""
        errors = [abs(self.compute_partial_sum(x, n) - self.compute_exact(x)) for x in x_values]
        return {
            'mean': statistics.mean(errors),
            'median': statistics.median(errors),
            'mode': statistics.mode(errors) if len(set(errors)) < len(errors) else "No unique mode",
            'variance': statistics.variance(errors),
            'std_dev': statistics.stdev(errors)
        }

    def plot_series(self, x_values, n_values, file_path):
        """Plot series approximations and exact function."""
        plt.figure()
        for n in n_values:
            F_x = [self.compute_partial_sum(x, n) for x in x_values]
            plt.plot(x_values, F_x, label=f'n={n}')
        exact = [self.compute_exact(x) for x in x_values]
        plt.plot(x_values, exact, 'k-', label='Exact e^x')
        plt.xlabel('x')
        plt.ylabel('F(x)')
        plt.title('Taylor Series Approximation of e^x')
        plt.legend()
        plt.grid(True)
        plt.savefig(file_path)
        plt.show()

# main.py
def main():
    approximator = ExponentialSeries()
    x_values = [i / 10 for i in range(-20, 21)]  # -2 to 2
    n_values = [1, 3, 5]
    approximator.generate_table(x_values, n_values)
    approximator.plot_series(x_values, n_values, "series_plot.png")
    stats = approximator.compute_statistics(x_values, 5)
    print("Statistics:", stats)

if __name__ == "__main__":
    main()