from decimal import Decimal
from web3 import Web3
from web3.middleware import geth_poa_middleware
from eth_account import Account
from eth_account.signers.local import LocalAccount
from zksync2.manage_contracts.gas_provider import StaticGasProvider
from zksync2.module.module_builder import ZkSyncBuilder
from zksync2.core.types import Token
from zksync2.provider.eth_provider import EthereumProvider
from zksync2.signer.eth_signer import PrivateKeyEthSigner
from zksync2.core.types import Token, ZkBlockParams, BridgeAddresses, EthBlockParams

from zksync_auto.config import config
from zksync_auto.account import AccountLoader


class ZksyncAuto(object):

    def __init__(self, **kwargs):
        self.network = config.network
        self.acc = config.acc
        self.list_acc = AccountLoader().parser_file()

        self.zksync_web3 = ZkSyncBuilder.build(self.network.zksync)
        self.eth_web3 = Web3(Web3.HTTPProvider(self.network.eth))
        self.account: LocalAccount = Account.from_key(self.acc.pri)

    def deposit(self, anount: int or float = None):
        try:
            if not anount:
                return

            zk_gas_price = self.zksync_web3.eth.gas_price
            eth_gas_price = self.eth_web3.eth.gas_price
            print(f"{zk_gas_price=} and {eth_gas_price=}")
            self.eth_web3.middleware_onion.inject(geth_poa_middleware, layer=0)
            gas_fee = round(1555000 * 1.3)
            print(f"gas fee: {gas_fee=}")
            gas_provider = StaticGasProvider(Web3.toWei(100, "gwei"), gas_fee)
            eth_provider = EthereumProvider.build_ethereum_provider(
                zksync=self.zksync_web3,
                eth=self.eth_web3,
                account=self.account,
                gas_provider=gas_provider
            )
            tx_receipt = eth_provider.deposit(
                token=Token.create_eth(),
                amount=Web3.toWei(anount, "ether"),
                user_address=self.account.address
            )
            print(f"tx status: {tx_receipt['status']}")
            print(f"tx tx_receipt: {tx_receipt}")

        except Exception as _e:
            print(f"Error: {_e}")

    def l1_balance(self, account: LocalAccount = None):
        if not account:
            account = self.account
        print(f"Account: {account.address}")
        eth_balance = self.eth_web3.eth.get_balance(account.address)
        print(f"Eth balance: {Web3.fromWei(eth_balance, 'ether')}")

    def l2_balance(self, account: LocalAccount = None):
        if not account:
            account = self.account
        zk_balance = self.zksync_web3.zksync.get_balance(account.address, EthBlockParams.LATEST.value)
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
    zksync_auto.l1_balance()
    zksync_auto.l2_balance()

    # deposit eth to zksync
    zksync_auto.deposit(anount=1)

    # transfer eth from zksync to zksync

    # withdraw eth from zksync
    # zksync_auto.withdraw(anount=0.01)


if __name__ == "__main__":
    process()
