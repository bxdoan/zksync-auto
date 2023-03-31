import json
import requests
from web3 import Web3
from decimal import *
from web3.middleware import geth_poa_middleware

from zksync_auto import utils
from zksync_auto.constants import CHAINS, ONEINCH_BASE_URL, CONTRACTS, GAS_ORACLE


class UnknownToken(Exception):
    pass


class OneInchSwap(object):

    def __init__(self, address, chain='ethereum', version='v5.0'):
        self.presets = None
        self.tokens = {}
        self.tokens_by_address = {}
        self.protocols = []
        self.address = address
        self.version = version
        self.chain_id = CHAINS[chain]
        self.chain = chain
        self.tokens = self.get_tokens()
        self.spender = self.get_spender()

        self.base_ver_chain = f'{ONEINCH_BASE_URL}/{self.version}/{self.chain_id}'

    @staticmethod
    def _get(url, params=None, headers=None):
        """ Implements a get request """
        try:
            response = requests.get(url, params=params, headers=headers)
            response.raise_for_status()
            payload = response.json()
        except requests.exceptions.ConnectionError as e:
            print(f"ConnectionError when doing a GET request {url=} and {params=} and {e=}")
            payload = None
        except requests.exceptions.HTTPError as e:
            err = utils.parse_error_response(e)
            print(f"HTTPError {url=} and {params=} and {err=}")
            payload = None
        return payload

    def _token_to_address(self, token: str):
        if len(token) == 42:
            address = self.w3.to_checksum_address(token)
            return address
        else:
            try:
                address = self.tokens[token]['address']
            except:
                raise UnknownToken("Token not in 1inch Token List")
            return address

    def health_check(self):
        """
        Calls the Health Check Endpoint
        :return: Always returns code 200 if API is stable
        """
        url = f'{self.base_ver_chain}/healthcheck'
        response = self._get(url)
        return response['status']

    def get_spender(self):
        url = f'{self.base_ver_chain}/approve/spender'
        result = self._get(url)
        if not result.__contains__('spender'):
            return result
        self.spender = result
        return self.spender

    def get_tokens(self):
        """
        Calls the Tokens API endpoint
        :return: A dictionary of all the whitelisted tokens.
        """
        url = f'{self.base_ver_chain}/tokens'
        result = self._get(url)
        if not result.__contains__('tokens'):
            return result
        for key in result['tokens']:
            token = result['tokens'][key]
            self.tokens_by_address[key] = token
            self.tokens[token['symbol']] = token
        return self.tokens

    def get_liquidity_sources(self):
        url = f'{self.base_ver_chain}/liquidity-sources'
        result = self._get(url)
        if not result.__contains__('liquidity-sources'):
            return result
        self.protocols = result
        return self.protocols

    def get_presets(self):
        url = f'{self.base_ver_chain}/presets'
        result = self._get(url)
        if not result.__contains__('presets'):
            return result
        self.presets = result
        return self.presets

    def get_quote(self, from_token_symbol: str, to_token_symbol: str, amount: float, decimal=None, **kwargs):
        """
        Calls the QUOTE API endpoint. NOTE: When using custom tokens, the token decimal is assumed to be 18. If your
        custom token has a different decimal - please manually pass it to the function (decimal=x)
        """
        from_address = self._token_to_address(from_token_symbol)
        to_address = self._token_to_address(to_token_symbol)
        if decimal is None:
            try:
                self.tokens[from_token_symbol]['decimals']
            except KeyError:
                decimal = 18
            else:
                decimal = self.tokens[from_token_symbol]['decimals']
        else:
            pass
        if decimal == 0:
            amount_in_wei = int(amount)
        else:
            amount_in_wei = int(amount * 10 ** decimal)
        url = f'{self.base_ver_chain}/quote'
        params = {
            'fromTokenAddress': from_address,
            'toTokenAddress': to_address,
            'amount': amount_in_wei
        }
        result = self._get(url, params=params)

        from_base = Decimal(result['fromTokenAmount']) / Decimal(10 ** result['fromToken']['decimals'])
        to_base = Decimal(result['toTokenAmount']) / Decimal(10 ** result['toToken']['decimals'])
        if from_base > to_base:
            rate = from_base / to_base
        else:
            rate = to_base / from_base
        return result, rate

    def get_swap(self, from_token_symbol: str, to_token_symbol: str,
                 amount: float, slippage: float, decimal=None, send_address=None, **kwargs):
        """
        Calls the SWAP API endpoint. NOTE: When using custom tokens, the token decimal is assumed to be 18. If your
        custom token has a different decimal - please manually pass it to the function (decimal=x)
        """
        if send_address is None:
            send_address = self.address
        else:
            pass
        from_address = self._token_to_address(from_token_symbol)
        to_address = self._token_to_address(to_token_symbol)
        if decimal is None:
            try:
                self.tokens[from_token_symbol]['decimals']
            except KeyError:
                decimal = 18
            else:
                decimal = self.tokens[from_token_symbol]['decimals']
        else:
            pass
        if decimal == 0:
            amount_in_wei = int(amount)
        else:
            amount_in_wei = int(amount * 10 ** decimal)
        url = f'{self.base_ver_chain}/swap'
        params = {
            'fromTokenAddress': from_address,
            'toTokenAddress': to_address,
            'amount': amount_in_wei,
            'fromAddress': send_address,
            'slippage': slippage
        }
        result = self._get(url, params=params)
        return result

    def get_allowance(self, from_token_symbol: str, send_address=None):
        if send_address is None:
            send_address = self.address
        from_address = self._token_to_address(from_token_symbol)
        url = f'{self.base_ver_chain}/approve/allowance'
        params = {
            'tokenAddress': from_address,
            'walletAddress': send_address
        }
        result = self._get(url, params=params)
        return result

    def get_approve(self, from_token_symbol: str, amount=None, decimal=None):
        from_address = self._token_to_address(from_token_symbol)
        if decimal is None:
            try:
                self.tokens[from_token_symbol]['decimals']
            except KeyError:
                decimal = 18
            else:
                decimal = self.tokens[from_token_symbol]['decimals']
        else:
            pass
        url = f'{self.base_ver_chain}/approve/transaction'
        params = {
            'tokenAddress': from_address
        }
        if amount:
            if decimal == 0:
                amount_in_wei = int(amount)
            else:
                amount_in_wei = int(amount * 10 ** decimal)

            params['amount'] = amount_in_wei

        result = self._get(url, params=params)
        return result


