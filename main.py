import argparse
import pandas as pd
import numpy as np

from tax_systems.tax_system import TaxSystem
from tax_systems.market import Market
from tax_systems.fixed_interest import FixedInterest
from tax_systems.box3_2026 import Box3_2026
from tax_systems.box3_2028 import Box3_2028
from tax_systems.box2 import Box2
from graphs import *

# customize settings below
START_BALANCE = 100_000
SPANS = [5, 10, 20, 30, 50, 75]

def rnd(x):
    return int(round(x, 0))

def get_period_yield(start, end, n):
    return round(((end / start) ** (1/n) - 1) * 100, 2)

def to_datetime(tm: pd.Series):
    return pd.Timestamp(f"{tm:.2f}")

def get_price_inc_dividend(df : pd.DataFrame):
    result = []
    prev = 0

    for time, row in df.iterrows():

        if not result:
            # First month its equal to the real price
            result.append(row['Price'])
            prev = row['Price']
            continue

        pos = df.index.get_loc(time)
        prev_price = df.iloc[pos-1]['Price']

        period_divided = row['Dividend'] / 12

        if np.isnan(period_divided):
            period_divided = 0
        period_return = ((row['Price']  +  period_divided) / prev_price)

        price_inc_div = prev * period_return
        prev = price_inc_div
        result.append(round(price_inc_div, 2))

    return result

def add_ath_distance(df, price_col="Price Inc Dividend"):
    ath = df[price_col].cummax()
    df["Pct Below ATH"] = 1 - (df[price_col] / ath)
    return df

def get_statistics(balances, start, years):

    balances = sorted(balances)
    n = len(balances)

    stats = {
        "min*" : get_period_yield(start, balances[0], years),
        "10%*" : get_period_yield(start, balances[int(n * 0.10)], years),
        # "q1" : get_period_yield(start, balances[int(n * 0.25)], years),
        "med*" : get_period_yield(start, balances[int(n * 0.50)], years),
        "avg*" : get_period_yield(start, np.mean(balances), years),
        # "q3" : get_period_yield(start, balances[int(n * 0.75)], years),
        "90%*" : get_period_yield(start, balances[int(n * 0.90)], years),
        "max*" : get_period_yield(start, balances[n-1], years),
        "avg balance" : rnd(np.mean(balances)),
    }

    return stats

def winrate_matrix(balances: dict, year):
    keys = list(balances.keys())
    n = len(balances[keys[0]][year])

    matrix = pd.DataFrame(index=keys, columns=keys, dtype=float)

    for kx in keys:
        for ky in keys:
            if kx == ky:
                matrix.loc[kx, ky] = np.nan
                continue

            wins = 0
            for i in range(n):
                if balances[kx][year][i] > balances[ky][year][i]:
                    wins += 1

            matrix.loc[kx, ky] = round(100 * wins / n, 1)

    return matrix

def get_rolling_returns(df, years, ath_percentage=100):
    out = []

    dates = df.index
    max_date = dates.max()

    for start_date in dates:
        end_date = start_date + pd.DateOffset(years=years)

        if end_date > max_date:
            break  # end_dates will be invalid onwards

        # Only inlclude start points below ATH percentage
        # default=100, so all included
        if df.loc[start_date, "Pct Below ATH"] > (ath_percentage / 100):
            continue

        start_price = df.loc[start_date, "Price Inc Dividend"]
        yearly = []

        for y in range(1, years + 1):
            target = start_date + pd.DateOffset(years=y)

            if target in df.index:
                end = df.loc[target, "Price Inc Dividend"]
            else:
                idx = df.index.get_indexer([target], method="nearest")[0]
                end = df.iloc[idx]["Price Inc Dividend"]

            year_return = (end / start_price) - 1
            yearly.append(year_return)
            start_price = end

        assert(end == df.loc[end_date, "Price Inc Dividend"])

        out.append(yearly)

    return out

def run_with_samples(label, system_cls, start_amount, samples):
    balances = {}
    for yearly_returns in samples:
        system = system_cls(start_amount)

        for year, r in enumerate(yearly_returns):
            system.do_year(r)
            balances.setdefault(year + 1, []).append(system.netto_balance)

    return balances

def run_with_samples_with_switch(label, system_cls_first, system_cls_second, start_amount, samples):
    balances = {}

    for yearly_returns in samples:
        year = 0
        system_first = system_cls_first(start_amount)
        for r in yearly_returns[:2]:
            system_first.do_year(r)
            year += 1
            balances.setdefault(year, []).append(system_first.netto_balance)

        system_second = system_cls_second(system_first.netto_balance)

        for r in yearly_returns[2:]:
            system_second.do_year(r)
            year += 1
            balances.setdefault(year, []).append(system_second.netto_balance)

    return balances




def run_years(label, system : TaxSystem, years):

    for i in range(1, years + 1):
        system.do_year(0.10)

    print(f"== {label}")
    print(f"Balance: {rnd(system.balance      ):9,}  Yearly Yield: {get_period_yield(system.start_amount, system.balance, years):4}%")
    print(f"Bruto  : {rnd(system.bruto_balance):9,}  Yearly Yield: {get_period_yield(system.start_amount, system.bruto_balance, years):4}%")
    print(f"Netto  : {rnd(system.netto_balance):9,}  Yearly Yield: {get_period_yield(system.start_amount, system.netto_balance, years):4}%")
    print("")


