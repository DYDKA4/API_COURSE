from werkzeug.exceptions import abort

from nebula_communication.generate_uuid import generate_uuid
from nebula_communication.nebula_functions import fetch_vertex, update_vertex, find_destination, delete_vertex, \
    add_in_vertex, add_edge
from parser.parser.tosca_v_1_3.assignments.AttributeAssignment import AttributeAssignment


def update_attribute_assignment(service_template_vid, father_node_vid, value, value_name, varargs: list, type_update):
    if len(varargs) != 2:
        abort(400)
    destination = find_destination(father_node_vid, varargs[0])
    if destination is None:
        abort(400)
    property_vid_to_update = None
    for property_vid in destination:
        property_value = fetch_vertex(property_vid, 'AttributeAssignment')
        property_value = property_value.as_map()
        if property_value.get('name').as_string() == varargs[1]:
            property_vid_to_update = property_vid
            break
    if property_vid_to_update is None:
        abort(400)
    if type_update == 'delete':
        delete_vertex('"' + property_vid_to_update.as_string() + '"')
        return
    if value_name == 'value':
        value_name = 'values'
    property_value = fetch_vertex(property_vid_to_update, 'AttributeAssignment')
    property_value = property_value.as_map()
    if value_name in property_value.keys():
        update_vertex('PropertyAssignment', property_vid_to_update, value_name, value)
    else:
        abort(400)


def add_attribute_assignment(type_update, varargs, cluster_name, parent_vid, edge_name):
    if type_update == 'add' and len(varargs) == 2:
        data_type = AttributeAssignment('"' + varargs[1] + '"')
        generate_uuid(data_type, cluster_name)
        add_in_vertex(data_type.vertex_type_system, 'name, vertex_type_system',
                      data_type.name + ',"' + data_type.vertex_type_system + '"', data_type.vid)
        add_edge(edge_name, '', parent_vid, data_type.vid, '')
        return True
    return False