class TransactionHelper(object):

    @staticmethod
    def _get(url, params=None, headers=None):
        """ Implements a get request """
        try:
            response = requests.get(url, params=params, headers=headers)
            response.raise_for_status()
            payload = response.json()
        except requests.exceptions.ConnectionError as e:
            print("ConnectionError when doing a GET request from {}".format(url))
            payload = None
        except requests.exceptions.HTTPError:
            print("HTTPError {}".format(url))
            payload = None
        return payload

    def __init__(self, rpc_url, public_key, private_key, chain='ethereum', broadcast_1inch=False):
        self.w3 = Web3(Web3.HTTPProvider(rpc_url))
        self.abi = utils.load_abi('erc20.json')
        self.abi_aggregator = utils.load_abi('aggregatorv5.json')

        if chain == 'polygon' or chain == 'avalanche':
            self.w3.middleware_onion.inject(geth_poa_middleware, layer=0)
        else:
            pass
        self.public_key = public_key
        self.private_key = private_key
        self.chain = chain
        self.chain_id = CHAINS[chain]
        self.broadcast_1inch = broadcast_1inch

    def build_tx(self, raw_tx, speed='high'):
        nonce = self.w3.eth.get_transaction_count(self.public_key)
        if 'tx' in raw_tx:
            tx = raw_tx['tx']
        else:
            tx = raw_tx
        if 'from' not in tx:
            tx['from'] = self.w3.to_checksum_address(self.public_key)
        tx['to'] = self.w3.to_checksum_address(tx['to'])
        if 'gas' not in tx:
            tx['gas'] = self.w3.eth.estimate_gas(tx)
        tx['nonce'] = nonce
        tx['chainId'] = int(self.chain_id)
        tx['value'] = int(tx['value'])
        tx['gas'] = int(tx['gas'] * 1.25)
        if self.chain == 'ethereum' or self.chain == 'polygon' or self.chain == 'avalanche' or\
                self.chain == 'gnosis' or self.chain == 'klaytn':
            gas = self._get(GAS_ORACLE + self.chain_id)
            tx['maxPriorityFeePerGas'] = int(gas[speed]['maxPriorityFeePerGas'])
            tx['maxFeePerGas'] = int(gas[speed]['maxFeePerGas'])
            tx.pop('gasPrice')
        else:
            tx['gasPrice'] = int(tx['gasPrice'])
        return tx

    def sign_tx(self, tx):
        signed_tx = self.w3.eth.account.sign_transaction(tx, self.private_key)
        return signed_tx

    def broadcast_tx(self, signed_tx, timeout=360):
        if self.broadcast_1inch is True:
            tx_json = signed_tx.rawTransaction
            tx_json = {"rawTransaction": tx_json.hex()}
            payload = requests.post('https://tx-gateway.1inch.io/v1.1/' + self.chain_id + '/broadcast', data=self.w3.toJSON(tx_json), headers={"accept": "application/json, text/plain, */*", "content-type": "application/json"})
            tx_hash = json.loads(payload.text)
            tx_hash = tx_hash['transactionHash']
            receipt = self.w3.eth.wait_for_transaction_receipt(tx_hash, timeout=timeout)
            return receipt, tx_hash
        else:
            tx_hash = self.w3.eth.send_raw_transaction(signed_tx.rawTransaction)
            print(tx_hash.hex())
            receipt = self.w3.eth.wait_for_transaction_receipt(tx_hash, timeout=timeout)
            return receipt, tx_hash.hex()

    def get_ERC20_balance(self, contract_address, decimal=None):
        contract = self.w3.eth.contract(address=self.w3.to_checksum_address(contract_address), abi=self.abi)
        balance_in_wei = contract.functions.balanceOf(self.public_key).call()
        if decimal is None:
            return self.w3.from_wei(balance_in_wei, 'ether')
        elif decimal == 0:
            return balance_in_wei
        else:
            return balance_in_wei / 10 ** decimal

    def decode_abi(self, transaction):
        address = self.w3.to_checksum_address('0x1111111254EEB25477B68fb85Ed929f73A960582')
        contract = self.w3.eth.contract(address=address, abi=self.abi_aggregator)
        data = transaction['tx']['data']
        decoded_data = contract.decode_function_input(data)
        return decoded_data


