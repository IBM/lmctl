/*
 This is the generic message creation logic for ScaleVnfRequest messages based on the 2.4.1 version of the ETSI SOL003 specification
 */
logger.debug('Generating ScaleVnfRequest message for VNFM');
load('classpath:scripts/lib.js');

// Create the message object to be returned
var message = {additionalParams: {}};

// Set the standard message properties
message.type = executionRequest.properties.scaleType;
message.aspectId = executionRequest.properties.scaleAspectId;
setPropertyIfNotNull(executionRequest.properties, message, 'numberOfSteps');
setPropertyIfNotNull(executionRequest.properties, message, 'node_type');

logger.debug('Message generated successfully');
// Turn the message object into a JSON string to be returned back to the Java driver
JSON.stringify(message);