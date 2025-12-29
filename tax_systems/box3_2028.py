from .tax_system import TaxSystem

BELASTING_TARIEF = 0.36
HEFFINGSVRIJ = 1800


class Box3_2028(TaxSystem):

    loss_carry_forward = 0.0

    def __init__(self, start_amount):
        super().__init__(start_amount)


    def do_year(self, interest):

        profit = self._get_profit(self.balance, interest)

        if profit < 0:
            tax = 0

            # verlies -> carry forward (mits > 500)
            loss = -profit
            if loss > 500:
                self.loss_carry_forward += (loss - 500)

        else:
            # winst: eerst compenseer carry-forward
            taxable = profit - HEFFINGSVRIJ - self.loss_carry_forward
            if taxable < 0:
                # nog niet genoeg winst om vrijstelling + verlies eruit te halen
                tax = 0
                if self.loss_carry_forward > profit:
                    self.loss_carry_forward -= profit
                else:
                    self.loss_carry_forward = 0

            else:
                tax = taxable * BELASTING_TARIEF
                # reset carry-forward
                self.loss_carry_forward = 0

        new_balance = self.balance + profit - tax

        self.balance = new_balance
        self.bruto_balance = new_balance
        self.netto_balance = new_balance

        self.bruto_tax_payed += tax
        self.netto_tax_payed += tax

        self.year += 1

        # print(f"Year: {self.year:2,} Profit: {int(profit):6,} Tax: {int(tax):6,} Balance: {int(self.balance):8,}")

        return
