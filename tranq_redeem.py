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

contract = tq_contracts["tqONE"]
fn = os.path.join("web3_base", "abis", "tranqONE.json")

abi = get_abi(fn)

w3 = Web3(Web3.WebsocketProvider(wss_url))
tx = Web3Base(w3, envs.p_key, abi=abi)
tx.check_details()

c = tx.w3.eth.contract(address=contract, abi=abi)

amount = tx.w3.toWei("1000", "ether")
print(amount)
gas_price = w3.toWei("50", "gwei")
print(gas_price)

# tqOne
balanceOf = c.functions.balanceOf(tx.account).call()
print(f"balanceOf        ::  {balanceOf}")

rate = int(c.functions.exchangeRateStored().call() / 10 ** 16)
# print(f'rate             ::  {rate}')

balanceOne = int(balanceOf * rate / 100)
print(f"\nbalanceOne       ::  {balanceOne}")

borrowBalance = c.functions.borrowBalanceCurrent(tx.account).call()
print(f"borrowed         ::  {borrowBalance}")

max_wei_to_borrow = balanceOne // 100 * 65
print(f"MAx borrow       ::  {max_wei_to_borrow}")

perc_borrowed = borrowBalance / max_wei_to_borrow * 100
print(f"% borrowed       ::  {round(perc_borrowed, 2)}%")

perc_left = 100 - perc_borrowed
print(f"% Left           ::  {round(perc_left, 2)}%")

can_borrow = max_wei_to_borrow - borrowBalance
print(f"Left to Borrow   ::  {can_borrow}")

can_borrow_readable = round(can_borrow / 10 ** 18, 2)
print(f"one to  Borrow   ::  {can_borrow_readable}")

readableOne = round(balanceOne / 10 ** 18, 2)
print(f"\nreadableOne      ::  {readableOne}")

readableBorrowed = round(borrowBalance / 10 ** 18, 2)
print(f"readableBorrowed ::  {readableBorrowed}")

# TqOne
withdraw = int(amount / rate) * 100
print(f"\nto withdraw      ::  {withdraw}\n")

# readableWithdraw = round(withdraw / 10 ** 18, 2)
print(f"\nreadableWithdraw ::  {readable_price(withdraw)}\n")

# while amount > 0:
#     try:
#         # borrow
#         signed_txn = tx.tx_function(c.functions.borrow, gas_price, func_args=(amount,))
#         tx.process_tx(signed_txn)

#         time.sleep(1)

#         # deposit
#         signed_txn = tx.tx_function(c.functions.mint, gas_price, value=amount)
#         tx.process_tx(signed_txn)
#         amount = tx.w3.toWei('5000', "ether")
#     except:
#         amount -= 1000
#     time.sleep(1)

#
# # repay
# signed_txn = tx.tx_function(c.functions.repayBorrow, gas_price, value=amount)
# tx.process_tx(signed_txn)

# time.sleep(1)

# time.sleep(1)
# # deposit
# # signed_txn = tx.tx_function(c.functions.mint, gas_price, value=amount)
# # tx.process_tx(signed_txn)

# # withdraw
# signed_txn = tx.tx_function(c.functions.redeem , gas_price, func_args=(withdraw,))
# tx.process_tx(signed_txn)

# # time.sleep(1)
