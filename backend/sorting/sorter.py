from . import prefilter
from . import sorter_function as sorter
import pandas


class Adapter:
    """
    This Adapter class abstracts away the sorting and filtering implementation of the service and exposes two values:
    upper -> This is a sorted pandas dataframe containing all the sorted data exceding a certain threshold i.e more money
    lower -> This is a sorted pandas dataframe containing all the data below the same threshold i.e lower money amounts
    The properties are private therefore they can only be accessed by the getter methods.
    """

    def __init__(self, path: str, sort_by: str, amount_col: str, min_value: float):
        """
        The init function takes in the path to the csv, the value you want to sort the data by (eg, amount, customer_id), the name of the
        amount column in the csv, and the minimum value you want for the larger dataset
        """
        self.__upper: pandas.df = sorter.sort_csv(path, sort_by)
        self.__lower: pandas.df = sorter.sort_csv(path, sort_by)
        self.__all: pandas.df = sorter.sort_csv(path, sort_by)
        max_value = min_value

        self.__upper = prefilter.filter_min(self.__upper, amount_col, min_value)
        self.__lower = prefilter.filter_max(self.__lower, amount_col, max_value)

    def get_all(self):
        return self.__all

    def get_upper(self):
        return self.__upper

    def get_lower(self):
        return self.__lower
