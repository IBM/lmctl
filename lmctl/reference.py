import lmctl.utils.descriptors as descriptors

######################################
# Exceptions
######################################

class NotResolvableError(Exception):
    pass

class BadReferenceError(Exception):
    pass

class ReferenceSchema:

    def __init__(self, root_prefix, separator):
        self.root_prefix = root_prefix
        self.separator = separator

    def is_reference(self, potential_ref):
        starting_point = '{0}{1}'.format(self.root_prefix, self.separator)
        return potential_ref != None and potential_ref.startswith(starting_point) and len(potential_ref)>len(starting_point)

    def reference_value(self, reference):
        if not self.is_reference(reference):
            raise BadReferenceError('\'{0}\' is not a valid reference'.format(reference))
        reference_value = reference[len('{0}{1}'.format(self.root_prefix, self.separator)):]
        return reference_value 

    def reference_breakdown(self, full_reference):
        reference = self.reference_value(full_reference)
        parts = []
        remaining_reference = reference
        while remaining_reference != None:
            matching_idx = remaining_reference.find(self.separator)
            if matching_idx == -1:
                parts.append(remaining_reference)
                remaining_reference = None
            else:
                new_part = remaining_reference[:matching_idx]
                parts.append(new_part)
                remainder_idx = matching_idx + len(self.separator)
                remaining_reference = remaining_reference[remainder_idx:]
        return parts

class ReferenceMachine:

    def __init__(self, root_prefix, separator):
        self.schema = ReferenceSchema(root_prefix, separator)
        
    def builder(self):
        return ReferenceBuilder(self.schema)

    def is_reference(self, potential_ref):
        return self.schema.is_reference(potential_ref)

    def resolve(self, reference, resolution_map):
        return ReferenceResolver(self.schema, resolution_map).resolve(reference)

class ReferenceBuilder:

    def __init__(self, schema):
        self.schema = schema
        self.parts = []

    def add(self, part):
        self.parts.append(part)
        return self

    def add_before(self, part):
        self.parts.insert(0, part)
        return self

    def get(self):
        parts_str = ''
        idx = 0
        if len(self.parts) == 0:
            raise BadReferenceError('Cannot build a reference with no parts')
        for part in self.parts:
            if idx != 0:
                parts_str += self.schema.separator
            parts_str += part
            idx += 1
        return '{0}{1}{2}'.format(self.schema.root_prefix, self.schema.separator, parts_str)

class ReferenceResolver:

    def __init__(self, schema, resolution_map):
        self.schema = schema
        self.resolution_map = resolution_map

    def resolve(self, reference):
        reference_parts = self.schema.reference_breakdown(reference)
        return self.__resolve(reference, reference_parts, self.resolution_map)

    def __resolve(self, reference, reference_parts, resolution_map):
        if len(reference_parts) == 0:
            return None
        next_part = reference_parts.pop(0)
        if next_part not in resolution_map:
            raise NotResolvableError('Cannot find \'{0}\' in reference: {1}'.format(next_part, reference))
        next_value = resolution_map[next_part]
        if len(reference_parts) == 0:
            return next_value
        elif type(next_value) is dict:
            return self.__resolve(reference, reference_parts, next_value)
        else:
            next_step = reference_parts.pop(0)
            raise BadReferenceError('Reference has invalid step from \'{0}\' to \'{1}\': {2}'.format(next_part, next_step, reference))


