
# used python version Python 3.9.13
from pyteal import *
from algosdk.v2client import algod
from algosdk.future.transaction import AssetConfigTxn, AssetTransferTxn, AssetFreezeTxn, wait_for_confirmation
from algosdk.mnemonic import to_private_key
from algosdk import account, mnemonic
import json
import base64
from algosdk.future import transaction


#contract global var 
assetid = "AssetId"
creator = "Creator"

def approval_program():
    on_creation = Seq(
        [
            #write the creator address into global var
            App.globalPut(Bytes("Creator"), Txn.sender()),
            #write asset id into global variable
            App.globalPut(Bytes("AssetId"), Btoi(Txn.application_args[0])),
            Return(Int(1))
        ]
    )

    program = Cond(
        [Txn.application_id() == Int(0), on_creation],
        [Txn.on_completion() == OnComplete.OptIn, Return(Int(0))],
        [Txn.on_completion() == OnComplete.CloseOut, Return(Int(0))],
        [Txn.on_completion() == OnComplete.UpdateApplication, Return(Int(0))],
        [Txn.on_completion() == OnComplete.DeleteApplication, Return(Int(0))],
        [Txn.on_completion() == OnComplete.NoOp, Return(Int(0))]
    )


    return program


def clear_state_program():
    program = Seq(
        [
            Return(Int(1))
        ]
    )

    return program


if __name__ == "__main__":
    
    with open("asset_approve_state.teal", "w") as f:
        compiled = compileTeal(approval_program(), Mode.Application, version=6)
        f.write(compiled)

    with open("asset_clear_state.teal", "w") as f:
        compiled = compileTeal(clear_state_program(), Mode.Application, version=6)
        f.write(compiled)