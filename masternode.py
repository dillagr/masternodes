#!/usr/bin/env python3
##
##
import json
import sys
import subprocess
import requests
import os

from dotenv import dotenv_values
dot = dotenv_values()


#from emoji import emojize
import logging
FORMAT = "%(asctime)s - %(name)s - %(levelname)s: %(message)s"
logging.basicConfig(level=logging.INFO, format=FORMAT)
logr = logging.getLogger('masternode')



## ---> EDITS HERE! <---
COINCLI = '/usr/local/bin/flits-cli'


## SEND A SHOUTOUT!!!
def send_alert(message):
    ## just sends the message over telegram
    subprocess.run( ["/usr/local/bin/telegram-send", f"{message}"], stdout=subprocess.PIPE )
    return True


## START MASTERNODE!!!
def start_mnode(masternode):
    ## starts the masternode
    #subprocess.run( [COINCLI,'startmasternode','alias','0', masternode], stdout=subprocess.PIPE )
    debug = walletrpc(method="startmasternode", params=["alias", "0", masternode])
    logr.debug(f"Response: {json.dumps(debug, indent=4)}")
    return True


## COLLECT DATA!!!
def walletrpc(method, params = None):

    ### VARIABLES
    RPCUSER=dot.get('_USER')
    RPCPASS=dot.get('_PASS')
    RPCPORT=dot.get('_PORT')
    _RPCURL = "http://127.0.0.1:" +str(RPCPORT)
    HEADERS = {'content-type': "application/json", 'cache-control': "no-cache"}
    PAYLOAD = json.dumps({"method": method, "params": params})
    ### DO-NOT-MODIFY HERE

    #current = subprocess.run([COINCLI, 'getblockcount'], stdout=subprocess.PIPE).stdout.decode()
    try:
        r = requests.post( _RPCURL, headers=HEADERS, data=PAYLOAD, auth=(RPCUSER, RPCPASS) )
        return r.json()
    except:
        return None



js = walletrpc(method="listmasternodeconf")
logr.debug(f"MASTERNODE: {json.dumps(js, indent=4)}")

blk = walletrpc(method="getblockcount")
logr.debug(f"BLOCK: {json.dumps(blk, indent=4)}")

#if blk.get('result') <= 1000:
#    raise SystemExit

#ss = walletrpc(method="getstakingstatus")
#logr.debug(f"BLOCK: {json.dumps(ss, indent=4)}")


for MN in js.get("result"):

    MESSAGE = f"⚠️ WARNING! {dot.get('_TICK')} {MN.get('alias')} is {MN.get('status')}."

    if MN['status'] in ('ENABLED', 'ACTIVE', 'PRE_ENABLED'): pass

    elif MN['status'] in ('EXPIRED', 'MISSING'):
        start_mnode(MN['alias'])
        send_alert(MESSAGE)

    else:
        logr.debug(f"⚠️ WARNING! {dot.get('_TICK')} Masternode {MN.get('alias')} is {MN.get('status')}.")
        MESSAGE = f"⚠️ WARNING! {dot.get('_TICK')} Masternode {MN.get('alias')} is {MN.get('status')}."
        send_alert(MESSAGE)

