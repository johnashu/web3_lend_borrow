from lend_borrow import *

# TODO: work out the calculation to consider multiple assets - get_rate()
# With multiple assets, you will need to adjust this to match the % on the app..
# With a single asses as collatoral, you can simply use the % for that collateral.
MAX_BORROW_PERCENT = 65  # ONE only
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

    # tx.deposited_token()
    # tx.percentage_left()
    # tx.left_to_borrow()
    # print(tx.gas_price)

    # r, s = tx.wait_for_receipt('0x84b695d4e34ebbb4218d39c6890c2a3cf770435f7cc27dd8d42638353bf69906')
    # tx.check_tx_hash(s, '0x84b695d4e34ebbb4218d39c6890c2a3cf770435f7cc27dd8d42638353bf69906')

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
        stop_at_amount=100000,
        stop_at_perc=0,
        # test_run=True,
    )

    # tx.fill_borrow_from_deposit(
    #     percent=3,
    #     buffer=10,
    #     GAS_AMOUNT=0.02,
    #     # test_run=True
    # )
