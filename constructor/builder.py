import pandas as pd
import math
import os
from typing import Optional
from constructor import ResquestBuilder


class StockInfoConstructor:
    MARKET_RISK = 0.15
    MAX_PL = 40
    MIN_LIQUIDITY = 0.19
    BANKS_PATH = os.path.abspath("../data/bancos_e_seguradoras.txt")

    """
    Class responsible to construct the dataframe with all the infomation of fundamentalist indicators
    The information is collect from https://statusinvest.com.br/
    """

    def __init__(self) -> None:

        self.__request_builder = ResquestBuilder()

        self.__stocks_table: pd.Dataframe = self.__build_initial_dataframe()

        self.__filtered_stocks_table = self.__build_filtered_dataframe()

        self.__construct_complete_info()

        self.__original_data: pd.DataFrame = self.__request_builder.data

        self.__dict_info: Optional[dict] = None

    @property
    def stocks_table(self):
        return self.__stocks_table

    @property
    def filtered_stocks_table(self):
        return self.__filtered_stocks_table

    @property
    def dict_info(self):
        self.__build_dict_info()
        return self.__dict_info

    @property
    def original_data(self):
        return self.__original_data

    @property
    def all_tickers(self):
        return list(self.dict_info.keys())

    @property
    def request_time(self):
        return self.__request_builder.request_time

    def __build_initial_dataframe(self):
        """
        This methods initializes the initial dataframe with the information of stocks
        """

        original_data = self.__request_builder.data

        treated_data = self.__treat_original_data(original_data=original_data)

        return treated_data

    def __build_filtered_dataframe(self) -> pd.DataFrame:

        copy_data = self.__stocks_table.copy(deep=True)

        banks_index = [t for t in copy_data.index if t[:4] in self.__get_banks_tickers()]

        copy_data.drop(banks_index, inplace=True)

        copy_data.drop(copy_data[copy_data['P/L'] >
                                 self.MAX_PL].index, inplace=True)
        copy_data.drop(copy_data[copy_data['LIQUIDEZ MEDIA DIARIA']
                                 < self.MIN_LIQUIDITY].index, inplace=True)
        copy_data.drop(copy_data[copy_data['EV/EBIT']
                                 <= 0].index, inplace=True)

        return copy_data

    def __get_banks_tickers(self):
        with open(self.BANKS_PATH, "r") as file:
            lines = file.readlines()

        return [ticker[:4] for ticker in lines]

    def __treat_original_data(self, original_data: pd.DataFrame):
        """
        This method treat and clean the original data coming from statusinvest
        """
        original_data['DY'] = original_data['DY'].fillna(0)
        original_data['DY'] = original_data['DY'] / 100
        original_data['VALOR DE MERCADO'] = original_data['VALOR DE MERCADO'] / 1000000000
        original_data['LIQUIDEZ MEDIA DIARIA'] = original_data['LIQUIDEZ MEDIA DIARIA'] / 1000000
        original_data['CAGR LUCROS 5 ANOS'] = original_data['CAGR LUCROS 5 ANOS'] / 100
        original_data['CAGR RECEITAS 5 ANOS'] = original_data['CAGR RECEITAS 5 ANOS'] / 100
        original_data['ROE'] = original_data['ROE'] / 100
        original_data['ROIC'] = original_data['ROIC'] / 100
        original_data['MARGEM BRUTA'] = original_data['MARGEM BRUTA'] / 100
        original_data['MARGEM EBIT'] = original_data['MARGEM EBIT'] / 100
        original_data['MARG. LIQUIDA'] = original_data['MARG. LIQUIDA'] / 100
        original_data.drop(
            original_data[original_data['PRECO'] == 0].index, inplace=True)
        original_data.drop(
            original_data[original_data['LIQUIDEZ MEDIA DIARIA'].isnull()].index, inplace=True)

        stocks_data = self.__create_missing_fundamentalist_indicators(
            data=original_data)

        return stocks_data

    def __create_missing_fundamentalist_indicators(self, data: pd.DataFrame):
        """
        This method creates and insert the missing fundamentalist indicators
        """

        data['DPA'] = (data['DY'] * data['PRECO'])
        data['PAYOUT'] = data['DPA'] / data['LPA']

        data['CRESCIMENTO ESPERADO'] = self.__build_expected_growth(data=data)
        data['CRESCIMENTO MEDIO'] = self.__build_mean_projected_growth(
            data=data)

        data['PEG'] = data['P/L'] / data['CRESCIMENTO MEDIO']

        data.set_index('TICKER', inplace=True)
        data.index.name = None

        return data

    def __build_expected_growth(self, data: pd.DataFrame) -> list:
        """
        This method construc the expected growth based on past growth.
        """
        expected_growth = list()
        for i in data.index.tolist():
            if data['PAYOUT'][i] == 0:
                expected_growth.append(0.2 * data['ROE'][i])
            else:
                expected_growth.append((1 - data['PAYOUT'][i]) * data['ROE'][i])

        return expected_growth

    def __build_mean_projected_growth(self, data: pd.DataFrame) -> list:
        """
        This method calculates the expected growth for the future, based on the past growth.
        """

        projected_growth = list()

        for i in data.index.tolist():
            if data['CAGR LUCROS 5 ANOS'].isnull()[i]:
                projected_growth.append(data['CRESCIMENTO ESPERADO'][i])
            else:
                projected_growth.append(
                    (data['CRESCIMENTO ESPERADO'][i] + data['CAGR LUCROS 5 ANOS'][i]) / 2)

        return projected_growth

    def build_graham_fair_price(self, data: pd.DataFrame) -> list:
        """
        Calculates the fair price of stocks using Graham method
        """

        graham_prices = []
        for i in data.index.tolist():
            a = data['LPA'][i]
            b = data['VPA'][i]
            c = 22.5 * a * b
            if c < 0:
                graham_prices.append(None)
            elif a < 0:
                graham_prices.append(None)
            else:
                value = math.sqrt(c)
                graham_prices.append(value)

        return graham_prices

    def build_gordon_fair_price(self, data: pd.DataFrame) -> list:
        return (1 / self.MARKET_RISK) * data['DPA'] * (1 + 0.01 * data['CAGR LUCROS 5 ANOS'])

    def build_bazin_fair_price(self, data: pd.DataFrame) -> list:
        return data['DPA'] / 0.06

    def build_greenbalt_rank(self, data: pd.DataFrame):
        data_ebit_order = data.sort_values(by='EV/EBIT')
        data_ebit_order['RANK EV/EBIT'] = [
            pos for pos in range(data_ebit_order.shape[0])]
        data['RANK EV/EBIT'] = data_ebit_order['RANK EV/EBIT']

        data_order_roic = data.sort_values(by='ROIC', ascending=False)
        data_order_roic['RANK ROIC'] = [
            pos for pos in range(data_order_roic.shape[0])]
        data['RANK ROIC'] = data_order_roic['RANK ROIC']

        data['PONTUACAO GREENBLATT'] = data['RANK EV/EBIT'] + data['RANK ROIC']

        data_order_greenbalt = data.sort_values(by='PONTUACAO GREENBLATT')
        data_order_greenbalt['RANK GREENBLATT'] = [
            pos for pos in range(data_order_greenbalt.shape[0])]
        data['RANK GREENBLATT'] = data_order_greenbalt['RANK GREENBLATT'].astype(int)

        self.__actualize_original_table_with_greenbalt_info(data=data)

        return data

    def __actualize_original_table_with_greenbalt_info(self, data: pd.DataFrame):
        array_rank = list()
        for ticker in self.__stocks_table.index.tolist():
            if ticker in data.index.tolist():
                index = data.index.get_loc(ticker)
                value = int(data['RANK GREENBLATT'][index])
                array_rank.append(int(value))
            else:
                array_rank.append(-1)

        self.__stocks_table['RANK GREENBLATT'] = array_rank

    def __construct_complete_info(self):
        self.__stocks_table['PRECO JUSTO (GRAHAM)'] = self.build_graham_fair_price(
            data=self.__stocks_table)
        self.__stocks_table['DESCONTO (GRAHAM)'] = (
                self.__stocks_table['PRECO JUSTO (GRAHAM)'] / self.__stocks_table['PRECO'] - 1)

        self.__stocks_table['PRECO JUSTO (BAZIN)'] = self.build_bazin_fair_price(
            data=self.__stocks_table)
        self.__stocks_table['DESCONTO (BAZIN)'] = (
                self.__stocks_table['PRECO JUSTO (BAZIN)'] / self.__stocks_table['PRECO'] - 1)

        self.__stocks_table['PRECO JUSTO (GORDON)'] = self.build_gordon_fair_price(
            data=self.__stocks_table)
        self.__stocks_table['DESCONTO (GORDON)'] = (
                self.__stocks_table['PRECO JUSTO (GORDON)'] / self.__stocks_table['PRECO'] - 1)

        self.__filtered_stocks_table = self.build_greenbalt_rank(
            data=self.__filtered_stocks_table)

    def get_stocks_complete_data(self):
        return self.stocks_table, self.filtered_stocks_table

    def __construct_info_as_dict(self) -> dict:
        """
        Build a dictionary with all stocks info
        """

        stocks_dict = dict()
        for i, ticker in enumerate(self.stocks_table.index.tolist()):
            stocks_dict[ticker] = {}
            for col in self.stocks_table.columns:
                stocks_dict[ticker]['TICKER'] = ticker
                value = self.stocks_table.iloc[i][col]
                if col[:4] == 'RANK':
                    value = int(value)
                if isinstance(value, float):
                    if col[:5] == 'PRECO':
                        precision = 2
                    else:
                        precision = 4
                    value = round(value, precision)
                if math.isnan(value):
                    value = None
                stocks_dict[ticker][col] = value

        return stocks_dict

    def __build_dict_info(self):
        if self.__dict_info is None:
            self.__dict_info = self.__construct_info_as_dict()


if __name__ == "__main__":
    import json

    constructor = StockInfoConstructor()
    info = constructor.dict_info

    print("OK")
