from zksync_auto.oneinch import OneInchSwap, TransactionHelper, OneInchOracle

from zksync_auto.account import AccountLoader
from zksync_auto.config import config


class InchProcessor(object):

    def __init__(self, **kwargs):
        self.network = config.network

        self.list_acc = AccountLoader().parser_file()

    def swap(self):

        rpc_url = self.network.goerli
        # binance_rpc = "adifferentRPCurl.com"
        first_account = self.list_acc[0]
        public_key = first_account['address']
        private_key = first_account['private_key']

        exchange = OneInchSwap(public_key)
        bsc_exchange = OneInchSwap(public_key, chain='binance')
        helper = TransactionHelper(rpc_url, public_key, private_key)
        # bsc_helper = TransactionHelper(binance_rpc, public_key, private_key, chain='binance')
        oracle = OneInchOracle(rpc_url, chain='goerli')

        # See chains currently supported by the helper method:
        helper.chains
        # {"ethereum": "1", "binance": "56", "polygon": "137", "avalanche": "43114"}
        # Straight to business:
        # Get a swap and do the swap
        result = exchange.get_swap(
            from_token_symbol="ETH",
            to_token_symbol="USDT",
            amount=1,
            slippage=0.5
        )  # get the swap transaction
        result = helper.build_tx(result)  # prepare the transaction for signing, gas price defaults to fast.
        result = helper.sign_tx(result)  # sign the transaction using your private key
        result = helper.broadcast_tx(result)  # broadcast the transaction to the network and wait for the receipt.

        # USDT to ETH price on the Oracle. Note that you need to indicate the token decimal if it is anything other than 18.
        oracle.get_rate_to_ETH("0xa0b86991c6218b36c1d19d4a2e9eb0ce3606eb48", src_token_decimal=6)

        # Get the rate between any two tokens.
        oracle.get_rate(src_token="0x6B175474E89094C44Da98b954EedeAC495271d0F",
                        dst_token="0x111111111117dC0aa78b770fA6A738034120C302")

        exchange.health_check()


def process():
    inch = InchProcessor()
    inch.swap()


if __name__ == "__main__":
    process()