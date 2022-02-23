from lend_borrow import *

MAX_BORROW_PERCENT = 60
GWEI = 2

if __name__ == "__main__":
    contracts = dict(
        MOVR="0x6a1A771C7826596652daDC9145fEAaE62b1cd07f",
    )
    rpc = "https://rpc.moonriver.moonbeam.network"
    chain_id = 1285
    # wss_url = 'wss://moonriver.api.onfinality.io/public-ws'
    # wss_url = 'wss://wss.api.moonriver.moonbeam.network'
    contract = contracts["MOVR"]
    fn = os.path.join("web3_base", "abis", "moonwellMOVR.json")
    abi = get_abi(fn)
    w3 = Web3(Web3.HTTPProvider(rpc))
    tx = LendBorrow(
        contract,
        GWEI,
        MAX_BORROW_PERCENT,
        w3,
        envs.p_key_movr,
        abi=abi,
        chain_id=chain_id,
    )
    tx.check_details()
    amount = tx.w3.toWei(1, "ether")
    print(amount)
    rate = tx.get_rate()
    print(rate)
    # print(tx.gas_price)
    # tx.withdraw(amount)
    # time.sleep(1)
    # tx.repay(amount)
    # tx.borrow(amount)
    # tx.deposit(amount)

    # tx.repay_all_borrow_from_deposit(
    #     amount_less_than_max=1000,
    #     repay_buffer=1,
    #     buffer_amount=100,
    #     stop_at_amount=68000,
    # )
    # tx.fill_borrow_from_deposit(
    #     percent=5,
    #     buffer=1,
    #     GAS_AMOUNT=0.01,
    #     test_run=True
    #     )
