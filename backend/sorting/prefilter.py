"""
Do not call these functions directly, call them from the sorter adapter class (see sorter.py)
"""

from . import sorter_function as sorter
import pandas as pd


def filter_min(df: pd.DataFrame, amount_col: str, min_value: float) -> pd.DataFrame:
    """
    Filters DataFrame to only include transactions exceding minimum value
    """
    try:
        if amount_col not in df.columns:
            raise KeyError(f"column {amount_col} not found in the DataFrame")
        df_clean = df.copy()
        df_clean[amount_col] = pd.to_numeric(df_clean[amount_col], errors="coerce")

        # filter out NaN and filter out minimum values
        filtered_df = df_clean[df_clean[amount_col] >= min_value]

        print(
            f"Filtered out {len(df) - len(filtered_df)} transactions below {min_value}."
        )
        return filtered_df
    except KeyError as e:
        print(f"Filtering error: {e}")
        return df

    except Exception as e:
        print(f"An unexpected error occurred during filtering: {e}")
        return df


def filter_max(df: pd.DataFrame, amount_col: str, max_value: float) -> pd.DataFrame:
    """
    Filters DataFrame to only include transactions within maximum value
    """
    try:
        if amount_col not in df.columns:
            raise KeyError(f"column {amount_col} not found in the DataFrame")
        df_clean = df.copy()
        df_clean[amount_col] = pd.to_numeric(df_clean[amount_col], errors="coerce")

        # filter out NaN and filter out maximum values
        filtered_df = df_clean[df_clean[amount_col] < max_value]

        print(
            f"Filtered out {len(df) - len(filtered_df)} transactions below {max_value}."
        )
        return filtered_df
    except KeyError as e:
        print(f"Filtering error: {e}")
        return df

    except Exception as e:
        print(f"An unexpected error occurred during filtering: {e}")
        return df


def main():
    print(
        filter_min(
            sorter.sort_csv("data/mlinzi_sample_transactions.csv", "customer_id"),
            "amount_kes",
            2000,
        )
    )
    print(
        filter_max(
            sorter.sort_csv("data/mlinzi_sample_transactions.csv", "customer_id"),
            "amount_kes",
            2000,
        )
    )


if __name__ == "__main__":
    main()
