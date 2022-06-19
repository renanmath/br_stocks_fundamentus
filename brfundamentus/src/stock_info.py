from brfundamentus.constructor import StockInfoConstructor
from typing import List, Dict


class StockInfo:
    """
    This class is responsible for handle the fundamentalist info
    """

    def __init__(self):
        self.__constructor = StockInfoConstructor()
        self.__all_info = self.__constructor.dict_info
        self.__complete_data, self.__filtered_data = self.__constructor.get_stocks_complete_data()
        self.__all_parameters_keys = self.__complete_data.columns.tolist()

    @property
    def all_info(self):
        return self.__all_info

    @property
    def complete_data(self):
        return self.__complete_data

    @property
    def filtered_data(self):
        return self.__filtered_data

    @property
    def all_tickers(self):
        return list(self.all_info.keys())

    @property
    def request_time(self):
        return self.__constructor.request_time

    def __filter_stocks_by_single_criterion(self, parameter: str,
                                            cut_criterion: float = 0,
                                            reverse_cut: bool = False,
                                            disconsider: list = None,
                                            only_from: list = None) -> list:

        if disconsider is None:
            disconsider = []
        if only_from is None:
            only_from = []

        if parameter not in self.__all_parameters_keys:
            return []

        all_info = self.all_info
        modifier = - 1 if reverse_cut else 1
        info_list = [all_info[ticker] for ticker in all_info
                     if all_info[ticker][parameter] is not None and ticker not in disconsider
                     and modifier * all_info[ticker][parameter] > modifier * cut_criterion]

        if only_from:
            info_list = [
                info for info in info_list if info["TICKER"] in only_from]

        return info_list

    def get_top_stocks_by_criterion(self, num_stocks: int, parameter: str,
                                    cut_criterion: float = 0, reverse_cut: bool = False,
                                    ascending: bool = False,
                                    disconsider: list = [],
                                    only_from: list = []) -> List[Dict]:
        """
        This method filter stocks by a given criterion.
        Returns a list of dictionaries with all information of the filterd stocks.
        Parameters:
            - num_stocks (int): Maximum lenght of the result list.
            - parameter (string): The parameter by which we want to filter the stocks.
                                It should be a key from the dictionary of all info. Otherwise, method will return a empty list.
            - cut_criterion (float): Value used as cut criterion. Default value is 0.
                                    By default, method selects all stocs which 'parameter' value is grether then 'cut_criterion'
            - reverse_cut (bool): If True, method will invert the condiction, selecting all stocs which 'parameter' value is less then 'cut_criterion'.
                                Default value is False.
            - ascending (bool): If True, result list will be sorted by ascending values of 'parameter'.
                                If Falae, result list will be sorted by descending values of 'parameter'.
                                Default value is False.
            - disconsider (list): A list of tickers. All stocks with thoses tickers will be excluded in the final result.
            - only_from (list): A list of tickers. Method will only consider stocks from that list before filter by given criterion.
        """

        info_list = self.__filter_stocks_by_single_criterion(parameter=parameter,
                                                             cut_criterion=cut_criterion,
                                                             reverse_cut=reverse_cut,
                                                             disconsider=disconsider,
                                                             only_from=only_from)

        info_list.sort(key=lambda x: x[parameter], reverse=not ascending)

        max_index = min(num_stocks, len(info_list))

        return info_list[:max_index]

    def get_top_stocks_by_conditions(self, conditionals: List[Dict], sort_by: dict,
                                     num_stocks: int = 50,
                                     disconsider: list = None,
                                     only_from: list = None) -> List[Dict]:
        """
        This method filter the stocsk by a set of criteria.
        Returns a list of dictionaries with all information of the filterd stocks.

        Params:
            - conditionals: A list of dictionaries, each one containing information of one criterion.
                            Each dictionarie must have the following keys:
                                - 'parameter' (string): the criterion one wants to filter. Should be a key from the dictionarie of all info.
                                - 'cut_criterion' (float): a value used as cut criterion.
                                - 'reverse_cut' (bool): flag to indicate if the cut_criterion is reversed.
            - num_stocks (int): Maximum number of stocks in the result list. Default value is 50.
            - disconsider (list): A list of tickers. All stocks with thoses tickers will be excluded in the final result.
            - only_from (list): A list of tickers. Method will only consider stocks from that list before filter by given criterion.

        """

        list_of_stocks_filtered = list()
        for criterion in conditionals:
            total_info = self.__filter_stocks_by_single_criterion(
                parameter=criterion['parameter'],
                cut_criterion=criterion['cut_criterion'],
                reverse_cut=criterion['reverse_cut'],
                disconsider=disconsider,
                only_from=only_from)

            only_tickers = [x['TICKER'] for x in total_info]
            list_of_stocks_filtered.append(only_tickers)

        selected_tickers = [ticker for ticker in self.all_info
                            if all((ticker in single_list for single_list in list_of_stocks_filtered))]

        result = [self.all_info[ticker] for ticker in selected_tickers]
        result.sort(key=lambda x: x[sort_by['parameter']],
                    reverse=not sort_by['ascending'])

        limit = min(len(result), num_stocks)

        return result[:limit]

    def top_graham(self, num_stocks: int = 50, cut: float = 0.2,
                   disconsider: list = [],
                   only_from: list = []):
        return self.get_top_stocks_by_criterion(num_stocks=num_stocks,
                                                parameter='DESCONTO (GRAHAM)',
                                                cut_criterion=cut,
                                                disconsider=disconsider,
                                                only_from=only_from)

    def top_bazin(self, num_stocks: int = 50, cut: float = 0.15,
                  disconsider: list = [],
                  only_from: list = []):
        return self.get_top_stocks_by_criterion(num_stocks=num_stocks,
                                                parameter='DESCONTO (BAZIN)',
                                                cut_criterion=cut,
                                                disconsider=disconsider,
                                                only_from=only_from)

    def top_gordon(self, num_stocks: int = 50, cut: float = 0.1,
                   disconsider: list = [],
                   only_from: list = []):
        return self.get_top_stocks_by_criterion(num_stocks=num_stocks,
                                                parameter='DESCONTO (GORDON)',
                                                cut_criterion=cut,
                                                disconsider=disconsider,
                                                only_from=only_from)

    def top_greenblatt(self, num_stocks: int = 50, disconsider: list = [],
                       only_from: list = []):
        return self.get_top_stocks_by_criterion(num_stocks=num_stocks,
                                                parameter='RANK GREENBLATT',
                                                cut_criterion=-1, ascending=True,
                                                disconsider=disconsider,
                                                only_from=only_from)

    def get_ticker_info(self, ticker: str) -> dict:
        """
        Returns a dictionary with all information of the stock.
        Returns nothing if ticker is not valid.
        """
        return self.all_info.get(ticker, None)


if __name__ == "__main__":
    ticker = "VALE3"

    stocks_info = StockInfo()

    all_info = stocks_info.all_info

    print(all_info[ticker])

    print("OK")
