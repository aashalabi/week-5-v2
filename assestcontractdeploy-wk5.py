
# used python version Python 3.9.13
from pyteal import *
from algosdk.v2client import algod
from algosdk.future.transaction import AssetConfigTxn, AssetTransferTxn, AssetFreezeTxn, wait_for_confirmation
from algosdk.mnemonic import to_private_key
from algosdk import account, mnemonic
import json
import base64
from algosdk.future import transaction
from assestcontractwk5 import approval_program, clear_state_program


algod_address = "https://testnet-api.algonode.cloud"
algod_client = algod.AlgodClient("", algod_address)

asset_creator_address = "youraddress"
passphrase = "your phrase"
private_key = to_private_key(passphrase)
asset_id = 153070630 #None #assigned later


def intToBytes(i):
    return i.to_bytes(8, "big")

def create_asset(asset_creator, priv_key):
    txn = AssetConfigTxn(
        sender=asset_creator,
        sp=algod_client.suggested_params(),
        total=1000,
        default_frozen=False,
        unit_name="ENB",
        asset_name="ENB",
        manager=asset_creator_address,
        reserve=asset_creator_address,
        freeze=asset_creator_address,
        clawback=asset_creator_address,
        url="", 
        decimals=0)
    # Sign with secret key of creator
    stxn = txn.sign(priv_key)
    # Send the transaction to the network and retrieve the txid.
    try:
        txid = algod_client.send_transaction(stxn)
        print("Signed transaction with txID: {}".format(txid))
        # Wait for the transaction to be confirmed
        confirmed_txn = wait_for_confirmation(algod_client, txid, 4)  
        print("TXID: ", txid)
        print("Result confirmed in round: {}".format(confirmed_txn['confirmed-round']))   
    except Exception as err:
        print(err)
    # Retrieve the asset ID of the newly created asset by first
    # ensuring that the creation transaction was confirmed,
    # then grabbing the asset id from the transaction.
    print("Transaction information: {}".format(
        json.dumps(confirmed_txn, indent=4)))
    # print("Decoded note: {}".format(base64.b64decode(
    #     confirmed_txn["txn"]["txn"]["note"]).decode()))
    try:
        # Pull account info for the creator
        # get asset_id from tx
        # Get the new asset's information from the creator account
        ptx = algod_client.pending_transaction_info(txid)
        asset_id = ptx["asset-index"]
        #print_created_asset(algod_client, accounts[1]['pk'], asset_id)
        #print_asset_holding(algod_client, accounts[1]['pk'], asset_id)
        print("Asset ID: ", asset_id )
            # write the asset index to an environment file
        f = open('assetid.txt', 'w+')
        f.write(f'asset_id = {confirmed_txn["asset-index"]}')
        f.close()
    except Exception as e:
        print(e)

# call application
# create new application
def create_app(
    client,
    private_key,
    approval_program,
    clear_program,
    global_schema,
    local_schema,
    app_args,
):
    # define sender as creator
    sender = account.address_from_private_key(private_key)

    # declare on_complete as NoOp
    on_complete = transaction.OnComplete.NoOpOC.real

    # get node suggested parameters
    params = client.suggested_params()
    # comment out the next two (2) lines to use suggested fees
    params.flat_fee = True
    params.fee = 1000

    # create unsigned transaction
    txn = transaction.ApplicationCreateTxn(
        sender,
        params,
        on_complete,
        approval_program,
        clear_program,
        global_schema,
        local_schema,
        app_args,
    )

    # sign transaction
    signed_txn = txn.sign(private_key)
    tx_id = signed_txn.transaction.get_txid()

    # send transaction
    client.send_transactions([signed_txn])

    # await confirmation
    wait_for_confirmation(client, tx_id)

    # display results
    transaction_response = client.pending_transaction_info(tx_id)
    app_id = transaction_response["application-index"]
    print("Created new app-id:", app_id)

    return app_id
def compile_program(client, source_code):
    compile_response = client.compile(source_code)
    return base64.b64decode(compile_response["result"])


if __name__ == "__main__":
    #create_asset(asset_creator_address, private_key)
    app_args = [
        intToBytes(asset_id), #Itob #intToBytes
    ]
    '''
    # get PyTeal approval program
    approval_program_ast = approval_program()
    # compile program to TEAL assembly
    approval_program_teal = compileTeal(
        approval_program_ast, mode=Mode.Application, version=6
    )
    # compile program to binary
    approval_program_compiled = compile_program(algod_client, approval_program_teal)

    # get PyTeal clear state program
    clear_state_program_ast = clear_state_program()
    # compile program to TEAL assembly
    clear_state_program_teal = compileTeal(
        clear_state_program_ast, mode=Mode.Application, version=6
    )
    # compile program to binary
    clear_state_program_compiled = compile_program(
        algod_client, clear_state_program_teal
    )
    '''
     # declare application state storage (immutable)
    local_ints = 0
    local_bytes = 1
    global_ints = (
        24  # 4 for setup + 20 for choices. Use a larger number for more choices.
    )
    global_bytes = 1
    global_schema = transaction.StateSchema(global_ints, global_bytes)
    local_schema = transaction.StateSchema(local_ints, local_bytes)
    #call_app(algod_client, private_key, index, app_args)
    app_id = create_app(
        algod_client,
        private_key,
        approval_program_compiled,
        clear_state_program_compiled,
        global_schema,
        local_schema,
        app_args,
    )
    print (f'App create id: {app_id}')

