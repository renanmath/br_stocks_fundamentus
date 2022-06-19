from brfundamentus.src import StockInfo
from copy import copy

"""
This script is an example of how to use some of the functionalities
"""


def arredondar(x: float):
    try:
        return round(x, 4)
    except (TypeError, ValueError):
        return x


def print_list(list_of_stocks: list):
    for stock in list_of_stocks:
        print(
            f"{stock['TICKER']} | {int(stock['RANK GREENBLATT'])} | {arredondar(stock['PRECO'])} | {arredondar(stock['DESCONTO (GRAHAM)'])} | {arredondar(stock['DESCONTO (BAZIN)'])} | {arredondar(stock['DESCONTO (GORDON)'])} | {arredondar(stock['CRESCIMENTO MEDIO'])} | {stock['DY']}")

    print("-" * 50)


def only_tickers(list_of_stocks: list) -> list:
    return [info["TICKER"] for info in list_of_stocks]


def union_lists(list1: list, list2: list) -> list:
    union = copy(list1)
    union += [x for x in list2 if x not in list1]

    return union


# First, instantiate a stock information handler
# This class is responsible to perform the valuations
# and has some useful filter methods
stock_info = StockInfo()

# Then, define your own filters
# They have to be dictionaries of three keys:
# parameter, cut_criterion and reverse_cut.
# See the docstring of method get_top_stocks_by_conditions
filtros_comuns = [
    {
        "parameter": "PRECO JUSTO (GRAHAM)",
        "cut_criterion": 150.00,
        "reverse_cut": True
    },
    {
        "parameter": "PRECO JUSTO (BAZIN)",
        "cut_criterion": 150.00,
        "reverse_cut": True
    },
    {
        "parameter": "PRECO JUSTO (GORDON)",
        "cut_criterion": 150.00,
        "reverse_cut": True
    },
    {
        "parameter": "LIQUIDEZ MEDIA DIARIA",
        "cut_criterion": 0.2,
        "reverse_cut": False
    },
    {
        "parameter": "DY",
        "cut_criterion": 0.3,
        "reverse_cut": True
    },
    {
        "parameter": "DY",
        "cut_criterion": 0.04,
        "reverse_cut": False
    },
    {
        "parameter": "MARGEM BRUTA",
        "cut_criterion": 0.2,
        "reverse_cut": False
    },
    {
        "parameter": "MARG. LIQUIDA",
        "cut_criterion": 0.12,
        "reverse_cut": False
    },
    {
        "parameter": "LIQ. CORRENTE",
        "cut_criterion": 1.05,
        "reverse_cut": False
    },
    {
        "parameter": "P/L",
        "cut_criterion": 7,
        "reverse_cut": True
    },
    {
        "parameter": "DIV. LIQ. / PATRI.",
        "cut_criterion": 0.55,
        "reverse_cut": True
    },
    {
        "parameter": "ROE",
        "cut_criterion": 0.15,
        "reverse_cut": False
    }

]

filtros = [
    {
        "parameter": "CRESCIMENTO MEDIO",
        "cut_criterion": 0.1,
        "reverse_cut": False
    },
    {
        "parameter": "DESCONTO (GRAHAM)",
        "cut_criterion": 0.3,
        "reverse_cut": False
    },
    {
        "parameter": "DESCONTO (BAZIN)",
        "cut_criterion": 0.2,
        "reverse_cut": False
    },
    {
        "parameter": "DESCONTO (GORDON)",
        "cut_criterion": 0,
        "reverse_cut": False
    }
]

filtros += filtros_comuns

rank = {
    "parameter": "DESCONTO (GRAHAM)",
    "ascending": False
}

initial_list = stock_info.get_top_stocks_by_conditions(
    conditionals=filtros, sort_by=rank, num_stocks=600)

print("\nPrimeira lista")
print_list(initial_list)
print(len(initial_list))

# second list

filtros = [

    {
        "parameter": "DESCONTO (GRAHAM)",
        "cut_criterion": 0.5,
        "reverse_cut": False
    },
    {
        "parameter": "CRESCIMENTO MEDIO",
        "cut_criterion": 0.2,
        "reverse_cut": False
    },
    {
        "parameter": "RANK GREENBLATT",
        "cut_criterion": 100,
        "reverse_cut": True
    }
]

filtros += filtros_comuns

second_list = union_lists(initial_list,
                          stock_info.get_top_stocks_by_conditions(conditionals=filtros, sort_by=rank, num_stocks=600))

print("Segunda lista")
print_list(second_list)
print(len(second_list))

filtros = [

    {
        "parameter": "DESCONTO (GRAHAM)",
        "cut_criterion": 0.3,
        "reverse_cut": False
    },
    {
        "parameter": "CRESCIMENTO MEDIO",
        "cut_criterion": 0.1,
        "reverse_cut": False
    },
    {
        "parameter": "RANK GREENBLATT",
        "cut_criterion": 50,
        "reverse_cut": True
    }
]

filtros += filtros_comuns

third_list = union_lists(second_list,
                         stock_info.get_top_stocks_by_conditions(conditionals=filtros, sort_by=rank, num_stocks=600))

print("Terceira lista")
print_list(third_list)
print(len(third_list))
