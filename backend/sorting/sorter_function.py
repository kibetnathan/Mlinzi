import pandas as pd
import os


def sort_csv(path: str, sort_by: str):
    try:
        if not os.path.exists(path):
            raise FileNotFoundError(f"The input file '{path}' does not exist")
        file = pd.read_csv(path)

        cols_to_check = [sort_by] if isinstance(sort_by, str) else sort_by
        missing_cols = [col for col in cols_to_check if col not in file.columns]
        if missing_cols:
            raise KeyError(f"Column(s) {missing_cols} not found in the csv file")
        sorted_data = file.sort_values(by="customer_id", ascending=True)

        return sorted_data
    except FileNotFoundError as e:
        print(f"File Error: {e}")
    except pd.errors.EmptyDataError:
        print(f"Data Error: The file '{path}' is empty.")
    except pd.errors.ParserError:
        print(f"Parser Error: '{path}' is not a valid CSV format.")
    except KeyError as e:
        print(f"Sorting Error: {e}")
    except PermissionError:
        print(
            "Permission Error: Cannot read or write to the specified path. Check your folder permissions."
        )
    except Exception as e:
        print(f"An unexpected error occured: {e}")


def main():
    print(sort_csv("data/mlinzi_sample_transactions.csv", "customer_id"))


if __name__ == "__main__":
    main()
