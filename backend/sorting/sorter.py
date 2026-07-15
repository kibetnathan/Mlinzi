import prefilter
import sorter_function as sorter
import pandas


class Adapter:
    def __init__(self, path, sort_by, amount_col, min_value, max_value):
        self.__upper: pandas.df = sorter.sort_csv(path, sort_by)
        self.__lower: pandas.df = sorter.sort_csv(path, sort_by)

        self.__upper = prefilter.filter_min(self.__upper, amount_col, min_value)
        self.__lower = prefilter.filter_max(self.__lower, amount_col, max_value)

    def get_upper(self):
        return self.__upper

    def get_lower(self):
        return self.__lower
