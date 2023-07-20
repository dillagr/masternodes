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
import logging
from time import sleep
from random import randint

from dotenv import dotenv_values
dot = dotenv_values()

from blockhash import get_blockhash, fetch_blockhash


#########################################################################
( _ADDR, _PORT, _USER, _PASS ) = ( dot.get('_ADDR'), dot.get('_PORT'), dot.get('_USER'), dot.get('_PASS'))

ERRMESSAGE=""
APISRCH=dot.get('APISRCH')

## DO NOT CHANGE
HEADERS = { "Content-type": "application/json" }
_THAT = f"http://127.0.0.1:{_PORT}"

_HOST=platform.node()

## logging
FORMAT = "%(asctime)s - %(name)s - %(levelname)s: %(message)s"
logr = logging.getLogger('masternode')

IS_SYNCED_WITH_EXPLORER = False   ## assume false
SYNC_TEST_RAN = False   ## change this later
AUTO_RESTART_MASTERNODE = True

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
    _RPCURL = "http://127.0.0.1:" +str(_PORT)
    HEADERS = {'content-type': "application/json;", 'cache-control': "no-cache"}
    PAYLOAD = json.dumps({"method": method, "params": params})
    ### DO-NOT-MODIFY HERE

    try:
        r = requests.post( _RPCURL, headers=HEADERS, data=PAYLOAD, auth=(_USER, _PASS) )
        return r.json()
    except:
        return None


#########################################################################
def is_blockchain_synced(height: int) -> bool:
    global IS_SYNCED_WITH_EXPLORER
    global SYNC_TEST_RAN
    SYNC_TEST_RAN = True
    BLKHASH = get_blockhash(height)
    logr.debug(f"BLKHASH: {BLKHASH}")
    assert BLKHASH, "⚠️ WARNING! Undefined local blockhash."
    EXPHASH = fetch_blockhash(height)
    logr.debug(f"EXPHASH: {EXPHASH}")
    assert BLKHASH, "⚠️ WARNING! Undefined explorer blockhash."
    IS_SYNCED_WITH_EXPLORER = ( BLKHASH == EXPHASH )
    return IS_SYNCED_WITH_EXPLORER



#########################################################################
def main() -> None:
    js = walletrpc(method="listmasternodeconf")
    logr.debug(f"MASTERNODE: {json.dumps(js, indent=4)}")

    HEIGHT = walletrpc(method="getblockcount")
    logr.debug(f"BLOCK: {json.dumps(HEIGHT, indent=4)}")
    
    if abs( (HEIGHT.get('result') % 100_000) - 100_000 ) < 299:
        BLKMESSAGE = f"⚠️ WARNING! Blockchain height @{blk} -- about to change collateral."
        send_alert(BLKMESSAGE)

    #ss = walletrpc(method="getstakingstatus")
    #logr.debug(f"BLOCK: {json.dumps(ss, indent=4)}")


    for MN in js.get("result"):

        MESSAGE = f"⚠️ WARNING! {dot.get('_TICK')} {MN.get('alias')} is {MN.get('status')}."

        if MN['status'] in ('ENABLED', 'ACTIVE', 'PRE_ENABLED'): pass

        elif MN['status'] in ('EXPIRED', 'MISSING'):
            ## FIRST, MAKE SURE WE'RE SYNC'D
            if not IS_SYNCED_WITH_EXPLORER:
                ## DO IT ONCE, AT LEAST
                if not SYNC_TEST_RAN: is_blockchain_synced(HEIGHT.get('result'))
                WMESSAGE = f"⚠️ WARNING! Masternodes are not in-sync."
                if not IS_SYNCED_WITH_EXPLORER: 
                    send_alert(WMESSAGE)
                    raise SystemExit
            if AUTO_RESTART_MASTERNODE:
                start_mnode(MN['alias'])
                if "onion" in MN['address']: start_mnode(MN['alias'])
            send_alert(MESSAGE)

        else:
            logr.debug(f"⚠️ WARNING! {dot.get('_TICK')} Masternode {MN.get('alias')} is {MN.get('status')}.")
            MESSAGE = f"⚠️ WARNING! {dot.get('_TICK')} Masternode {MN.get('alias')} is {MN.get('status')}."
            send_alert(MESSAGE)


#########################################################################
if __name__ == "__main__":

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
