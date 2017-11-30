'''
Introduction:
Workshop Example Code from the Blockchain and Machine Learning Workshop at START Summit 2017 in Switzerland

Description:
This file will take the smart contract code from contract.sol, compile it and send it via transaction
to the Blockchain. Afterwards it will wait for the transaction to be included in a new block and
print the contract address.

Author:
Thomas Schmiedel, Data Reply 2017

Mail:
t.schmiedel@reply.de

Note:
This is just example code and not perfect yet, if you have any questions, advice, ..., just drop me a mail :-)
'''

##################################
# imports
##################################
from __future__ import print_function
import os, sys
from ethjsonrpc import EthJsonRpc
import time


##################################
# config
##################################
RPC_HOST = '127.0.0.1'
RPC_PORT = 8545
CONTRACT = 'contract.sol'
CONTRACT_COMPILED = 'contract_sol_ImgStorage.bin'
GAS = 20000000
WAIT_BLOCKS = 5


##################################
# main
##################################
def main():
    #
    # check
    #
    assert os.path.isfile(CONTRACT) and 'contract file not found'

    #
    # now, just connect to our own blockchain node via rpc interface
    #
    try:
        rpc = EthJsonRpc(RPC_HOST, RPC_PORT)
        print('-' * 80)
        print('client software: {}'.format(rpc.web3_clientVersion()))
        print('block: {}'.format(rpc.eth_blockNumber()))
        print('address: {}'.format(rpc.eth_coinbase()))
    except:
        print('unable to connect to rpc server at {}:{}'.format(RPC_HOST, RPC_PORT))
        sys.exit(-1)

    #
    # compile contract
    #
    print('-' * 80)
    print('compiling contract...')
    os.system('solcjs --bin {} > /dev/null'.format(CONTRACT))
    with open(CONTRACT_COMPILED, 'r') as f:
        contract_bin = f.read()
    print(contract_bin)

    #
    # create contract
    #
    print('-' * 80)
    lastBlock = rpc.eth_blockNumber()
    contract_tx = rpc.create_contract(rpc.eth_coinbase(), contract_bin, gas=GAS)
    print('contract sent, waiting for it to be mined...')
    #
    # get current block count
    #
    numTry = 0
    contract_addr = None
    while True:
        curBlock = rpc.eth_blockNumber()
        if curBlock > lastBlock:
            lastBlock = curBlock
            numTry += 1
            try:
                contract_addr = rpc.get_contract_address(contract_tx)
                if rpc.eth_getCode(contract_addr) == '0x0':
                    raise Exception()
                print('contract mined (block: {})'.format(curBlock))
                break
            except:
                print('new block detected, but contract not mined')
                if numTry == WAIT_BLOCKS:
                    print('publishing contract failed')
                    sys.exit(-1)
        time.sleep(1)
    #
    # return contract addr
    #
    print('-' * 80)
    print('contract_address:\n\n\n--> {} <--\n\n'.format(contract_addr))
    print('-' * 80)


##################################
# run
##################################
if __name__ == '__main__':
    main()
