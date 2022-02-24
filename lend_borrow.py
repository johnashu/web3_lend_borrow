import time
from web3_base.web3_base import Web3Base
from web3_base.includes.config import *
from web3_base.tools.utils import *


class LendBorrow(Web3Base):
    def __init__(
        self, contract: str, gas_price: int, MAX_BORROW_AMOUNT: int, *args, **kw
    ) -> None:
        self.MAX_BORROW_AMOUNT = MAX_BORROW_AMOUNT
        super().__init__(*args, **kw)
        self.contract = self.w3.eth.contract(address=contract, abi=self.abi)
        self.gas_price = self.w3.toWei(gas_price, "gwei")

    def token_balance(self) -> int:
        balanceOf = self.contract.functions.balanceOf(self.account).call()
        return balanceOf

    def get_rate(self) -> int:
        rate = int(self.contract.functions.exchangeRateStored().call() / 10 ** 16)
        return rate

    def deposited_token(self) -> int:
        balanceToken = int(self.token_balance() * self.get_rate() / 100)
        log.info(f"balanceToken    ::  {balanceToken}")
        return balanceToken

    def borrowed_balance(self) -> int:
        borrowBalance = self.contract.functions.borrowBalanceCurrent(
            self.account
        ).call()
        log.info(f"borrowed  ::  {borrowBalance}")
        return borrowBalance

    def max_borrow_amount(self) -> int:
        max_wei_available = int(self.deposited_token() // 100 * self.MAX_BORROW_AMOUNT)
        log.info(f"Max borrow       ::  {max_wei_available}")
        return max_wei_available

    def percent_borrowed(self) -> int:
        perc_borrowed = self.borrowed_balance() / self.max_borrow_amount() * 100
        perc_borrowed = round(perc_borrowed, 2)
        log.info(f"% borrowed       ::  {perc_borrowed}%")
        return perc_borrowed

    def percentage_left(self) -> int:
        perc_left = 100 - self.percent_borrowed()
        perc_left = round(perc_left, 2)
        log.info(f"% Left           ::  {perc_left}%")
        return perc_left

    def minus_percent(self, amount: int, percent: int) -> int:
        x_percent = int(self.max_borrow_amount() / 100 * percent)
        new_total = amount - x_percent
        log.info(f"Total Minus {x_percent}  ::  {new_total}")
        return new_total

    def left_to_borrow(self) -> int:
        can_borrow = self.max_borrow_amount() - self.borrowed_balance()
        log.info(f"Left to Borrow   ::  {can_borrow}")
        return can_borrow

    def calc_amount_by_rate(self, amount: int) -> int:
        calc = int(amount / self.get_rate()) * 100
        log.info(f"calculated amount      ::  {calc}\n")
        return calc

    def deposit(self, amount: int, **kw) -> None:
        log.info(f"Trying to Deposit  ::  {readable_price(amount)}")
        try:
            signed_txn = self.build_tx_with_function(
                self.contract.functions.mint, self.gas_price, value=amount
            )
            self.process_tx(signed_txn, **kw)
        except ValueError as e:
            log.error(f"issue with Depositing [ {amount} ]  ::  {e}")

    def withdraw(self, amount: int, **kw) -> None:
        log.info(f"Trying to withdraw  ::  {readable_price(amount)}")
        try:
            withdraw = self.calc_amount_by_rate(amount)
            signed_txn = self.build_tx_with_function(
                self.contract.functions.redeem, self.gas_price, func_args=(withdraw,)
            )
            self.process_tx(signed_txn, **kw)
        except ValueError as e:
            log.error(f"issue with withdrawing [ {amount} ]  ::  {e}")

    def borrow(self, amount: int, **kw) -> None:
        log.info(f"Trying to Borrow  :: {readable_price(amount)}")
        try:
            signed_txn = self.build_tx_with_function(
                self.contract.functions.borrow, self.gas_price, func_args=(amount,)
            )
            self.process_tx(signed_txn, **kw)
        except ValueError as e:
            log.error(f"issue with Borrowing [ {amount} ]  ::  {e}")

    def repay(self, amount: int, **kw) -> None:
        log.info(f"Trying to repay  ::  {readable_price(amount)}")
        try:
            signed_txn = self.build_tx_with_function(
                self.contract.functions.repayBorrow, self.gas_price, value=amount
            )
            self.process_tx(signed_txn, **kw)
        except ValueError as e:
            log.error(f"issue with repaying [ {amount} ]  ::  {e}")

    def repay_all_borrow_from_deposit(
        self,
        amount_less_than_max: int = 1000,
        repay_buffer: int = 3,
        buffer_amount: int = 100,
        stop_at_amount: int = 0,
        test_run: bool = False,
    ) -> None:
        # buffer
        minus_amount = self.w3.toWei(amount_less_than_max, "ether")
        minus_repay_buffer = self.w3.toWei(repay_buffer, "ether")
        buffer = self.w3.toWei(buffer_amount, "ether")
        while 1:

            if self.borrowed_balance() <= 50000000:
                log.info("Borrowed amounts paid..")
                break

            left = self.left_to_borrow() - minus_amount

            grab_borrow = self.left_to_borrow() - self.borrowed_balance()

            if grab_borrow > buffer:
                left = self.borrowed_balance() + minus_repay_buffer

            if left <= 0:
                log.error("Not enough Buffer to continue.. Exiting..")
                break
            if not test_run:
                self.withdraw(left)

            b = self.balance()
            if b >= stop_at_amount and stop_at_amount > 0:
                log.info(f"Amount in wallet is  {b}.. Exiting..")
                break

            repay = self.w3.toWei(b, "ether") - minus_repay_buffer

            if self.borrowed_balance() < repay:
                repay = self.borrowed_balance()

            if not test_run:
                self.repay(repay)

    def fill_borrow_from_deposit(
        self,
        percent: float = 2,
        buffer: int = 3,
        GAS_AMOUNT: float = 0.01,
        test_run: bool = False,
    ) -> None:
        minus_repay_buffer = self.w3.toWei(buffer, "ether")

        while True:
            deposit_flag = True
            borrow_flag = True
            b = self.balance()
            perc_left = self.percentage_left()
            b_wei = self.w3.toWei(b, "ether")

            log.info(f"Current Balance  ::  {b}")
            log.info(f"perc_left  ::  {perc_left}")
            log.info(f"perc_left <= percent  ::  {perc_left <= percent}")
            log.info(f"b_wei  ::  {b_wei}")
            log.info(f"minus_repay_buffer  ::  {minus_repay_buffer}")
            log.info(f"b_wei <= minus_repay_buffer  ::  {b_wei <= minus_repay_buffer}")

            if b_wei <= minus_repay_buffer:
                deposit_flag = False
                log.info(f"Deposit Flag False")

            if perc_left <= percent:
                log.info("Borrow Flag False")
                borrow_flag = False

            if not deposit_flag and not borrow_flag:
                log.info("Max percentage left reached.  Exiting..")
                break

            # borrow
            if borrow_flag:
                # get max borrow amount
                grab_borrow = self.left_to_borrow()

                # minus percent in wei.
                to_borrow = self.minus_percent(grab_borrow, percent)
                if to_borrow < self.w3.toWei(GAS_AMOUNT, "ether"):
                    log.info("Amount less than gas.. Not borrowing..")
                    borrow_flag = False
                else:
                    if not test_run:
                        self.borrow(to_borrow)

            # deposit
            if deposit_flag:
                if not test_run:
                    deposit_amount = self.w3.toWei(b, "ether") - minus_repay_buffer
                    self.deposit(deposit_amount)
