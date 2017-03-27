/*
Introduction:
Workshop Example Code from the Blockchain and Machine Learning Workshop at START Summit 2017 in Switzerland

Description:
This file implements the smart contract to be sent to the Blockchain.

Author:
Thomas Schmiedel, Data Reply 2017

Mail:
t.schmiedel@reply.de

Note:
This is just example code and not perfect yet, if you have any questions, advice, ..., just drop me a mail :-)
*/

pragma solidity ^0.4.0;

/*
 * The actual smart contract that can store a message, an image and tags for each user
 */
contract ImgStorage
{
	// data structure to contain message, image and tags
	struct UserState
	{
        string userMessage;
        bytes userImage;
        string userTags;
	}
	
	// create a mapping from account-address to UserState,
	// this way, each user can store his own state,
	// the history is within the blockchain and can be retrieved as well
	// --> nothing lost
	mapping (address => UserState) userMapping;

	// now just some functions to actually set a new state and request it
	function getOwnUserState() constant returns(string, bytes, string)
	{
	    return getUserState(msg.sender);
	}

	function getUserState(address target) constant returns(string, bytes, string)
	{
        return (userMapping[target].userMessage,
                userMapping[target].userImage,
                userMapping[target].userTags);
	}

	function setNewUserState(string message, bytes imgData, string tags)
	{
		userMapping[msg.sender].userMessage = message;
		userMapping[msg.sender].userImage = imgData;
		userMapping[msg.sender].userTags = tags;
	}
}
