from lend_borrow import *

# TODO: work out the calculation to consider multiple assets - get_rate()
# With multiple assets, you will need to adjust this to match the % on the app..
# With a single asses as collatoral, you can simply use the % for that collateral.
MAX_BORROW_PERCENT = 80.37  # ONE & USDC..
GWEI = 50

contracts = dict(
    tqONE="0x34B9aa82D89AE04f0f546Ca5eC9C93eFE1288940",
    tq1WBTC="0xd9c0D8Ad06ABE10aB29655ff98DcAAA0E059184A",
    tq1ETH="0xc63AB8c72e636C9961c5e9288b697eC5F0B8E1F7",
    tq1USDC="0xCa3e902eFdb2a410C952Fd3e4ac38d7DBDCB8E96",
    tq1USDT="0x7af2430eFa179dB0e76257E5208bCAf2407B2468",
)

if __name__ == "__main__":
    contract = contracts["tqONE"]
    fn = os.path.join("web3_base", "abis", "tranqONE.json")
    abi = get_abi(fn)
    w3 = Web3(Web3.WebsocketProvider(wss_url))
    tx = LendBorrow(contract, GWEI, MAX_BORROW_PERCENT, w3, envs.p_key, abi=abi)

    tx.check_details()
    amount = tx.w3.toWei(0.1, "ether")
    print(amount)
    rate = tx.get_rate()
    print(rate)

    tx.deposited_token()
    tx.percentage_left()
    tx.left_to_borrow()
    # r, s = tx.wait_for_receipt('')
    # tx.check_tx_hash(s, '')

    # print(tx.gas_price)
    # tx.withdraw(amount)
    # time.sleep(1)

    # tx.repay(amount)
    # tx.borrow(amount)
    # tx.deposit(
    #     amount,
    #     **dict(
    #         # display_receipt=True,
    #         display_tx_hash=True
    #     )
    # # )

    tx.repay_borrow_from_deposit(
        amount_less_than_max=100,
        repay_buffer=2.5,
        buffer_amount=100,
        stop_at_amount=1000,
        stop_at_perc=85,
        # test_run=True,
    )

    # tx.fill_borrow_from_deposit(
    #     percent=5,
    #     buffer=10,
    #     GAS_AMOUNT=0.01,
    #     test_run=True
    # )

953554858409426978998
92823763678341205555018

a = 2000000000000000000
b = 2992825550000000000

print(b <= a)
