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


class ZksyncAuto(object):

    def __init__(self, **kwargs):
        self.network = config.network
        self.acc = config.acc

        self.web3 = ZkSyncBuilder.build(self.network.zksync)
        self.eth_web3 = Web3(Web3.HTTPProvider(self.network.eth))
        self.account: LocalAccount = Account.from_key(self.acc.pri)

    def deposit(self, anount: int = None):
        try:
            if not anount:
                return

            gas_price = self.web3.eth.gas_price
            print(f"gas price: {gas_price=}")
            self.eth_web3.middleware_onion.inject(geth_poa_middleware, layer=0)
            gas_provider = StaticGasProvider(Web3.toWei(1, "gwei"), gas_price)
            eth_provider = EthereumProvider.build_ethereum_provider(zksync=self.web3,
                                                                    eth=self.eth_web3,
                                                                    account=self.account,
                                                                    gas_provider=gas_provider)
            tx_receipt = eth_provider.deposit(Token.create_eth(),
                                              self.eth_web3.toWei(Decimal(1), "ether"),
                                              self.account.address)
            print(f"tx status: {tx_receipt['status']}")
        except Exception as _e:
            print(f"Error: {_e}")

    def l1_balance(self):
        eth_balance = self.eth_web3.eth.get_balance(self.account.address)
        print(f"Eth: balance: {Web3.fromWei(eth_balance, 'ether')}")

    def l2_balance(self):
        zk_balance = self.web3.zksync.get_balance(self.account.address, EthBlockParams.LATEST.value)
        print(f"ZkSync balance: {zk_balance}")


if __name__ == "__main__":
    zksync_auto = ZksyncAuto()
    # zksync_auto.l1_balance()
    zksync_auto.l2_balance()
    # zksync_auto.deposit(anount=0.1)
