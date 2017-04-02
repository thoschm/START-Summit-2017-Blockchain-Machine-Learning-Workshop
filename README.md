# START-Summit-2017-Blockchain-Machine-Learning-Workshop
Presentation Material and Sample Code from the Blockchain and Machine Learning Workshop at START Summit 2017 in Switzerland

# Intro
The purpose of this code is to demonstrate in a simple example, how to bring Blockchain technology, smart contracts and Machine Learning together.
It implements a simple chat client that can transmit messages, images and tags to the Blockchain. Tags are automatically extracted via a simple Deep Neural Network using the Keras Python Package with Tensorflow backend.
In addition to just sending messages, the client also supports listening for new messages on the Blockchain from other participants.
For details, please view the workshop presentation.

# Files
- runTestnet.sh: launches a local development Blockchain for easy testing
- contract.sol: contains the smart contract code in solidity language
- installContract.py: Python script for sending our contract to the Blockchain
- user.py: Python script that contains the actual chat client
- classify.py: Python script to classifiy an image file

# Setup
I really recommend using Linux at this point. The installation guidelines will focus on Ubuntu Linux 16.04 LTS, but should be similar for other distributions.

We need to install Python 2.7, pip, curl and git first:
- open a Linux Terminal and enter the following command:
- sudo apt-get install python2.7 python-pip curl git build-essential
- [enter key]

Install current nodejs version:
- inside the Terminal:
- curl -sL https://deb.nodesource.com/setup_7.x | sudo -E bash -
- [enter key]
- sudo apt-get install -y nodejs
- [enter key]

Install the blockchain test environment:
- sudo npm install -g ethereumjs-testrpc
- [enter key]

Now let's clone the workshop code:
- inside the Terminal enter on a new line:
- cd
- git clone https://github.com/thoschm/START-Summit-2017-Blockchain-Machine-Learning-Workshop.git workshop_code
- [enter key]