class OneInchOracle(object):

    def __init__(self, rpc_url, chain='ethereum'):
        self.w3 = Web3(Web3.HTTPProvider(rpc_url))
        self.oracle_abi = utils.load_abi('oracle.json')
        self.chain = chain
        self.chain_id = CHAINS[chain]
        self.contract_address = CONTRACTS[chain]
        self.oracle_contract = self.w3.eth.contract(address=self.contract_address, abi=self.oracle_abi)

    def get_rate(self, src_token, dst_token, wrap=False,
                 src_token_decimal: int = 18, dst_token_decimal: int = 18) -> float:
        rate = self.oracle_contract.functions.getRate(self.w3.to_checksum_address(src_token),
                                                      self.w3.to_checksum_address(dst_token), wrap).call()
        if src_token_decimal == 18 and dst_token_decimal < 18:
            rate = rate / 10 ** dst_token_decimal
        elif dst_token_decimal == 18 and src_token_decimal < 18:
            rate = rate / 10 ** ((18 - src_token_decimal) + 18)
        elif dst_token_decimal < 18 and src_token_decimal < 18:
            rate = rate / 10 ** ((18 - src_token_decimal) + (18 - dst_token_decimal))
        else:
            rate = rate / 10 ** 18
        return rate

    def get_rate_to_ETH(self, src_token, wrap=False, src_token_decimal=18) -> float:
        rate = self.oracle_contract.functions.getRateToEth(self.w3.to_checksum_address(src_token), wrap).call()
        if src_token_decimal == 18:
            rate = rate / 10 ** 18
        elif src_token_decimal < 18:
            rate = rate / 10 ** ((18 - src_token_decimal) + 18)
        return rate
