import unittest
from unittest.mock import patch
import pandas as pd
from sorting.sorter import Adapter


class TestAdapter(unittest.TestCase):
    @patch("sorting.sorter_function.os.path.exists", return_value=True)
    @patch("sorting.sorter_function.pd.read_csv")
    def test_adapter_processing(self, mock_read_csv, mock_exists):
        mock_csv_data = pd.DataFrame(
            {
                "customer_id": ["C3", "C1", "C2", "C33"],
                "amount_kes": [2500, 17000, 1200, 440],
            }
        )
        mock_read_csv.return_value = mock_csv_data

        dataset = Adapter(
            "fake_file.csv",
            "customer_id",
            "amount_kes",
            1500,
        )

        # --- File access assertions ---
        # sort_csv is called 3x in __init__ (upper, lower, all)
        self.assertEqual(mock_read_csv.call_count, 3)
        mock_read_csv.assert_called_with("fake_file.csv")

        # --- Upper: values >= 1500 ---
        upper = dataset.get_upper()
        self.assertEqual(len(upper), 2)
        self.assertNotIn(1200, upper["amount_kes"].values)
        self.assertNotIn(440, upper["amount_kes"].values)

        # --- Lower: values <= 1500 ---
        lower = dataset.get_lower()
        self.assertEqual(len(lower), 2)
        self.assertNotIn(17000, lower["amount_kes"].values)
        self.assertNotIn(2500, lower["amount_kes"].values)

        # --- Sorting: alphabetical by customer_id ---
        upper_customers = upper["customer_id"].tolist()
        self.assertEqual(upper_customers, sorted(upper_customers))


if __name__ == "__main__":
    unittest.main()

