#!/usr/bin/env python3

import json
import httpx
import telegram
import decimal
import sys
import platform

from random import randint
from decouple import config
from loguru import logger

_ADDR=config('_ADDR')
_PORT=config('_PORT')
_USER=config('_USER')
_PASS=config('_PASS')

rs = httpx.Client(http2=True)

ERRMESSAGE=""
APISRCH=config('APISRCH')

## DO NOT CHANGE
HEADERS = { "Content-type": "application/json" }
_THAT = f"http://127.0.0.1:{_PORT}"

_HOST=platform.node()

#########################################################################
def get_blockcount() -> dict:
    ## BLKHEIGHT
    jc = walletrpc(method="getblockcount", params=None)
    return jc.get("result")

#########################################################################
def get_blockhash(blockheight) -> dict:
    ## BLKHASH
    jc = walletrpc(method="getblockhash", params=[blockheight])
    return jc.get("result")    

#########################################################################
def get_txid(blockheight):
    blockhash = get_blockhash(blockheight)
    txid = walletrpc("getblock", [blockhash])
    assert txid.get('result'), f"¡¡ERROR!! Unrecognized block {blockheight}."
    return txid.get("result").get("tx")[1]

#########################################################################
def get_rawtransaction(blockheight):
    txid = get_txid(blockheight)
    tx = walletrpc("getrawtransaction", [txid])
    assert tx.get('result'), "¡¡ERROR!! Missing raw transaction."
    return tx.get("result")

#########################################################################
def decode_rawtransaction(blockheight):
    hexstring = get_rawtransaction(blockheight)
    tx = walletrpc("decoderawtransaction", [hexstring])
    assert tx.get('result'), "¡¡ERROR!! Unable to decode raw transaction"
    return tx.get("result").get("vout")

#########################################################################
def fetch_blockhash(height) -> str:
    THISURL=APISRCH +"?query=" +str(height)
    x = rs.get(THISURL)
    if x.status_code == 503: return None
    xj = x.json()
    if len(xj.get("response")) == 0: return None
    return xj["response"].get("hash")

#########################################################################
def fetch_blockheight() -> int:
    THISURL="https://explorer.decenomy.net/coreapi/v1/coins/FLS"
    x = rs.get(THISURL)
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
    #logger.debug(f"PAYLOAD: {json.dumps(PAYLOAD, indent=4)}")
    ### DO-NOT-MODIFY HERE

    try:
        r = rs.post( _RPCURL, headers=HEADERS, data=PAYLOAD, auth=(_USER, _PASS) )
        return r.json()
    except:
        return None


#########################################################################
def main() -> None :

    bot = telegram.Bot(token=config('TOKEN'))

    BLKCOUNT = get_blockcount()
    assert int(BLKCOUNT) > 0, "!!ERROR [@{_HOST}]!! Could not get block height."
    BLKHEIGHT = int(BLKCOUNT) - randint(3,12)  ## explorer might be delayed
    BLKHASH = get_blockhash(BLKHEIGHT)

    if BLKHEIGHT:
        QHEIGHT=BLKHEIGHT
    else:
        ERRMESSAGE = f"⚠️ WARNING [@{_HOST}]: Block height is non-numeric/invalid."
        bot.sendMessage(chat_id=config('_CHID'), text=ERRMESSAGE)
        sys.exit(99)


    EXPHASH=fetch_blockhash(QHEIGHT)
    EXPHEIGHT=fetch_blockheight()
    logr.info(f"Explorer HASH for Block {QHEIGHT}: {EXPHASH}")
    logr.info(f"Blockchain HASH for Block {QHEIGHT}: {BLKHASH}")
    logr.info(f"Explorer height {EXPHEIGHT}")
    logr.info(f"Blockchain height {BLKCOUNT}")
    
    if not EXPHASH:
        ERRMESSAGE = f"⚠️ WARNING [@{_HOST}]: FLITS explorer has issues!"
        bot.sendMessage(chat_id=config('_CHID'), text=ERRMESSAGE)
        sys.exit(99)



    ## APPLY THE LOGIC
    if EXPHASH != BLKHASH:
        ERRMESSAGE = f"⚠️ WARNING [@{_HOST}]: Local hash not same as Explorer hash (at height: {BLKHEIGHT})."
        bot.sendMessage(chat_id=config('_CHID'), text=ERRMESSAGE)
        sys.exit(99)

    if abs(BLKCOUNT -EXPHEIGHT) > 9:
        ERRMESSAGE = f"⚠️ WARNING [@{_HOST}]: Block height ({BLKCOUNT}) not same as Explorer (height: {EXPHEIGHT})."
        bot.sendMessage(chat_id=config('_CHID'), text=ERRMESSAGE)
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
        logr.WARN(f"¡¡Exception!! {EX}")
        raise SystemExit

    ## VARS??
    debug = False
    for opt, arg in opts:
        if opt in ('-d', '-v', '--debug', '--verbose'): debug = True

    if debug:
        logging.basicConfig(level=logging.INFO, format=FORMAT)
    else:
        logging.basicConfig(level=logging.WARN)
        ## limit "Traceback" outputs
        sys.tracebacklimit=0

#########################################################################
    main()
