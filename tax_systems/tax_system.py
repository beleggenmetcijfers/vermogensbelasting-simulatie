

class TaxSystem:

    start_amount : int

    balance : int
    bruto_balance : int

    netto_balance : int

    bruto_tax_payed : int
    netto_tax_payed : int

    year : int

    def __init__(self, start_amount):

        self.start_amount = start_amount

        self.balance = start_amount
        self.bruto_balance = start_amount
        self.netto_balance = start_amount

        self.bruto_tax_payed = 0
        self.netto_tax_payed = 0

        self.year = 0

    def _get_profit(self, start_amount, interest):

        profit = start_amount * interest
        return profit

    def do_year(self, interest):
        pass



    def get_year_tax(self, start_amount, end_amount) -> int:
        # implement
        assert(False)

    def get_final_tax(self):
        # implement
        assert(False)


    def get_final_tax_bruto(self, start_amount: float, end_amount: float) -> float:
        assert(False)

    def get_final_tax_netto(self, start_amount: float, end_amount: float) -> float:
        assert(False)
