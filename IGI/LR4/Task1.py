# vacation_handler.py
import csv
import pickle
from collections import Counter

class EmployeeVacation:
    """Represents an employee's vacation data."""
    def __init__(self, last_name, day, month):
        self.last_name = last_name
        self.day = int(day)
        self.month = month.lower()

    def to_dict(self):
        """Convert object to dictionary for CSV serialization."""
        return {'last_name': self.last_name, 'day': self.day, 'month': self.month}

    @classmethod
    def from_dict(cls, data):
        """Create object from dictionary."""
        return cls(data['last_name'], data['day'], data['month'])

    def __str__(self):
        return f"{self.last_name}: {self.day} {self.month}"

class VacationDataHandler:
    """Base class for handling vacation data."""
    def __init__(self):
        self.employees = []

    def load_data(self, file_path):
        """Load data from file (to be implemented by subclasses)."""
        raise NotImplementedError

    def save_data(self, file_path):
        """Save data to file (to be implemented by subclasses)."""
        raise NotImplementedError

    def get_employee_vacation(self, last_name):
        """Search for an employee's vacation details."""
        for emp in self.employees:
            if emp.last_name.lower() == last_name.lower():
                return str(emp)
        return "Employee not found"

    def get_monthly_stats(self):
        """Calculate number and percentage of employees per month."""
        total = len(self.employees)
        if total == 0:
            return {}
        month_counts = Counter(emp.month for emp in self.employees)
        return {month: (count, (count / total) * 100) for month, count in month_counts.items()}

class CSVVacationDataHandler(VacationDataHandler):
    """Handles vacation data using CSV format."""
    def load_data(self, file_path):
        self.employees = []
        try:
            with open(file_path, 'r', newline='') as csvfile:
                reader = csv.DictReader(csvfile)
                for row in reader:
                    self.employees.append(EmployeeVacation.from_dict(row))
        except FileNotFoundError:
            print(f"Error: File {file_path} not found.")
        except ValueError as e:
            print(f"Error: Invalid data format - {e}")

    def save_data(self, file_path):
        if not self.employees:
            print("No data to save.")
            return
        try:
            with open(file_path, 'w', newline='') as csvfile:
                fieldnames = ['last_name', 'day', 'month']
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                writer.writeheader()
                for emp in self.employees:
                    writer.writerow(emp.to_dict())
        except IOError as e:
            print(f"Error saving file: {e}")

class PickleVacationDataHandler(VacationDataHandler):
    """Handles vacation data using pickle format."""
    def load_data(self, file_path):
        try:
            with open(file_path, 'rb') as f:
                self.employees = pickle.load(f)
        except FileNotFoundError:
            print(f"Error: File {file_path} not found.")
        except pickle.PickleError as e:
            print(f"Error loading pickle data: {e}")

    def save_data(self, file_path):
        if not self.employees:
            print("No data to save.")
            return
        try:
            with open(file_path, 'wb') as f:
                pickle.dump(self.employees, f)
        except IOError as e:
            print(f"Error saving file: {e}")

# main.py
def main():
    """Main function to test vacation schedule functionality."""
    # Sample data for testing
    sample_data = [
        EmployeeVacation("Smith", 15, "June"),
        EmployeeVacation("Johnson", 20, "July"),
        EmployeeVacation("Williams", 5, "June")
    ]
    
    # Choose CSV handler (pickle can be swapped in)
    handler = CSVVacationDataHandler()
    file_path = "vacations.csv"
    handler.employees = sample_data
    handler.save_data(file_path)
    handler.load_data(file_path)

    while True:
        print("\nVacation Schedule Menu:")
        print("1. Search employee")
        print("2. Show monthly stats")
        print("3. Exit")
        choice = input("Enter choice: ")
        try:
            if choice == "1":
                name = input("Enter last name: ")
                print(handler.get_employee_vacation(name))
            elif choice == "2":
                stats = handler.get_monthly_stats()
                for month, (count, pct) in stats.items():
                    print(f"{month}: {count} employees ({pct:.2f}%)")
            elif choice == "3":
                break
            else:
                print("Invalid choice.")
        except Exception as e:
            print(f"Error: {e}")

if __name__ == "__main__":
    main()