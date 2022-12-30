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

#########################################################################
def get_block_count() -> dict:
    ##
    GTBLCOUNT = {"jsonrpc": "1.0", "id": "blkcount", "method": "getblockcount", "params": [] } 
    PAYLOAD = json.dumps(GTBLCOUNT)
    c = requests.post(_THAT, headers=HEADERS, data=PAYLOAD, auth=(_USER, _PASS))
    jc = c.json(parse_float=decimal.Decimal)
    return jc.get("result")

#########################################################################
def get_block_hash(blockheight) -> dict:
    ## BLKHEIGHT
    GTBLHASH = {"jsonrpc": 1.0, "id": "blkhash", "method": "getblockhash", "params": [blockheight]} 
    PAYLOAD = json.dumps(GTBLHASH)
    c = requests.post(_THAT, headers=HEADERS, data=PAYLOAD, auth=(_USER, _PASS))
    jc = c.json(parse_float=decimal.Decimal)
    return jc.get("result")    

#########################################################################
def fetch_block_hash(height) -> str:
    THISURL=APISRCH +"?query=" +str(height)
    x = requests.get(THISURL)
    #print(x, x.status_code)
    #print(THISURL)
    if x.status_code == 503:
        return None
    xj = x.json()
    if len(xj.get("response")) == 0:
        return None
    return xj["response"].get("hash")


#########################################################################
def main() -> None :

    bot = telegram.Bot(token=dot.get('TOKEN'))

    BLKCOUNT = get_block_count()
    assert int(BLKCOUNT) > 0, "!!ERROR!! Could not get block height."
    BLKHEIGHT = int(BLKCOUNT) - randint(5,22)  ## explorer might be delayed
    BLKHASH = get_block_hash(BLKHEIGHT)

    if BLKHEIGHT:
        QHEIGHT=BLKHEIGHT
    else:
        ERRMESSAGE = "⚠️ WARNING: Block height is non-numeric/invalid."
        bot.sendMessage(chat_id=dot.get('_CHID'), text=ERRMESSAGE)
        sys.exit(99)


    EXPHASH=fetch_block_hash(QHEIGHT)
    logr.debug(f"Explorer HASH for Block {QHEIGHT}: {EXPHASH}")
    logr.debug(f"Blockchain HASH for Block {QHEIGHT}: {BLKHASH}")
    
    if not EXPHASH:
        ERRMESSAGE = "⚠️ WARNING: TRTT explorer has issues!"
        bot.sendMessage(chat_id=dot.get('_CHID'), text=ERRMESSAGE)
        sys.exit(99)



    ## APPLY THE LOGIC
    if EXPHASH != BLKHASH:
        ERRMESSAGE = f"⚠️ WARNING: Local [{_HOST}] hash not same as Explorer hash (at height{BLKHEIGHT})."
        bot.sendMessage(chat_id=dot.get('_CHID'), text=ERRMESSAGE)
        sys.exit(99)



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