def run_years_static(start):

    for year in SPANS:
        print(f"\n=== Samples: {year} jaar ===")

        run_years("Box 3 2026", Box3_2026(start), year)
        run_years("Box 3 2028", Box3_2028(start), year)
        run_years("Box 2 VPB", Box2(start, start, kostprijs_waarderen=False), year)
        run_years("Box 2 kostprijs", Box2(start, start, kostprijs_waarderen=True), year)


def main(mode, market_data_file, max_years, ath_percentage):

    df = pd.read_csv(market_data_file, delimiter=";")
    df['Date'] = df['Date'].apply(lambda t: pd.Timestamp(f"{t:.2f}"))
    df = df.set_index("Date")
    df['Price Inc Dividend'] = get_price_inc_dividend(df)

    df = add_ath_distance(df)

    print(f"   Period: {rnd(len(df) / 12):3} years")
    print(f"5% >= ATH: {rnd(len(df[ df['Pct Below ATH'] <= 0.05]) / 12):3} years")
    print(f"      ATH: {rnd(len(df[ df['Pct Below ATH'] == 0]) / 12):3} years")

    max_year = min(max_years, max(SPANS))

    if mode == 'transition':

        samples = get_rolling_returns(df, max_year, ath_percentage)

        balances = {}
        balances['Market'] = run_with_samples("Market", Market, START_BALANCE, samples)
        balances['Box 3 26 > Box 3 28'] = run_with_samples_with_switch("", Box3_2026, Box3_2028, START_BALANCE, samples)
        balances['Savings Acc > Box 2'] = run_with_samples_with_switch("Box 3 2026", FixedInterest, lambda s: Box2(s, s, kostprijs_waarderen=True), START_BALANCE, samples)
        balances['Box 3 26 > Box 2'] = run_with_samples_with_switch("Box 3 2026", Box3_2026, lambda s: Box2(s, s, kostprijs_waarderen=True), START_BALANCE, samples)
        balances['Box 2 Kostprijs'] = run_with_samples("Box 2 Kostprijs", lambda s: Box2(s, s, kostprijs_waarderen=True), START_BALANCE, samples)


        for year in SPANS:
            if year > max_year:
                continue

            print(f"\n=== Samples: {year} jaar ===")

            statistics = []
            # get statistics
            for k, balance in balances.items():
                res = {"Name" : k}
                res.update(get_statistics(balance[year], START_BALANCE, year))
                statistics.append(res)

                # index_min = min(range(len(balance[year])), key=balance[year].__getitem__)
                # print(f"{k:20} MIN:", samples[index_min])

            print(pd.DataFrame(statistics).to_markdown(index=False))
            print("*Compound Annual Growth Rate (CAGR)")
            print(winrate_matrix(balances, year))

        plot_median_balances(balances, "Tax systems", f"output/transition_{max_year}yrs_{rnd(START_BALANCE/1000)}k.pdf")
        plot_median_with_min_max(balances, "Tax systems", f"output/transition_{max_year}yrs_{rnd(START_BALANCE/1000)}k_itv.pdf")

    elif mode == 'long_term':

        samples = get_rolling_returns(df, max_year, ath_percentage)

        balances = {}
        balances['Market'] = run_with_samples("Market", Market, START_BALANCE, samples)
        balances['Box 3 2026'] = run_with_samples("Box 3 2026", Box3_2026, START_BALANCE, samples)
        balances['Box 3 2028'] = run_with_samples("Box 3 2028", Box3_2028, START_BALANCE, samples)
        balances['Box 2 VPB'] = run_with_samples("Box 2 VPB", lambda s: Box2(s, s, kostprijs_waarderen=False), START_BALANCE, samples)
        balances['Box 2 Kostprijs'] = run_with_samples("Box 2 VPB", lambda s: Box2(s, s, kostprijs_waarderen=True), START_BALANCE, samples)


        for year in SPANS:
            if year > max_year:
                continue

            print(f"\n=== Samples: {year} jaar ===")

            statistics = []
            # get statistics
            for k, balance in balances.items():
                res = {"Name" : k}
                res.update(get_statistics(balance[year], START_BALANCE, year))
                statistics.append(res)

            print(pd.DataFrame(statistics).to_markdown(index=False))
            print("*Compound Annual Growth Rate (CAGR)")
            print(winrate_matrix(balances, year))

        plot_median_balances(balances, "Tax systems", f"output/long_term_comparison_{max_year}yrs_{rnd(START_BALANCE/1000)}k.pdf")
        plot_median_with_min_max(balances, "Tax systems", f"output/long_term_comparison_{max_year}yrs_{rnd(START_BALANCE/1000)}k_itv.pdf")

    elif mode == 'static':
        run_years_static(START_BALANCE)


if __name__ == '__main__':
    arg_parser = argparse.ArgumentParser(description='Dutch Wealth-tax simulation')
    arg_parser.add_argument('mode', choices=['static', 'transition', 'long_term'], help='mode', default='long_term')
    arg_parser.add_argument("-d", "--data", help="market_data csv", required=True)
    arg_parser.add_argument("-y", "--max-years", help="max number of years to run", default=50, type=int)
    arg_parser.add_argument("-a", "--ath-percentage", help="if set, only include start-points within given ATH percentage (default=100)", default=100, type=int)
    args = arg_parser.parse_args()

    if args.ath_percentage > 100 or args.ath_percentage < 0:
        print("Invalid ATH percentage: Give number between 0 and 100")

    main(args.mode, args.data, args.max_years, args.ath_percentage)
