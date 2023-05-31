![](./imgs/zkSync-logo.png)

# zksync-auto

Python script to send ETH transactions and mint NFTs in Zksync Era network every X days. 
Keeps your accounts active on a regular basis.

NOTE: If you don't want to having problems with claim for a possible Zksync airdrop, this auto script is for you. Do not forget to star and fork from the top right. If you have questions: [Chat](https://t.me/bxdoan)

## Features
- Send ETH transactions from Ethereum mainnet to Zksync Era network every X days.
- Mint NFTs in Zksync Era network every X days.

## System Requirements:

### Python packages
```shell
pip install -r requirements.txt
```
or using pyenv and pipenv
```shell
pipenv install
```

### Configurations
Set update some config file in `config.json` file.
```shell
cp .env-example .env
cp config.example.json config.json
cp account.example.csv account.csv
```

You can create url `network` for `eth` and `zksync` from Alchemy by yourself and update it into `config.json`.
read [alchemy](./alchemy.md)

## Usage
run with python
```sh
python zksync_auto/app.py
```

or run with pipenv setup
```sh
./run.sh
```

then you will see something like this or log file in `tmp` folder:

## Contact

[![Telegram](https://img.shields.io/badge/Telegram-2CA5E0?style=for-the-badge&logo=telegram&logoColor=white)](https://t.me/bxdoan)
[![Twitter](https://img.shields.io/badge/Twitter-1DA1F2?style=for-the-badge&logo=twitter&logoColor=white)](https://twitter.com/bxdoan)
[![Email](https://img.shields.io/badge/Gmail-D14836?style=for-the-badge&logo=gmail&logoColor=white)](mailto:hi@bxdoan.com)

## Thanks for use
Buy me a coffee

[![buymecoffee](https://img.shields.io/badge/Buy_Me_A_Coffee-FFDD00?style=for-the-badge&logo=buy-me-a-coffee&logoColor=black)](https://www.buymeacoffee.com/bxdoan)
[![bxdoan.eth](https://img.shields.io/badge/Ethereum-3C3C3D?style=for-the-badge&logo=Ethereum&logoColor=white)](https://etherscan.io/address/0x610322AeF748238C52E920a15Dd9A8845C9c0318)
[![paypal](	https://img.shields.io/badge/PayPal-00457C?style=for-the-badge&logo=paypal&logoColor=white)](https://paypal.me/bxdoan)
