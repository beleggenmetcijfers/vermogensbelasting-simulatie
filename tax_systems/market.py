from .tax_system import TaxSystem

FORFAITAIR_RENDEMENT = 0.06
BELASTING_TARIEF = 0.36
BELASTING_VRIJE_VOET = 59.357  # 2024, 1 persoon

class Market(TaxSystem):

    def __init__(self, start_amount):
        super().__init__(start_amount)


    def do_year(self, interest):

        profit = self._get_profit(self.balance, interest)

        new_balance = self.balance + profit

        self.balance = new_balance
        self.bruto_balance = new_balance
        self.netto_balance = new_balance

        self.year += 1
        return
