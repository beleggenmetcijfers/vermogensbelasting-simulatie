# box2.py
from .tax_system import TaxSystem

# VPB tarieven 2026
VPB_TARIEF_LAAG = 0.19
VPB_TARIEF_HOOG = 0.258
VPB_SCHIJF_GRENS = 200_000

# Box 2 tarieven 2026
BOX2_TARIEF_LAAG = 0.245
BOX2_TARIEF_HOOG = 0.31
BOX2_SCHIJF_GRENS = 68_843


DIVIDEND_YIELD = 0.015  # 1.5% default

class Box2(TaxSystem):

    agio_balance : int
    kostprijs_waarderen : bool

    loss_carry_forward : int
    total_dividend : int
    total_tax_dividend : int

    def __init__(self, start_amount, of_which_agio, kostprijs_waarderen: bool = False):
        """
        agio_storting: bedrag dat (onbelast) in de BV is gestort bovenop nominale kapitaal.
        kostprijs_waarderen: als True -> VPB wordt niet jaarlijks betaald, maar alleen bij 'verkoop'/uitdeling (kostprijswaardering).
        """

        super().__init__(start_amount)

        self.agio_balance = float(of_which_agio)
        self.kostprijs_waarderen = bool(kostprijs_waarderen)

        self.loss_carry_forward = 0.0
        self.total_dividend = 0
        self.total_tax_dividend = 0

        self.__recalculate_balances(self.balance)


    def _get_tax_vpb(self, profit):
        # We assume always the lowest tariff
        if profit <= 0:
            return 0.0
        return profit * VPB_TARIEF_LAAG

    def _get_tax_box2(self, bruto_balance: float) -> float:
        # We assume we can always payout in lowest tariff
        taxable = bruto_balance - self.agio_balance
        if taxable <= 0:
            return 0.0
        return taxable * BOX2_TARIEF_LAAG

        # if distrib_amount <= BOX2_SCHIJF_GRENS:
        #     tax += distrib_amount * BOX2_TARIEF_LAAG
        # else:
        #     tax += BOX2_SCHIJF_GRENS * BOX2_TARIEF_LAAG
        #     tax += (distrib_amount - BOX2_SCHIJF_GRENS) * BOX2_TARIEF_HOOG

        # return round(tax, 2)


    def __recalculate_balances(self, end_balance):

        self.balance = end_balance

        if self.kostprijs_waarderen:
            profit = self.balance - self.start_amount - self.total_dividend
            tax_vpb = self._get_tax_vpb(profit)

            self.bruto_balance = self.balance - tax_vpb
            self.bruto_tax_payed = tax_vpb + self.total_tax_dividend

        else:
            # VPB has already been payed
            self.bruto_balance = self.balance

        tax_box2 = self._get_tax_box2(self.bruto_balance)

        self.netto_tax_payed = tax_box2
        self.netto_balance = self.bruto_balance - tax_box2


    def do_year(self, interest):

        start_balance = self.balance
        profit = self._get_profit(self.balance, interest)
        new_balance = self.balance + profit

        if self.kostprijs_waarderen:
            # Only subtract tax payed on dividends
            dividend = start_balance * DIVIDEND_YIELD
            tax_dividend =  self._get_tax_vpb(dividend)

            new_balance -= tax_dividend
            self.total_dividend += dividend
            self.total_tax_dividend += tax_dividend

        else:
            taxable = profit

            if profit <= 0:
                # voeg het verlies toe aan carry forward (positief bedrag)
                self.loss_carry_forward += (-profit)
                taxable = 0

            elif profit <= self.loss_carry_forward:
                self.loss_carry_forward -= profit
                taxable = 0

            else:
                taxable -= self.loss_carry_forward
                self.loss_carry_forward = 0.0

            tax = self._get_tax_vpb(taxable)
            # subtract tax from balance
            new_balance -= tax
            self.bruto_tax_payed += tax

        self.year += 1
        self.__recalculate_balances(new_balance)
        return
