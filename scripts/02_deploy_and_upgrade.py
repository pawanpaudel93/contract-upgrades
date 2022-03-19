from scripts.helpful_scripts import (
    get_account,
    encode_function_data,
    upgrade,
    LOCAL_BLOCKCHAIN_ENVIRONMENTS,
)
from brownie import (
    Box,
    accounts,
    network,
    BoxV2,
    ProxyAdmin,
    TransparentUpgradeableProxy,
    Contract,
)

publish_source = (
    True if network.show_active() not in LOCAL_BLOCKCHAIN_ENVIRONMENTS else False
)


def main():
    account = get_account()
    print("Deploying to {}".format(network.show_active()))
    box = Box.deploy({"from": account}, publish_source=publish_source)

    proxy_admin = ProxyAdmin.deploy({"from": account}, publish_source=publish_source)

    # box_encoded_initializer = encode_function_data(box.store, 1)
    box_encoded_initializer = encode_function_data()

    proxy = TransparentUpgradeableProxy.deploy(
        box.address,
        proxy_admin.address,
        box_encoded_initializer,
        {"from": account, "gas_limit": 1000000},
        publish_source=publish_source,
    )
    print(f"Proxy deployed to {proxy}, you can now upgrade to v2!")
    proxy_box = Contract.from_abi("Box", proxy.address, Box.abi)
    proxy_box.store(1, {"from": account})

    # upgrade
    box_v2 = BoxV2.deploy({"from": account}, publish_source=publish_source)
    upgrade_tx = upgrade(account, proxy, box_v2.address, proxy_admin)
    upgrade_tx.wait(1)
    print(f"Proxy has been upgraded")
    proxy_box = Contract.from_abi("BoxV2", proxy.address, BoxV2.abi)
    proxy_box.increment({"from": account})
    print(proxy_box.retrieve())
