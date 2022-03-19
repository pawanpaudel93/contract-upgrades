from scripts.helpful_scripts import get_account, encode_function_data, upgrade
from brownie import (
    Box,
    BoxV2,
    ProxyAdmin,
    TransparentUpgradeableProxy,
    Contract,
    exceptions,
)
import pytest


def test_proxy_upgrades():
    account = get_account()
    box = Box.deploy({"from": account})
    proxy_admin = ProxyAdmin.deploy({"from": account})

    box_encoded_initializer = encode_function_data()
    proxy = TransparentUpgradeableProxy.deploy(
        box.address,
        proxy_admin.address,
        box_encoded_initializer,
        {"from": account, "gas_limit": 1000000},
    )
    # deploy boxV2
    box_v2 = BoxV2.deploy({"from": account})
    proxy_box = Contract.from_abi("BoxV2", proxy.address, BoxV2.abi)
    with pytest.raises(exceptions.VirtualMachineError):
        proxy_box.increment({"from": account})

    upgrade_tx = upgrade(account, proxy, box_v2.address, proxy_admin)
    upgrade_tx.wait(1)
    assert proxy_box.retrieve() == 0
    proxy_box.increment({"from": account})
    assert proxy_box.retrieve() == 1
    assert (
        box.retrieve() != 1
    )  # this fails because the logic/implementation part doesnot contain state
    assert (
        box_v2.retrieve() != 1
    )  # this fails because the logic/implementation part doesnot contain state
