/*
 This is the generic message creation logic for InstantiateNsRequest messages based on the 2.4.1 version of the ETSI SOL005 specification
 */
logger.debug('Generating InstantiateNsRequest message for ETSI SOL005 v3.3.1');
load('classpath:scripts/lib.js');

// Create the message object to be returned
var message = {extVirtualLinks: [], extManagedVirtualLinks: [], vimConnectionInfo: [], additionalParams: {}};

// Set the standard message properties
// The nsFlavourId is required, the other fields are optional
setPropertyIfNotNull(executionRequest.properties, message, 'nsFlavourId');
setPropertyIfNotNull(executionRequest.properties, message, 'nsInstantiationLevelId');

for (var key in executionRequest.getProperties()) {
    if (key.startsWith('additionalParams.') || key.startsWith('extVirtualLinks.') || key.startsWith('extManagedVirtualLinks.') || key.startsWith('vimConnectionInfo.')) {
        // print('Got property [' + key + '], value = [' + executionRequest.properties[key] + ']');
        addProperty(message, key, executionRequest.properties[key]);
    }
}

logger.debug('Message generated successfully');
// Turn the message object into a JSON string to be returned back to the Java driver
JSON.stringify(message);