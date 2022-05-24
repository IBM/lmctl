/*
 This is the generic parsing logic for NsInstance objects based on the 3.3.1 version of the ETSI SOL005 specification
 */
logger.debug('Parsing NsInstance message for ETSI SOL005 v3.3.1');
load('classpath:scripts/lib.js');

var parsedMessage = JSON.parse(message);
outputs.put('nsInstanceId', parsedMessage.id);

var flattenedProperties = flattenPropertyMap(parsedMessage);
for (var propertyName in flattenedProperties) {
    // Ignore certain property names
    if (propertyName !== 'id' && propertyName !== 'name' && propertyName !== 'index' && !propertyName.startsWith('_links.')) {
        outputs.put(propertyName, flattenedProperties[propertyName]);
    }
}

logger.debug('Message parsed successfully');
