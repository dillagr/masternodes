#!/usr/bin/env python3

import json
import requests
import telegram
import decimal
import sys

from random import randint
from dotenv import dotenv_values
dot = dotenv_values()

#########################################################################

_ADDR=dot.get('_ADDR')
_PORT=dot.get('_PORT')
_USER=dot.get('_USER')
_PASS=dot.get('_PASS')

ERRMESSAGE=""
APISRCH=dot.get('APISRCH')

## DO NOT CHANGE
HEADERS = { "Content-type": "application/json" }
_THAT="http://" +_ADDR +":" +_PORT

#########################################################################

import logging
FORMAT = "%(asctime)s - %(name)s - %(levelname)s: %(message)s"
logging.basicConfig(level=logging.DEBUG, format=FORMAT)
logr = logging.getLogger('blockhash')



def get_block_count():
    ##
    GTBLCOUNT = {"jsonrpc": "1.0", "id": "blkcount", "method": "getblockcount", "params": [] } 
    PAYLOAD = json.dumps(GTBLCOUNT)
    c = requests.post(_THAT, headers=HEADERS, data=PAYLOAD, auth=(_USER, _PASS))
    jc = c.json(parse_float=decimal.Decimal)
    return jc.get("result")

def get_block_hash(blockheight):
    ## BLKHEIGHT
    GTBLHASH = {"jsonrpc": 1.0, "id": "blkhash", "method": "getblockhash", "params": [blockheight]} 
    PAYLOAD = json.dumps(GTBLHASH)
    c = requests.post(_THAT, headers=HEADERS, data=PAYLOAD, auth=(_USER, _PASS))
    jc = c.json(parse_float=decimal.Decimal)
    return jc.get("result")    

BLKCOUNT = get_block_count()
assert int(BLKCOUNT) > 0, "!!ERROR!! Could not get block height."
BLKHEIGHT = int(BLKCOUNT) - randint(5,22)  ## explorer might be delayed
BLKHASH = get_block_hash(BLKHEIGHT)
#print(BLKHEIGHT, BLKHASH)

#########################################################################

def fetch_block_hash(height):
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


def main() -> None :

    bot = telegram.Bot(token=dot.get('TOKEN'))

    if BLKHEIGHT:
        QHEIGHT=BLKHEIGHT
    else:
        ERRMESSAGE = "⚠️ WARNING: Block height is non-numeric/invalid."
        bot.sendMessage(chat_id=dot.get('_CHID'), text=ERRMESSAGE)
        sys.exit(99)


    

#########################################################################


    EXPHASH=fetch_block_hash(QHEIGHT)
    logr.debug(f"Explorer HASH for Block {QHEIGHT}: {EXPHASH}")
    logr.debug(f"Blockchain HASH for Block {QHEIGHT}: {BLKHASH}")
    
    if not EXPHASH:
        ERRMESSAGE = "⚠️ WARNING: TRTT explorer has issues!"
        bot.sendMessage(chat_id=dot.get('_CHID'), text=ERRMESSAGE)
        sys.exit(99)


#########################################################################

    ## APPLY THE LOGIC
    if EXPHASH != BLKHASH:
        ERRMESSAGE = "⚠️ WARNING: Local hash not same as Explorer hash (at height{}).".format(BLKHEIGHT)
        bot.sendMessage(chat_id=dot.get('_CHID'), text=ERRMESSAGE)
        sys.exit(99)



if __name__ == "__main__":
    main()
