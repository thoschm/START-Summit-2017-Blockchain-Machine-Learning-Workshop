'''
Introduction:
Workshop Example Code from the Blockchain and Machine Learning Workshop at START Summit 2017 in Switzerland

Description:
The file user.py implements an easy chat-client for transmitting text and images to Blockchain smart contract.
Tags are automatically extracted from an image using a Deep Residual Neural Network.

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
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'
from ethjsonrpc import EthJsonRpc
import time
import io
from PIL import Image
import signal
from ethereum.abi import decode_abi
from ethereum import utils

# import ML stuff
from resnet50 import ResNet50
from keras.preprocessing import image
from imagenet_utils import preprocess_input, decode_predictions
import numpy as np


##################################
# simple keras deep learning
##################################
class ImageClassifier:
    @staticmethod
    def predict(filename):
        assert os.path.isfile(filename) and 'cannot find file'
        model = ResNet50(weights='imagenet')

        img = image.load_img(filename, target_size=(224, 224))
        x = image.img_to_array(img)
        x = np.expand_dims(x, axis=0)
        x = preprocess_input(x)

        preds = decode_predictions(model.predict(x))
        if len(preds) == 0:
            return None
        return preds[0][0][1]


##################################
# config
##################################
RPC_HOST = '127.0.0.1'
RPC_PORT = 8545
GAS = 20000000
IMAGE_SIZE = 256


##################################
# signal handler
##################################
LISTENING = False
def handler(sig, frame):
    global LISTENING
    if not LISTENING:
        sys.stdout.write('\nenter q or quit to leave\n>> ')
    else:
        print('\n')
    LISTENING = False
signal.signal(signal.SIGINT, handler)


##################################
# decode transaction input
##################################
class Decoder:
    @staticmethod
    def decodeABI(tinput, sig='setNewUserState(string,bytes,string)'):
        abi = tinput[2 :]
        hash = utils.sha3(sig)[: 4].encode('hex')
        if abi[: 8] != hash:
            return None
        return decode_abi(['string', 'bytes', 'string'], abi[8 :].decode('hex'))


##################################
# image helper
##################################
class ImageHelper:
    @staticmethod
    def imgToBytes(image):
        assert isinstance(image, Image.Image) and 'give me correct PIL Image'
        # resize
        data = io.BytesIO()
        image.resize(size=(IMAGE_SIZE, IMAGE_SIZE), resample=Image.LANCZOS).save(data, 'JPEG', quality=90)
        return data.getvalue()

    @staticmethod
    def bytesToImg(data):
        assert isinstance(data, bytes) and 'give me correct bytestream'
        return Image.open(io.BytesIO(data))


##################################
# main
##################################
def main():
    #
    # receive contract addr
    #
    if len(sys.argv) != 3:
        print('Usage:\npython user.py <contract addr> <account addr>')
        sys.exit(-1)
    contract_addr = sys.argv[1]
    account_addr = sys.argv[2]

    #
    # create rpc interface
    #
    try:
        print('-' * 80)
        rpc = EthJsonRpc(RPC_HOST, RPC_PORT)
        print('client software: {}'.format(rpc.web3_clientVersion()))
        print('block: {}'.format(rpc.eth_blockNumber()))
        print('address: {}'.format(rpc.eth_coinbase()))
    except:
        print('unable to connect to rpc server at {}:{}'.format(RPC_HOST, RPC_PORT))
        sys.exit(-1)

    #
    # check contract is online
    #
    print('-' * 80)
    if rpc.eth_getCode(contract_addr) == '0x0':
        print('!!! contract code not available on blockchain !!!')
        sys.exit(-1)
    print('found contract on blockchain!')

    #
    # console
    #
    topics = []
    print('-' * 80)
    print('starting chat command line...')
    while True:
        #
        # simply read input
        #
        sys.stdout.write('>> ')
        command = sys.stdin.readline()

        #
        # quit?
        #
        if 'q' in command:
            sys.exit(0)

        #
        # show help
        #
        elif command == '\n' or 'help' in command:
            print('commands: help, send, status, topics, search, listen')

        #
        # compose new message
        #
        elif 'send' in command:
            print('-' * 80)
            print('[composing new message]')
            sys.stdout.write('message....: ')
            msg = sys.stdin.readline().strip()
            sys.stdout.write('image file.: ')
            img = sys.stdin.readline().strip()
            sys.stdout.write('custom tags: ')
            tag = sys.stdin.readline().strip()
            print('-' * 80)
            print('sending...')
            # loading image
            try:
                image = Image.open(img)
            except Exception as e:
                print('loading {} failed'.format(img))
                continue
            # prediction
            print('precessing image...')
            label = ImageClassifier.predict(img)
            if label is None:
                print('classification failed')
                continue
            print('label: {}'.format(label))
            tag += ' #' + label
            bs = ImageHelper.imgToBytes(image)
            tx = rpc.call_with_transaction(account_addr, contract_addr,
                                           'setNewUserState(string,bytes,string)', [msg, bs, tag],
                                           gas=GAS)
            print('done, transaction id: {}'.format(tx))

        #
        # get own last post
        #
        elif 'status' in command:
            print('-' * 80)
            print('[receiving last post]')
            userMessage, userImage, userTags = rpc.call(contract_addr, 'getUserState(address)', [account_addr],
                                                        ['string', 'bytes', 'string'])
            if not userMessage:
                print('nothing posted yet')
                continue
            print('  content: {}'.format(userMessage))
            print('  tags...: {}'.format(userTags))
            ImageHelper.bytesToImg(userImage).show()

        #
        # set tag filters
        #
        elif 'topics' in command:
            topics = [t.strip() for t in command.split()[1 : ]]
            if len(topics) == 0:
                print('please provide actual topics after <topics> command')
                continue
            print('filter set for messages on topics: {}'.format(topics))

        #
        # search complete blockchain for messages with certain tags
        #
        elif 'search' in command:
            if len(topics) == 0:
                print('call topics first')
                continue
            curBlock = rpc.eth_blockNumber()
            for i in range(curBlock + 1):
                for trans in rpc.eth_getBlockByNumber(i)['transactions']:
                    res = Decoder.decodeABI(trans['input'])
                    if res is None:
                        continue
                    msg, code, tags = res
                    if all(t not in tags for t in topics):
                        continue
                    print('-' * 80)
                    print('message from user {} (block {}):'.format(trans['from'], i))
                    print('  content: {}'.format(msg))
                    print('  tags...: {}'.format(tags))
                    ImageHelper.bytesToImg(code).show(title='{}'.format(tags))

        #
        # start listening for messages
        #
        elif 'listen' in command:
            if len(topics) == 0:
                print('call topics first')
                continue
            global LISTENING
            LISTENING = True
            curBlock = rpc.eth_blockNumber()
            while LISTENING:
                newBlock = rpc.eth_blockNumber()
                if newBlock > curBlock:
                    print('new block detected ({})'.format(newBlock))
                    curBlock = newBlock
                    for trans in rpc.eth_getBlockByNumber(newBlock)['transactions']:
                        res = Decoder.decodeABI(trans['input'])
                        if res is None:
                            continue
                        msg, code, tags = res
                        if all(t not in tags for t in topics):
                            continue
                        print('-' * 80)
                        print('message from user {} (block {}):'.format(trans['from'], newBlock))
                        print('  content: {}'.format(msg))
                        print('  tags...: {}'.format(tags))
                        ImageHelper.bytesToImg(code).show(title='{}'.format(tags))
                time.sleep(1)

        #
        # default response
        #
        else:
            print('command not recognized')


##################################
# run
##################################
if __name__ == '__main__':
    main()
