#!/usr/bin/env python3

import json
import requests
import httpx
import telegram
import decimal
import sys
import platform

from random import randint
from dotenv import dotenv_values
dot = dotenv_values()

_ADDR=dot.get('_ADDR')
_PORT=dot.get('_PORT')
_USER=dot.get('_USER')
_PASS=dot.get('_PASS')

ERRMESSAGE=""
APISRCH=dot.get('APISRCH')

## DO NOT CHANGE
HEADERS = { "Content-type": "application/json" }
_THAT = f"http://127.0.0.1:{_PORT}"

_HOST=platform.node()

#########################################################################
def get_block_count() -> dict:
    ## BLKHEIGHT
    jc = walletrpc(method="getblockcount", params=None)
    return jc.get("result")

#########################################################################
def get_block_hash(blockheight) -> dict:
    ## BLKHASH
    jc = walletrpc(method="getblockhash", params=[blockheight])
    return jc.get("result")    

#########################################################################
def fetch_block_hash(height) -> str:
    THISURL=APISRCH +"?query=" +str(height)
    x = requests.get(THISURL)
    if x.status_code == 503: return None
    xj = x.json()
    if len(xj.get("response")) == 0: return None
    return xj["response"].get("hash")

#########################################################################
def fetch_block_height() -> int:
    THISURL="https://explorer.decenomy.net/coreapi/v1/coins/FLS"
    x = requests.get(THISURL)
    if x.status_code == 503: return None
    xj = x.json()
    if len(xj.get("response")) == 0: return None
    return xj["response"].get("bestblockheight")

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
def main() -> None :

    bot = telegram.Bot(token=dot.get('TOKEN'))

    BLKCOUNT = get_block_count()
    assert int(BLKCOUNT) > 0, "!!ERROR [@{_HOST}]!! Could not get block height."
    BLKHEIGHT = int(BLKCOUNT) - randint(5,22)  ## explorer might be delayed
    BLKHASH = get_block_hash(BLKHEIGHT)

    if BLKHEIGHT:
        QHEIGHT=BLKHEIGHT
    else:
        ERRMESSAGE = f"⚠️ WARNING [@{_HOST}]: Block height is non-numeric/invalid."
        bot.sendMessage(chat_id=dot.get('_CHID'), text=ERRMESSAGE)
        sys.exit(99)


    EXPHASH=fetch_block_hash(QHEIGHT)
    EXPHEIGHT=fetch_block_height()
    logr.debug(f"Explorer HASH for Block {QHEIGHT}: {EXPHASH}")
    logr.debug(f"Blockchain HASH for Block {QHEIGHT}: {BLKHASH}")
    logr.debug(f"Explorer height {EXPHEIGHT}")
    logr.debug(f"Blockchain height {BLKCOUNT}")
    
    if not EXPHASH:
        ERRMESSAGE = f"⚠️ WARNING [@{_HOST}]: FLITS explorer has issues!"
        bot.sendMessage(chat_id=dot.get('_CHID'), text=ERRMESSAGE)
        sys.exit(99)



    ## APPLY THE LOGIC
    if EXPHASH != BLKHASH:
        ERRMESSAGE = f"⚠️ WARNING [@{_HOST}]: Local hash not same as Explorer hash (at height: {BLKHEIGHT})."
        bot.sendMessage(chat_id=dot.get('_CHID'), text=ERRMESSAGE)
        sys.exit(99)

    if abs(BLKCOUNT -EXPHEIGHT) > 9:
        ERRMESSAGE = f"⚠️ WARNING [@{_HOST}]: Block height ({BLKHCOUNT}) not same as Explorer (height: {EXPHEIGHT})."
        bot.sendMessage(chat_id=dot.get('_CHID'), text=ERRMESSAGE)
        sys.exit(99)





#########################################################################
if __name__ == "__main__":

    import logging
    from getopt import getopt
    FORMAT = "%(asctime)s - %(name)s - %(levelname)s: %(message)s"
    logr = logging.getLogger('blockhash')

    ## getopt
    try: opts, args = getopt( sys.argv[1:], "vd", ["verbose", "debug"] )
    except BaseException as EX:
        logr.info(f"¡¡Exception!! {EX}")
        raise SystemExit

    ## VARS??
    debug = False
    for opt, arg in opts:
        if opt in ('-d', '-v', '--debug', '--verbose'): debug = True

    if debug:
        logging.basicConfig(level=logging.DEBUG, format=FORMAT)
    else:
        logging.basicConfig(level=logging.INFO)
        ## limit "Traceback" outputs
        sys.tracebacklimit=0

#########################################################################
    main()
