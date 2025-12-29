from .tax_system import TaxSystem

# Tarieven 2026
FORFAITAIR_RENDEMENT = 0.06
BELASTING_TARIEF = 0.36
BELASTING_VRIJE_VOET = 59.357

class Box3_2026(TaxSystem):

    def __init__(self, start_amount):
        super().__init__(start_amount)


    def do_year(self, interest):

        profit = self._get_profit(self.balance, interest)

        taxable = max(0, self.balance - BELASTING_VRIJE_VOET)
        profit_fictief = taxable * FORFAITAIR_RENDEMENT

        # Tegenbewijsregeling
        profit_werkelijk = taxable * interest if interest > 0 else 0

        # Kies laagste rendement
        taxable_profit = min(profit_fictief, profit_werkelijk)
        tax = taxable_profit * BELASTING_TARIEF

        new_balance = self.balance + profit - tax

        self.balance = new_balance
        self.bruto_balance = new_balance
        self.netto_balance = new_balance

        self.bruto_tax_payed += tax
        self.netto_tax_payed += tax

        self.year += 1

        # print(f"Year: {self.year:2,} Profit: {int(profit):6,} Tax: {int(tax):6,} Balance: {int(self.balance):8,}")

        return
