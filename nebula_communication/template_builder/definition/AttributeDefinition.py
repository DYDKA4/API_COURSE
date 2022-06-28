from werkzeug.exceptions import abort

from nebula_communication.nebula_functions import fetch_vertex, find_destination
from nebula_communication.template_builder.definition.SchemaDefinition import construct_schema_definition
from parser.parser.tosca_v_1_3.definitions.AttributeDefinition import AttributeDefinition


def construct_attribute_definition(list_of_vid) -> dict:
    result = {}

    property_definition = AttributeDefinition('name').__dict__

    for vid in list_of_vid:
        vertex_value = fetch_vertex(vid, 'AttributeDefinition')
        vertex_value = vertex_value.as_map()
        tmp_result = {}
        vertex_keys = vertex_value.keys()
        for vertex_key in vertex_value.keys():
            if not vertex_value[vertex_key].is_null() and vertex_key not in {'vertex_type_system', 'name'}:
                tmp_result[vertex_key] = vertex_value[vertex_key].as_string()
        edges = set(property_definition.keys()) - set(vertex_keys) - {'vid'}
        for edge in edges:
            destination = find_destination(vid, edge)
            if edge == 'entry_schema':
                tmp_result['entry_schema'] = construct_schema_definition(destination)
            elif edge == 'key_schema':
                tmp_result['key_schema'] = construct_schema_definition(destination)
            elif edge == 'type':
                data_type = fetch_vertex(destination[0], 'DataType')
                data_type = data_type.as_map()
                data_type = data_type['name'].as_string()
                tmp_result['type'] = data_type
            else:
                abort(500)
        result[vertex_value['name'].as_string()] = tmp_result
    return result
