from lend_borrow import *
from time import sleep

AMOUNT = 1000
DELAY = 10
token = '0x794a61358D6845594F94dc1DB02A252b5b4814aD' # ONE
to = '0xfAFfb33B924C33381dee35D445013D3200249572' #receiver

MAX_BORROW_PERCENT = 65  # ONE only
GWEI = 50

contracts = dict(
    AAVE="0xe86B52cE2e4068AdE71510352807597408998a69"
)

if __name__ == "__main__":
    contract = contracts["AAVE"]
    fn = os.path.join("web3_base", "abis", "AAVE.json")
    abi = get_abi(fn)
    # w3 = Web3(Web3.WebsocketProvider(wss_url))
    w3 = Web3(Web3.HTTPProvider(main_net))
    tx = LendBorrow(contract, GWEI, MAX_BORROW_PERCENT, w3, envs.p_key, abi=abi)

    tx.check_details()
    amount = tx.w3.toWei(AMOUNT, "ether")
    print(amount)    
         
    while 1:
        try:
            tx.withdraw_AAVE(token, amount, to)
            tx.check_details()
        except:
            pass
        sleep(DELAY)
   