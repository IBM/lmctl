/*
 This is the generic message creation logic for HealNsRequest messages based on the 3.3.1 version of the ETSI SOL005 specification
 */
logger.debug('Generating HealNsRequest message for ETSI SOL005 v3.3.1');
load('classpath:scripts/lib.js');

// Create the message object to be returned
var message = {additionalParams: {}};

for (var key in executionRequest.getProperties()) {
    if (key.startsWith('additionalParams.')) {
        // print('Got property [' + key + '], value = [' + executionRequest.properties[key] + ']');
        addProperty(message, key, executionRequest.properties[key]);
    }
}

logger.debug('Message generated successfully');
// Turn the message object into a JSON string to be returned back to the Java driver
JSON.stringify(message);