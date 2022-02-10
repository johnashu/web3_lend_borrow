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

    def max_wei_left(self) -> int:
        max_wei_available = int(self.deposited_one() // 100 * 65)
        log.info(f"Max borrow       ::  {max_wei_available}")
        return max_wei_available

    def percent_borrowed(self) -> int:
        perc_borrowed = self.borrowed_balance() / self.max_wei_left() * 100
        log.info(f"% borrowed       ::  {round(perc_borrowed, 2)}%")
        return perc_borrowed

    def percentage_left(self) -> int:
        perc_left = 100 - self.percent_borrowed()
        log.info(f"% Left           ::  {round(perc_left, 2)}%")

    def wei_left_to_borrow(self) -> int:
        can_borrow = self.max_wei_left() - self.borrowed_balance()
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
        signed_txn = self.tx_function(
            self.contract.functions.mint, self.gas_price, value=amount
        )
        self.process_tx(signed_txn)

    def withdraw(self, amount: int) -> None:
        withdraw = self.calc_amount_by_rate(amount)
        signed_txn = self.tx_function(
            self.contract.functions.redeem, gas_price, func_args=(withdraw,)
        )
        self.process_tx(signed_txn)

    def borrow(self, amount: int) -> None:
        signed_txn = self.tx_function(
            self.contract.functions.borrow, gas_price, func_args=(amount,)
        )
        self.process_tx(signed_txn)

    def repay(self, amount: int) -> None:
        signed_txn = self.tx_function(
            self.contract.functions.repayBorrow, gas_price, value=amount
        )
        self.process_tx(signed_txn)

    def repay_all_borrow_from_deposit(self) -> None:
        # buffer
        minus_amount = tx.w3.toWei("1000", "ether")
        minus_repay_buffer = tx.w3.toWei("3", "ether")
        buffer = tx.w3.toWei("100", "ether")
        while 1:
            if self.borrowed_balance() <= 50000000:
                log.info("Borrowed amounts paid..")
                break

            left = self.max_wei_left() - minus_amount
            grab_borrow = self.wei_left_to_borrow() - self.borrowed_balance()
            if grab_borrow > buffer:
                left = self.borrowed_balance()
            log.info(f"Trying to withdraw  ::  {self.readable_price(left)}")
            if left <= 0:
                log.error("Not enough Buffer to continue.. Exiting..")
                break
            try:
                self.withdraw(left)
            except ValueError as e:
                log.error(f"issue with withdrawing [ {left} ]  ::  {e}")
            time.sleep(2)
            b = self.balance()
            repay = tx.w3.toWei(b, "ether") - minus_repay_buffer
            if self.borrowed_balance() < repay:
                repay = self.borrowed_balance()
            log.info(f"Trying to repay  ::  {self.readable_price(repay)}")
            try:
                self.repay(repay)
            except ValueError as e:
                log.error(f"issue with reapaying [ {left} ]  ::  {e}")
            time.sleep(2)


if __name__ == "__main__":
    contract = tq_contracts["tqONE"]
    fn = os.path.join("web3_base", "abis", "tranqONE.json")
    abi = get_abi(fn)
    w3 = Web3(Web3.WebsocketProvider(wss_url))
    tx = Tranq(contract, 50, w3, envs.p_key, abi=abi)

    amount = tx.w3.fromWei(1000, "ether")
    print(amount)
    print(tx.gas_price)

    tx.repay_all_borrow_from_deposit()
    # tx.withdraw(amount)
    # time.sleep(1)
    # tx.repay(amount)
