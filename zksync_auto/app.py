from decimal import Decimal
from web3 import Web3
from web3.middleware import geth_poa_middleware
from eth_account import Account
from eth_account.signers.local import LocalAccount
from zksync2.module.module_builder import ZkSyncBuilder
from zksync2.provider.eth_provider import EthereumProvider
from zksync2.core.types import Token, EthBlockParams

from zksync_auto.config import config
from zksync_auto.account import AccountLoader


class ZksyncAuto(object):

    def __init__(self, **kwargs):
        self.network = config.network
        self.acc = config.acc
        self.list_acc = AccountLoader().parser_file()

        self.web3 = ZkSyncBuilder.build(self.network.zksync)
        self.eth_web3 = Web3(Web3.HTTPProvider(self.network.eth))
        self.account: LocalAccount = Account.from_key(self.acc.pri)

    def deposit(self, anount: int or float = None):
        try:
            if not anount:
                return

            gas_price = self.web3.eth.gas_price
            print(f"gas price: {gas_price=}")
            self.eth_web3.middleware_onion.inject(geth_poa_middleware, layer=0)
            eth_provider = EthereumProvider(
                zksync_web3=self.web3,
                eth_web3=self.eth_web3,
                l1_account=self.account
            )
            tx_receipt = eth_provider.deposit(
                token=Token.create_eth(),
                amount=Web3.to_wei(anount, "ether"),
                to=self.account.address,
                gas_price=gas_price,
            )
            print(f"tx status: {tx_receipt['status']}")
        except Exception as _e:
            print(f"Error: {_e}")

    def l1_balance(self, account: LocalAccount = None):
        if not account:
            account = self.account
        eth_balance = self.eth_web3.eth.get_balance(account.address)
        print(f"Eth balance: {Web3.fromWei(eth_balance, 'ether')}")

    def l2_balance(self, account: LocalAccount = None):
        if not account:
            account = self.account
        zk_balance = self.web3.zksync.get_balance(account.address, EthBlockParams.LATEST.value)
        print(f"ZkSync balance: {Web3.fromWei(zk_balance, 'ether')}")

    def l2_balance_all(self):
        for acc in self.list_acc:
            if not acc.get('private_key'):
                continue
            print(f"Account: {acc['address']}")
            account = Account.from_key(acc['private_key'].lower())
            self.l2_balance(account=account)


def process():
    zksync_auto = ZksyncAuto()

    # get zksync balance
    # zksync_auto.l2_balance_all()

    # deposit eth to zksync
    zksync_auto.deposit(anount=0.01)

    # withdraw eth from zksync
    # zksync_auto.withdraw(anount=0.01)


if __name__ == "__main__":
    process()
