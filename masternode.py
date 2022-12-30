#!/usr/bin/env python3
##
##
import json
import sys
import subprocess
import requests
import os
import telegram
import platform
from time import sleep
from random import randint

from dotenv import dotenv_values
dot = dotenv_values()

from blockhash import get_block_count, get_block_hash, fetch_block_hash

#from emoji import emojize
import logging
FORMAT = "%(asctime)s - %(name)s - %(levelname)s: %(message)s"
logr = logging.getLogger('masternode')


#########################################################################
def send_alert(message: str) -> None:
    ## just sends the message over telegram
    bot = telegram.Bot(token=dot.get('TOKEN'))
    bot.sendMessage(chat_id=dot.get('_CHID'), text=message)
    return None


#########################################################################
def start_mnode(masternode: str) -> None:
    ## starts the masternode
    debug = walletrpc(method="startmasternode", params=["alias", "0", masternode])
    logr.debug(f"Response: {json.dumps(debug, indent=4)}")
    return None


#########################################################################
def walletrpc(method: str, params: list = None) -> dict:

    ### VARIABLES
    _RPCURL = "http://127.0.0.1:" +str(RPCPORT)
    HEADERS = {'content-type': "application/json", 'cache-control': "no-cache"}
    PAYLOAD = json.dumps({"method": method, "params": params})
    ### DO-NOT-MODIFY HERE

    try:
        r = requests.post( _RPCURL, headers=HEADERS, data=PAYLOAD, auth=(RPCUSER, RPCPASS) )
        return r.json()
    except:
        return None


#########################################################################
def is_blockchain_synced(height: int) -> bool:
    BLKHASH = get_block_hash(height)
    EXPHASH = fetch_block_hash(height)
    return BLKHASH == EXPHASH



#########################################################################
def main() -> None:
    js = walletrpc(method="listmasternodeconf")
    logr.debug(f"MASTERNODE: {json.dumps(js, indent=4)}")

    blk = walletrpc(method="getblockcount")
    logr.debug(f"BLOCK: {json.dumps(blk, indent=4)}")
    
    if abs( (blk.get('result') % 100_000) - 100_000 ) < 299:
        BLKMESSAGE = f"⚠️ WARNING! Blockchain height @{blk} -- about to change collateral."
        send_alert(BLKMESSAGE)


    #ss = walletrpc(method="getstakingstatus")
    #logr.debug(f"BLOCK: {json.dumps(ss, indent=4)}")


    for MN in js.get("result"):

        MESSAGE = f"⚠️ WARNING! {dot.get('_TICK')} {MN.get('alias')} is {MN.get('status')}."

        if MN['status'] in ('ENABLED', 'ACTIVE', 'PRE_ENABLED'): pass

        elif MN['status'] in ('EXPIRED', 'MISSING'):
            HEIGHT = get_block_count() - randint(5,22)
            ## MAKE SURE WE'RE SYNC'D
            if not is_blockchain_synced(HEIGHT):
                WMESSAGE = f"⚠️ WARNING! Masternodes are not in-sync."
                send_alert(WMESSAGE)
                raise SystemExit
            start_mnode(MN['alias'])
            if "onion" in MN['address']: start_mnode(MN['alias'])
            send_alert(MESSAGE)

        else:
            logr.debug(f"⚠️ WARNING! {dot.get('_TICK')} Masternode {MN.get('alias')} is {MN.get('status')}.")
            MESSAGE = f"⚠️ WARNING! {dot.get('_TICK')} Masternode {MN.get('alias')} is {MN.get('status')}."
            send_alert(MESSAGE)


#########################################################################
if __name__ == "__main__":

    _ADDR=dot.get('_ADDR')
    _PORT=dot.get('_PORT')
    _USER=dot.get('_USER')
    _PASS=dot.get('_PASS')

    ERRMESSAGE=""
    APISRCH=dot.get('APISRCH')

    ## DO NOT CHANGE
    HEADERS = { "Content-type": "application/json" }
    _THAT="http://" +_ADDR +":" +_PORT

    _HOST=platform.node()

#########################################################################
    import logging
    from getopt import getopt
    FORMAT = "%(asctime)s - %(name)s - %(levelname)s: %(message)s"
    logr = logging.getLogger('blockhash')

    ## getopt
    try:
        opts, args = getopt( sys.argv[1:], "vd", ["verbose", "debug"] )
    except BaseException as EX:
        logr.info(f"¡¡Exception!! {EX}")
        raise SystemExit

    ## VARS??
    debug = False
    for opt, arg in opts:
        if opt in ('-d', '-v', '--debug', '--verbose'):
            debug = True

    if debug:
        logging.basicConfig(level=logging.DEBUG, format=FORMAT)
    else:
        logging.basicConfig(level=logging.INFO)
        ## limit "Traceback" outputs
        sys.tracebacklimit=0

#########################################################################
    main()
