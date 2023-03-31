from uniswap import Uniswap

from zksync_auto.account import AccountLoader
from zksync_auto.config import config


class UniProcessor(object):

    def __init__(self, **kwargs):
        self.network = config.network

        self.list_acc = AccountLoader().parser_file()

    def swap(self):
        # Some token addresses we'll be using later in this guide
        eth     = "0x0000000000000000000000000000000000000000"
        bat     = "0x0D8775F648430679A709E98d2b0Cb6250d2887EF"
        dai     = "0x6B175474E89094C44Da98b954EedeAC495271d0F"
        dai_new = "0x11fE4B6AE13d2a6055C8D9cF65c55bac32B5d844"
        acc = self.list_acc[0]
        print(f"Account: {acc['address']}")
        us = Uniswap(
            address=acc['address'],
            private_key=acc['private_key'],
            version=3,
            provider=self.network.eth
        )

        # Returns the amount of DAI you get for 1 ETH (10^18 wei)
        pr = us.get_price_input(dai_new, eth, 300 *  10 ** 18)
        pr = pr / 10 ** 18
        print(f"Price: {pr}")
        amount = Web3.toWei(0.1, 'gwei')
        result = us.make_trade_output(
            input_token=dai_new,
            output_token=eth,
            qty=30 * 10**18,
            fee=500
        )
        print(f"Swap result: {result}")


def process():
    inch = InchProcessor()
    inch.swap()


if __name__ == "__main__":
    process()