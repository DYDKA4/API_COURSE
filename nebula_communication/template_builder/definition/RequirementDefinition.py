from werkzeug.exceptions import abort

from nebula_communication.nebula_functions import fetch_vertex, find_destination
from nebula_communication.template_builder.definition.InterfaceDefinition import construct_interface_definition
from parser.parser.tosca_v_1_3.definitions.RequirementDefinition import RequirementDefinition


def construct_requirement_definition(list_of_vid) -> list:
    result = []
    requirement_definition = RequirementDefinition('name').__dict__

    for vid in list_of_vid:
        vertex_value = fetch_vertex(vid, 'RequirementDefinition')
        vertex_value = vertex_value.as_map()
        tmp_result = {}
        vertex_keys = vertex_value.keys()
        for vertex_key in vertex_keys:
            if not vertex_value[vertex_key].is_null() and vertex_key not in {'vertex_type_system', 'name'}:
                tmp_result[vertex_key] = vertex_value[vertex_key].as_string()
        edges = set(requirement_definition.keys()) - set(vertex_keys) - {'vid'}
        for edge in edges:
            destination = find_destination(vid, edge)
            if edge == 'capability':
                capability = fetch_vertex(destination[0], 'CapabilityType')
                capability = capability.as_map()
                capability = capability['name'].as_string()
                tmp_result['capability'] = capability
            elif edge == 'node':
                if destination:
                    node = fetch_vertex(destination[0], 'NodeType')
                    node = node.as_map()
                    node = node['name'].as_string()
                    tmp_result['node'] = node
            elif edge == 'relationship':
                if destination:
                    relationship = fetch_vertex(destination[0], 'RelationshipType')
                    relationship = relationship.as_map()
                    relationship = relationship['name'].as_string()
                    tmp_result['node'] = relationship
                    if tmp_result.get('relationship'):
                        tmp_result['relationship'] += {'type': relationship}
                    else:
                        tmp_result['relationship'] = {'type': relationship}
            elif edge == 'interfaces':
                interfaces = construct_interface_definition(destination)
                if tmp_result.get('relationship'):
                    tmp_result['relationship'] += {'interfaces': interfaces}
                else:
                    tmp_result['relationship'] = {'interfaces': interfaces}
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
                print(edge)
                abort(500)
        requirement = {vertex_value['name'].as_string():  tmp_result}
        result.append(requirement)

    return result
