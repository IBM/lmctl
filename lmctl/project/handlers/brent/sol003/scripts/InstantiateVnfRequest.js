/*
 This is the generic message creation logic for InstantiateVnfRequest messages based on the 2.4.1 version of the ETSI SOL003 specification
 */
logger.debug('Generating InstantiateVnfRequest message for ETSI SOL003 v2.4.1');
load('classpath:scripts/lib.js');

// Create the message object to be returned
var message = {extVirtualLinks: [], extManagedVirtualLinks: [], vimConnectionInfo: [], additionalParams: {}};

// Set the standard message properties
// The flavourId is required, the other fields are optional
setPropertyIfNotNull(executionRequest.properties, message, 'flavourId');
setPropertyIfNotNull(executionRequest.properties, message, 'instantiationLevelId');
setPropertyIfNotNull(executionRequest.properties, message, 'localizationLanguage');

for (var key in executionRequest.getProperties()) {
    if (key.startsWith('additionalParams.') || key.startsWith('extVirtualLinks.') || key.startsWith('extManagedVirtualLinks.') || key.startsWith('vimConnectionInfo.')) {
        // print('Got property [' + key + '], value = [' + executionRequest.properties[key] + ']');
        addProperty(message, key, executionRequest.properties[key]);
    }
}

logger.debug('Message generated successfully');
// Turn the message object into a JSON string to be returned back to the Java driver
JSON.stringify(message);