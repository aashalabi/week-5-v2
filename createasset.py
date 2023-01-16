from algosdk.v2client import algod
from algosdk.future.transaction import AssetConfigTxn, AssetTransferTxn, AssetFreezeTxn, wait_for_confirmation
from algosdk.mnemonic import to_private_key
from algosdk import account, mnemonic
import json
from algosdk.future import transaction

#https://github.com/algorand/docs/blob/master/examples/assets/v2/python/asset_example.py
algod_address = "https://testnet-api.algonode.cloud"
algod_client = algod.AlgodClient("", algod_address)

asset_creator_address = "MUNMWCHJSTPQNB4O74ML6EHXJBBZTFAMSRSUHVYOQFBXZL2AHA7KCKJPCI"
passphrase = "spell summer teach tilt ridge rely imitate before science enlist wear ivory rigid angle drop bicycle movie credit ridge obvious cherry hospital cat ability salt"
#passphrase = passphrase.replace(' ', ',')
print(passphrase)
private_key = to_private_key(passphrase)
asset_id = None #assigned later

algod_address2 = "RS4BOHULH5ZSZTZK6SJY5BVSXDHRKLXB7BNAEFO7AERGV2EHOICAQEGUIE"
passphrase2 = ""
#private_key2 = to_private_key(passphrase2)

def generate_algorand_keypair():
    private_key, address = account.generate_account()
    print("My address: {}".format(address))
    print("My private key: {}".format(private_key))
    phrase = mnemonic.from_private_key(private_key)
    print("My passphrase: {}".format(mnemonic.from_private_key(private_key)))

    return address, private_key, phrase


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
        f = open('asset.index', 'w+')
        f.write(f'{confirmed_txn["asset-index"]}')
        f.close()
    except Exception as e:
        print(e)
#   Utility function used to print asset holding for account and assetid
def print_asset_holding(algodclient, account, assetid):
    # note: if you have an indexer instance available it is easier to just use this
    # response = myindexer.accounts(asset_id = assetid)
    # then loop thru the accounts returned and match the account you are looking for
    account_info = algodclient.account_info(account)
    idx = 0
    for my_account_info in account_info['assets']:
        scrutinized_asset = account_info['assets'][idx]
        idx = idx + 1        
        if (scrutinized_asset['asset-id'] == assetid):
            print("Asset ID: {}".format(scrutinized_asset['asset-id']))
            print(json.dumps(scrutinized_asset, indent=4))
            break
def change_manager(sender, new_manager):
    params = algod_client.suggested_params()
    # comment these two lines if you want to use suggested params
    # params.fee = 1000
    # params.flat_fee = True
    txn = AssetConfigTxn(
        sender=sender['address'],
        sp=params,
        index=asset_id, 
        manager=new_manager,
        reserve=sender['address'],
        freeze=sender['address'],
        clawback=sender['address'])
    # sign by the current manager - Account 2
    stxn = txn.sign(sender['p_key'])
    # txid = algod_client.send_transaction(stxn)
    # print(txid)
    # Wait for the transaction to be confirmed
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
    # Check asset info to view change in management. manager should now be account 1
    #print_created_asset(algod_client, accounts[1]['pk'], asset_id)
def optin(sender, recv_account, asset_id ):
    params = algod_client.suggested_params()
    account_info = algod_client.account_info(recv_account)
    holding = None
    idx = 0
    for my_account_info in account_info['assets']:
        scrutinized_asset = account_info['assets'][idx]
        idx = idx + 1    
        if (scrutinized_asset['asset-id'] == asset_id):
            holding = True
            break
    if not holding:
        # Use the AssetTransferTxn class to transfer assets and opt-in
        print("Receiver is not optin ")
        txn = AssetTransferTxn(
            sender=sender['address'],
            sp=params,
            receiver=recv_account,
            amt=0,
            index=asset_id)
        stxn = txn.sign(sender['p_key'])
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
        # Now check the asset holding for that account.
        # This should now show a holding with a balance of 0.
        print_asset_holding(algod_client, recv_account, asset_id)    

def transfer_assets(sender, recv_account, asset_id, amount):
    # transfer asset of 10 from account 1 to account 3
    params = algod_client.suggested_params()
    # comment these two lines if you want to use suggested params
    # params.fee = 1000
    # params.flat_fee = True
    txn = AssetTransferTxn(
        sender=sender['address'],
        sp=params,
        receiver=recv_account,
        amt=10,
        index=asset_id)
    stxn = txn.sign(sender['p_key'])
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
    # The balance should now be 10.
    print_asset_holding(algod_client, sender['address'], asset_id)

def freeze_asset(freeze_account, asset_id):
    # FREEZE ASSET
    params = algod_client.suggested_params()
    # comment these two lines if you want to use suggested params
    # params.fee = 1000
    # params.flat_fee = True
    # The freeze address was the same as sebder
    txn = AssetFreezeTxn(
        sender=freeze_account['address'],
        sp=params,
        index=asset_id,
        target=freeze_account['address'],  #in our case send and freezer account are the same
        new_freeze_state=True)
    stxn = txn.sign(freeze_account['p_key'])
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
    # The balance should now be 10 with frozen set to true.
    print_asset_holding(algod_client, freeze_account['address'], asset_id)

def destroy_asset(manager, creator, asset_id):

    # 
    # the manager (Account 2) destroys the asset.
    params = algod_client.suggested_params()
    # comment these two lines if you want to use suggested params
    # params.fee = 1000
    # params.flat_fee = True

    # Asset destroy transaction
    txn = AssetConfigTxn(
        sender=manager['address'],
        sp=params,
        index=asset_id,
        strict_empty_address_check=False
        )

    # Sign with secret key of creator
    stxn = txn.sign(manager['p_key'])
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

    # Asset was deleted.
    try:
        print("Account 2 must do a transaction for an amount of 0, " )
        print("with a close_assets_to to the creator account, to clear it from its accountholdings")
        print("For Account 1, nothing should print after this as the asset is destroyed on the creator account")
    
        print_asset_holding(algod_client, creator, asset_id)
        # asset_info = algod_client.asset_info(asset_id)
    except Exception as e:
        print(e)
#asset_creator_address, private_key, phrase = generate_algorand_keypair()
create_asset(asset_creator_address, private_key)
#change_manager({'address':asset_creator_address, 'p_key': private_key }, algod_address2)
#opt in address 2 for asset GOLDPLAT
#optin({'address':asset_creator_address, 'p_key': private_key }, algod_address2, asset_id )
#please note sucess of the transfer depends on manually approving the optin from wallet
#transfer_assets({'address':asset_creator_address, 'p_key': private_key }, algod_address2, asset_id, 10 )
#freeze_asset({'address':asset_creator_address, 'p_key': private_key }, asset_id )
#destroy_asset({'address':algod_address2, 'p_key': private_key2 }, asset_creator_address, asset_id)