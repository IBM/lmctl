/*
 This is the generic message creation logic for OperateVnfRequest messages based on the 2.4.1 version of the ETSI SOL003 specification
 */
logger.debug('Generating OperateVnfRequest message for VNFM');
load('classpath:scripts/lib.js');

// Create the message object to be returned
var message = {additionalParams: {}};

// Set the standard message properties
message.changeStateTo = 'STOPPED';
// Should set stopType and gracefulStopTimeout (if required)
message.stopType = 'FORCEFUL';

logger.debug('Message generated successfully');
// Turn the message object into a JSON string to be returned back to the Java driver
JSON.stringify(message);