import os, time
from web3 import Web3
from web3_base.web3_base import Web3Base
from web3_base.includes.config import *
from web3_base.tools.utils import *

tq_contracts = dict(
    tqONE="0x34B9aa82D89AE04f0f546Ca5eC9C93eFE1288940",
    tq1WBTC="0xd9c0D8Ad06ABE10aB29655ff98DcAAA0E059184A",
    tq1ETH="0xc63AB8c72e636C9961c5e9288b697eC5F0B8E1F7",
    tq1USDC="0xCa3e902eFdb2a410C952Fd3e4ac38d7DBDCB8E96",
    tq1USDT="0x7af2430eFa179dB0e76257E5208bCAf2407B2468",
)


class Tranq(Web3Base):
    def __init__(self, contract: str, gas_price: int, *args, **kw) -> None:
        self.contract = w3.eth.contract(address=contract, abi=abi)
        self.gas_price = w3.toWei(gas_price, "gwei")
        super().__init__(*args, **kw)

    def tq_balance(self) -> int:
        balanceOf = self.contract.functions.balanceOf(self.account).call()
        return balanceOf

    def get_rate(self) -> int:
        rate = int(self.contract.functions.exchangeRateStored().call() / 10 ** 16)
        return rate

    def deposited_one(self) -> int:
        balanceOne = int(self.tq_balance() * self.get_rate() / 100)
        log.info(f"balanceOne    ::  {balanceOne}")
        return balanceOne

    def borrowed_balance(self) -> int:
        borrowBalance = self.contract.functions.borrowBalanceCurrent(
            self.account
        ).call()
        log.info(f"borrowed  ::  {borrowBalance}")
        return borrowBalance

    def max_borrow_amount(self) -> int:
        max_wei_available = int(self.deposited_one() // 100 * 65)
        log.info(f"Max borrow       ::  {max_wei_available}")
        return max_wei_available

    def percent_borrowed(self) -> int:
        perc_borrowed = self.borrowed_balance() / self.max_borrow_amount() * 100
        log.info(f"% borrowed       ::  {round(perc_borrowed, 2)}%")
        return perc_borrowed

    def percentage_left(self) -> int:
        perc_left = 100 - self.percent_borrowed()
        log.info(f"% Left           ::  {round(perc_left, 2)}%")
        return perc_left

    def minus_percent(self, amount: int, percent: int) -> int:
        x_percent = int(amount / 100 * percent)
        new_total = amount - x_percent
        log.info(f"Total Minus {x_percent}  ::  {new_total}")
        return new_total

    def left_to_borrow(self) -> int:
        can_borrow = self.max_borrow_amount() - self.borrowed_balance()
        log.info(f"Left to Borrow   ::  {can_borrow}")
        return can_borrow

    # def readable_amounts(self, amount_wei: int, name: str = "Amount") -> float:
    #     readable = round(amount_wei / 10 ** 18, 2)
    #     log_msg = f"{name}   ::  {readable}"
    #     log.info(log_msg)
    #     return readable  # , log_msg

    def calc_amount_by_rate(self, amount) -> int:
        calc = int(amount / self.get_rate()) * 100
        log.info(f"calculated amount      ::  {calc}\n")
        return calc

    def deposit(self, amount: int) -> None:
        log.info(f"Trying to Deposit  ::  {readable_price(amount)}")
        try:
            signed_txn = self.build_tx_with_function(
                self.contract.functions.mint, self.gas_price, value=amount
            )
            self.process_tx(signed_txn)
        except ValueError as e:
            log.error(f"issue with Depositing [ {amount} ]  ::  {e}")

    def withdraw(self, amount: int) -> None:
        log.info(f"Trying to withdraw  ::  {readable_price(amount)}")
        try:
            withdraw = self.calc_amount_by_rate(amount)
            signed_txn = self.build_tx_with_function(
                self.contract.functions.redeem, gas_price, func_args=(withdraw,)
            )
            self.process_tx(signed_txn)
        except ValueError as e:
            log.error(f"issue with withdrawing [ {amount} ]  ::  {e}")

    def borrow(self, amount: int) -> None:
        log.info(f"Trying to Borrow  :: $ {readable_price(amount)}")
        try:
            signed_txn = self.build_tx_with_function(
                self.contract.functions.borrow, gas_price, func_args=(amount,)
            )
            self.process_tx(signed_txn)
        except ValueError as e:
            log.error(f"issue with Borrowing [ {amount} ]  ::  {e}")

    def repay(self, amount: int) -> None:
        log.info(f"Trying to repay  ::  {readable_price(amount)}")
        try:
            signed_txn = self.build_tx_with_function(
                self.contract.functions.repayBorrow, gas_price, value=amount
            )
            self.process_tx(signed_txn)
        except ValueError as e:
            log.error(f"issue with repaying [ {amount} ]  ::  {e}")

    def repay_all_borrow_from_deposit(
        self,
        amount_less_than_max: int = 1000,
        repay_buffer: int = 3,
        buffer_amount: int = 100,
        stop_at_amount: int = 0,
    ) -> None:
        # buffer
        minus_amount = tx.w3.toWei(amount_less_than_max, "ether")
        minus_repay_buffer = tx.w3.toWei(repay_buffer, "ether")
        buffer = tx.w3.toWei(buffer_amount, "ether")
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

            self.withdraw(left)

            time.sleep(2)

            b = self.balance()
            if b >= stop_at_amount and stop_at_amount > 0:
                log.info(f"Amount in wallet is  {b}.. Exiting..")
                break

            repay = tx.w3.toWei(b, "ether") - minus_repay_buffer

            if self.borrowed_balance() < repay:
                repay = self.borrowed_balance()

            self.repay(repay)

            time.sleep(2)

    def fill_borrow_from_deposit(self, percent: float = 2, buffer: int = 3) -> None:
        minus_repay_buffer = tx.w3.toWei(buffer, "ether")

        while True:
            borrow_flag = True
            deposit_flag = True
            b = self.balance()
            # check amount to borrow > left borrow - percent
            perc_left = self.percentage_left()
            log.info(f"perc_left  ::  {perc_left}")

            if perc_left <= percent:
                if b <= buffer:
                    log.info("Max percentage left reached.  Exiting..")
                    break
                else:
                    log.info("Borrow Flag False")
                    borrow_flag = False

            # borrow
            if borrow_flag:
                # get max borrow amount
                grab_borrow = self.left_to_borrow()

                # minus percent in wei.
                to_borrow = self.minus_percent(grab_borrow, percent)
                self.borrow(to_borrow)

            time.sleep(2)

            if deposit_flag:
                # deposit
                deposit_amount = tx.w3.toWei(b, "ether") - minus_repay_buffer
                self.deposit(deposit_amount)

            time.sleep(2)


if __name__ == "__main__":
    contract = tq_contracts["tqONE"]
    fn = os.path.join("web3_base", "abis", "tranqONE.json")
    abi = get_abi(fn)
    w3 = Web3(Web3.WebsocketProvider(wss_url))
    tx = Tranq(contract, 50, w3, envs.p_key, abi=abi)

    # amount = tx.w3.fromWei(1000, "ether")
    # print(amount)
    # print(tx.gas_price)
    # tx.withdraw(amount)
    # time.sleep(1)
    # tx.repay(amount)

    # tx.repay_all_borrow_from_deposit(amount_less_than_max=1000, repay_buffer=3, buffer_amount= 100, stop_at_amount=68000)
    tx.fill_borrow_from_deposit(percent=2)
