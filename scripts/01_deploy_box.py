from scripts.helpful_scripts import get_account, encode_function_data
from brownie import Box, network, ProxyAdmin, TransparentUpgradeableProxy, Contract


def main():
    account = get_account()
    print("Deploying to {}".format(network.show_active()))
    box = Box.deploy({"from": account})

    proxy_admin = ProxyAdmin.deploy({"from": account})

    # box_encoded_initializer = encode_function_data(box.store, 1)
    box_encoded_initializer = encode_function_data()

    proxy = TransparentUpgradeableProxy.deploy(
        box.address,
        proxy_admin.address,
        box_encoded_initializer,
        {"from": account, "gas_limit": 1000000},
    )
    print(f"Proxy deployed to {proxy}, you can now upgrade to v2!")
    proxy_box = Contract.from_abi("Box", proxy.address, Box.abi)
    proxy_box.store(1, {"from": account})
    print(proxy_box.retrieve())
