from werkzeug.exceptions import abort

from nebula_communication.nebula_functions import fetch_vertex, find_destination
from nebula_communication.template_builder.definition.AttributeDefinition import construct_attribute_definition
from nebula_communication.template_builder.definition.ProperyDefinition import construct_property_definition
from parser.parser.tosca_v_1_3.definitions.CapabilityDefinition import CapabilityDefinition


def construct_capability_definition(list_of_vid) -> dict:
    result = {}
    capability_definition = CapabilityDefinition('name').__dict__

    for vid in list_of_vid:
        vertex_value = fetch_vertex(vid, 'CapabilityDefinition')
        vertex_value = vertex_value.as_map()
        tmp_result = {}
        vertex_keys = vertex_value.keys()
        for vertex_key in vertex_keys:
            if not vertex_value[vertex_key].is_null() and vertex_key not in {'vertex_type_system', 'name'}:
                tmp_result[vertex_key] = vertex_value[vertex_key].as_string()
        edges = set(capability_definition.keys()) - set(vertex_keys) - {'vid'}
        for edge in edges:
            destination = find_destination(vid, edge)
            if edge == 'type':
                capability_type = fetch_vertex(destination[0], 'CapabilityType')
                capability_type = capability_type.as_map()
                capability_type = capability_type['name'].as_string()
                tmp_result['type'] = capability_type
            elif edge == 'properties':
                tmp_result['properties'] = construct_property_definition(destination)
            elif edge == 'attributes':
                tmp_result['attributes'] = construct_attribute_definition(destination)
            elif edge == 'valid_source_types':
                valid_source_types = []
                for valid_source_type in destination:
                    data = fetch_vertex(valid_source_type, 'NodeType')
                    data = data.as_map()
                    valid_source_types.append(data['name'].as_string())
                tmp_result['valid_source_types'] = valid_source_types
            elif edge == 'occurrences':
                if destination:
                    relationship = fetch_vertex(destination[0], 'Occurrences')
                    relationship = relationship.as_map()
                    minimum: str = relationship['minimum'].as_string()
                    maximum: str = relationship['maximum'].as_string()
                    if minimum.isnumeric():
                        minimum: int = int(minimum)
                    elif minimum.replace('.', '', 1).isdigit():
                        minimum: float = float(minimum)

                    if maximum.isnumeric():
                        maximum: int = int(maximum)
                    elif maximum.replace('.', '', 1).isdigit():
                        maximum: float = float(maximum)
                    tmp_result['occurrences'] = [minimum, maximum]
            else:
                abort(500)
        result[vertex_value['name'].as_string()] = tmp_result

    return result
