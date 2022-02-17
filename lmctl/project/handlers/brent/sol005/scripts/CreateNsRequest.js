/*
 This is the generic message creation logic for CreateNsRequest messages based on the 3.3.1 version of the ETSI SOL005 specification
 */
logger.debug('Generating CreateNsRequest message for ETSI SOL005 v3.3.1');
load('classpath:scripts/lib.js');

// Create the message object to be returned
var message = {additionalParams: {}};

// Set the standard message properties
// The NSD id is required, the other fields are optional
setPropertyIfNotNull(executionRequest.properties, message, 'nsdId');
setPropertyIfNotNull(executionRequest.properties, message, 'nsName');
setPropertyIfNotNull(executionRequest.properties, message, 'nsDescription');

// Whilst not specifically present in the 3.3.1 version of the specification, we will add an
// additionalParams block here since all other request messages feature this.
for (var key in executionRequest.getProperties()) {
    if (key.startsWith('additionalParams.')) {
        // print('Got property [' + key + '], value = [' + executionRequest.properties[key] + ']');
        addProperty(message, key, executionRequest.properties[key]);
    }
}

logger.debug('Message generated successfully');
// Turn the message object into a JSON string to be returned back to the Java driver
JSON.stringify(message);