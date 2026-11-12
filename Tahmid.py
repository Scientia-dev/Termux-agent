# Tahmid.py
# This script prints the multiplication table for a user-provided integer.

def multiplication_table(n, limit=10):
    """Return a list of strings representing the multiplication table of n up to `limit`."""
    return [f"{n} x {i} = {n * i}" for i in range(1, limit + 1)]


def main():
    try:
        num_str = input("Enter an integer to see its multiplication table: ")
        n = int(num_str)
    except ValueError:
        print("Invalid input. Please enter a valid integer.")
        return

    table = multiplication_table(n)
    print("\n".join(table))


if __name__ == "__main__":
    main()
