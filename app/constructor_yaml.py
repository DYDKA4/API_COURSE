from nebula_communication import communication_with_nebula as cwn
import itertools
import yaml
import ast


def deep_update_dict(source, overrides):
    assert isinstance(source, dict)
    assert isinstance(overrides, dict)

    for k, v in overrides.items():
        if isinstance(v, dict) and isinstance(source.get(k), dict):
            source[k] = deep_update_dict(source.get(k, {}), v)
        elif isinstance(v, (list, set, tuple)) and isinstance(source.get(k), type(v)):
            type_save = type(v)
            source[k] = type_save(itertools.chain(iter(source[k]), iter(v)))
        else:
            source[k] = v
    return source


def form_properties(list_of_properties, definition_flag=False, name_in_edge=False, source_vid=None, flag_array=False):
    if flag_array:
        properties = []
    else:
        properties = {}
    for properties_vid in list_of_properties:
        properties_vid = properties_vid.as_string()
        if definition_flag:
            vertex_type = 'DefinitionProperties'
            edge_type = 'definition_property'
        else:
            vertex_type = 'AssignmentProperties'
            edge_type = 'assignment_property'
        value_name = cwn.fetch_vertex(None, f'"{properties_vid}"', vertex_type,
                                      'value_name', start_session=True)
        values = cwn.fetch_vertex(None, f'"{properties_vid}"', vertex_type,
                                  'values', start_session=True)
        try:
            values = ast.literal_eval(values)
        except ValueError:
            pass
        except SyntaxError:
            pass

        if name_in_edge:
            name = cwn.fetch_edge(None, f'"{source_vid}"', f'"{properties_vid}"', edge_type, 'name',
                                  start_session=True)
            if flag_array:
                properties.append({name: {value_name: values}})
            else:
                deep_update_dict(properties, {name: {value_name: values}})
        else:
            if flag_array:
                properties.append({value_name: values})
            else:
                deep_update_dict(properties, {value_name: values})
    properties = {'properties': properties}
    return properties


def form_capabilities(list_of_capability, definition_flag=False, name_in_edge=False,
                      source_vid=None, flag_form_properties=True):
    capabilities = {}
    for capabilities_vid in list_of_capability:
        capabilities_vid = capabilities_vid.as_string()
        if definition_flag:
            vertex_type = 'DefinitionCapabilities'
            edge_type = 'definition_capability'
            property_edge = 'definition_property'
            column = 'vertex_type_tosca'
        else:
            vertex_type = 'AssignmentCapabilities'
            edge_type = 'assignment_capability'
            property_edge = 'assignment_property'
            column = 'name'
        capabilities_name = cwn.fetch_vertex(None, f'"{capabilities_vid}"', vertex_type,
                                             column, start_session=True)
        if name_in_edge:
            name = cwn.fetch_edge(None, f'"{source_vid}"', f'"{capabilities_vid}"', edge_type, 'name',
                                  start_session=True)
            deep_update_dict(capabilities, {name: {'type': capabilities_name}})

        elif flag_form_properties:
            capabilities_property_list = cwn.find_destination(None, f'"{capabilities_vid}"',
                                                              property_edge, start_session=True,
                                                              full_list=True)
            capabilities_property = form_properties(capabilities_property_list)
            capabilities = deep_update_dict(capabilities, {capabilities_name: capabilities_property})
        else:
            print(capabilities_name)
            capabilities = deep_update_dict(capabilities, capabilities_name)
    if capabilities:
        capabilities = {'capabilities': capabilities}
    else:
        return {}
    return capabilities


def form_requirements(list_of_requirements, definition_flag=False):
    list_of_requirements_ready = []
    if definition_flag:
        vertex_type = 'DefinitionVertex'
        column = 'vertex_type_tosca'
        relationship = 'RelationshipType'
    else:
        vertex_type = 'AssignmentVertex'
        column = 'name'
        relationship = 'RelationshipTemplate'
    for requirement_vid in list_of_requirements:
        requirement_vid = requirement_vid.as_string()
        requirement_name = cwn.fetch_vertex(None, f'"{requirement_vid}"', 'RequirementsVertex',
                                            'name', start_session=True)
        requirement_destination = cwn.find_destination(None, f'"{requirement_vid}"',
                                                       'requirements_destination', start_session=True)
        if requirement_destination:
            destination_name = cwn.fetch_vertex(None, f'"{requirement_destination}"', vertex_type,
                                                column, start_session=True)
        node_filter = cwn.find_destination(None, f'"{requirement_vid}"', 'node_filter', start_session=True)
        if node_filter:
            print(node_filter)
            node_filter_properties = cwn.find_destination(None, f'"{node_filter}"',
                                                          'assignment_property', start_session=True, full_list=True)
            node_filter = form_properties(node_filter_properties, flag_array=True)
        occurrences = cwn.fetch_vertex(None, f'"{requirement_vid}"', 'RequirementsVertex',
                                       'occurrences', start_session=True)
        if occurrences:
            occurrences = ast.literal_eval(occurrences)

        requirement_capability = cwn.find_destination(None, f'"{requirement_vid}"',
                                                      'requirements_capability', start_session=True)
        requirement_capability_name = None
        print(requirement_capability)
        if requirement_capability:
            requirement_capability_name = cwn.fetch_vertex(None, f'"{requirement_capability}"',
                                                           'DefinitionCapabilities',
                                                           column, start_session=True)
        requirement_template = cwn.find_destination(None, f'"{requirement_vid}"',
                                                    'requirements', start_session=True)
        template_name = cwn.fetch_vertex(None, f'"{requirement_template}"', relationship,
                                         column, start_session=True)
        requirement = {}
        if node_filter:
            deep_update_dict(requirement, {'node_filter': node_filter})
        if requirement_destination:
            deep_update_dict(requirement, {requirement_name: {'node': destination_name}})
        if template_name:
            deep_update_dict(requirement, {requirement_name: {'relationship': template_name}})
        if requirement_capability:
            deep_update_dict(requirement[requirement_name], {'capability': requirement_capability_name})
        if occurrences:
            deep_update_dict(requirement[requirement_name], {'occurrences': occurrences})
        list_of_requirements_ready.append(requirement)

    list_of_requirements_ready = {'requirements': list_of_requirements_ready}
    return list_of_requirements_ready


def form_assignment_vertex(vid):
    name = cwn.fetch_vertex(None, f'"{vid}"', 'AssignmentVertex', 'name', start_session=True)
    type_of_vertex = cwn.fetch_vertex(None, f'"{vid}"', 'AssignmentVertex', 'type', start_session=True)
    node_template = {name: {'type': type_of_vertex}}
    list_of_properties = cwn.find_destination(None, f'"{vid}"',
                                              'assignment_property', start_session=True, full_list=True)
    list_of_capability = cwn.find_destination(None, f'"{vid}"',
                                              'assignment_capability', start_session=True, full_list=True)
    list_of_requirements = cwn.find_destination(None, f'"{vid}"',
                                                'requirements', start_session=True, full_list=True)
    list_of_requirements_ready = form_requirements(list_of_requirements)
    if list_of_requirements_ready.get('requirements'):
        deep_update_dict(node_template[name], list_of_requirements_ready)
    capabilities = form_capabilities(list_of_capability)
    if capabilities.get('capabilities'):
        deep_update_dict(node_template[name], capabilities)
    properties = form_properties(list_of_properties)
    if properties.get('properties'):
        deep_update_dict(node_template[name], properties)

    return node_template


def form_relationship_template(vid):
    name = cwn.fetch_vertex(None, f'"{vid}"', 'RelationshipTemplate', 'name', start_session=True)
    type_relationship_vid = cwn.find_destination(None, f'"{vid}"', 'type_relationship', start_session=True)
    type_relationship_name = cwn.fetch_vertex(None, f'"{type_relationship_vid}"',
                                              'RelationshipType', 'vertex_type_tosca', start_session=True)
    list_of_properties = cwn.find_destination(None, f'"{vid}"',
                                              'definition_property', start_session=True, full_list=True)
    properties = form_properties(list_of_properties, definition_flag=True)
    relationship_template = {name: {'type': type_relationship_name}}
    if properties.get('properties'):
        deep_update_dict(relationship_template[name], properties)
    return relationship_template


def form_definition_vertex(vid):
    nodes_template_definition = {}
    vertex_type_tosca = cwn.fetch_vertex(None, f'"{vid}"', 'DefinitionVertex',
                                         'vertex_type_tosca', start_session=True)
    list_of_properties = cwn.find_destination(None, f'"{vid}"',
                                              'definition_property', start_session=True, full_list=True)
    list_of_capability = cwn.find_destination(None, f'"{vid}"',
                                              'definition_capability', start_session=True, full_list=True)
    list_of_requirements = cwn.find_destination(None, f'"{vid}"',
                                                'requirements', start_session=True, full_list=True)
    list_of_interfaces = cwn.find_destination(None, f'"{vid}"',
                                              'definition_interface', start_session=True, full_list=True)
    derived_from_vid = cwn.find_destination(None, f'"{vid}"',
                                            'derived_from', start_session=True)
    properties = form_properties(list_of_properties, definition_flag=True, name_in_edge=True, source_vid=vid)
    capabilities = form_capabilities(list_of_capability, definition_flag=True, name_in_edge=True,
                                     source_vid=vid)
    list_of_requirements_ready = form_requirements(list_of_requirements, definition_flag=True)

    interface = {}
    if list_of_interfaces:
        for list_of_interfaces_vid in list_of_interfaces:
            list_of_interfaces_vid = list_of_interfaces_vid.as_string()
            name_of_interface = cwn.fetch_vertex(None, f'"{list_of_interfaces_vid}"', 'DefinitionInterface',
                                                 'vertex_type_tosca', start_session=True)
            name_of_edge = cwn.fetch_edge(None, f'"{vid}"', f'"{list_of_interfaces_vid}"',
                                          'definition_interface',
                                          'name', start_session=True)
            deep_update_dict(interface, {name_of_edge: {'type': name_of_interface}})
    node_template = vertex_type_tosca
    if derived_from_vid:
        derived_from = cwn.fetch_vertex(None, f'"{derived_from_vid}"',
                                        'DefinitionVertex', 'vertex_type_tosca', start_session=True)
        deep_update_dict(nodes_template_definition, {node_template: {'derived_from': derived_from}})
    if capabilities.get('capabilities'):
        deep_update_dict(nodes_template_definition, {node_template: capabilities})
    if properties.get('properties'):
        deep_update_dict(nodes_template_definition, {node_template: properties})
    if list_of_requirements_ready.get('requirements'):
        deep_update_dict(nodes_template_definition, {node_template: list_of_requirements_ready})
    if interface:
        interface = {'interfaces': interface}
        deep_update_dict(nodes_template_definition, {node_template: interface})
    if not (capabilities.get('capabilities') or properties.get('properties') or
            list_of_requirements_ready.get('requirements') or interface or derived_from_vid):
        deep_update_dict(nodes_template_definition, {node_template: 'None'})
    return nodes_template_definition


def form_capabilities_definition(vid):
    capabilities_definition = {}
    vertex_type_tosca = cwn.fetch_vertex(None, f'"{vid}"', 'DefinitionCapabilities',
                                         'vertex_type_tosca', start_session=True)
    list_of_properties = cwn.find_destination(None, f'"{vid}"',
                                              'definition_property', start_session=True, full_list=True)
    properties = form_properties(list_of_properties, definition_flag=True, name_in_edge=True, source_vid=vid)
    derived_from_vid = cwn.find_destination(None, f'"{vid}"',
                                            'derived_from', start_session=True)
    if derived_from_vid:
        derived_from = cwn.fetch_vertex(None, f'"{derived_from_vid}"',
                                        'DefinitionCapabilities', 'vertex_type_tosca', start_session=True)
        deep_update_dict(capabilities_definition, {vertex_type_tosca: {'derived_from': derived_from}})
    if properties.get('properties'):
        deep_update_dict(capabilities_definition, {vertex_type_tosca: properties})
    if not (derived_from_vid or properties.get('properties')):
        deep_update_dict(capabilities_definition, {vertex_type_tosca: 'None'})
    return capabilities_definition


def form_definition_interface(vid):
    interfaces_definition = {}
    vertex_type_tosca = cwn.fetch_vertex(None, f'"{vid}"', 'DefinitionInterface',
                                         'vertex_type_tosca', start_session=True)
    list_of_properties = cwn.find_destination(None, f'"{vid}"',
                                              'definition_property', start_session=True, full_list=True)
    properties = form_properties(list_of_properties, definition_flag=True, name_in_edge=True, source_vid=vid)
    for i, item in properties.get('properties').items():
        properties.get('properties')[i] = item['Function']
    derived_from_vid = cwn.find_destination(None, f'"{vid}"',
                                            'derived_from', start_session=True)
    if derived_from_vid:
        derived_from = cwn.fetch_vertex(None, f'"{derived_from_vid}"',
                                        'DefinitionInterface', 'vertex_type_tosca', start_session=True)
        deep_update_dict(interfaces_definition, {vertex_type_tosca: {'derived_from': derived_from}})
    if properties.get('properties'):
        deep_update_dict(interfaces_definition, {vertex_type_tosca: properties['properties']})
    if not (derived_from_vid or properties.get('properties')):
        deep_update_dict(interfaces_definition, {vertex_type_tosca: 'None'})
    return interfaces_definition


def form_definition_relationship_type(vid):
    relationship_type_definition = {}
    vertex_type_tosca = cwn.fetch_vertex(None, f'"{vid}"', 'RelationshipType',
                                         'vertex_type_tosca', start_session=True)
    list_of_properties = cwn.find_destination(None, f'"{vid}"',
                                              'definition_property', start_session=True, full_list=True)
    valid_target_types = cwn.find_destination(None, f'"{vid}"',
                                              'valid_target_types', start_session=True, full_list=True)
    valid_target_type_list = []
    for valid_target_type in valid_target_types:
        valid_target_type = valid_target_type.as_string()
        valid_target_type_name = cwn.fetch_vertex(None, f'"{valid_target_type}"', 'DefinitionCapabilities',
                                                  'vertex_type_tosca', start_session=True)
        valid_target_type_list.append(valid_target_type_name)
    properties = form_properties(list_of_properties, definition_flag=True, name_in_edge=True, source_vid=vid)
    derived_from_vid = cwn.find_destination(None, f'"{vid}"',
                                            'derived_from', start_session=True)
    if derived_from_vid:
        derived_from = cwn.fetch_vertex(None, f'"{derived_from_vid}"',
                                        'RelationshipType', 'vertex_type_tosca', start_session=True)
        deep_update_dict(relationship_type_definition, {vertex_type_tosca: {'derived_from': derived_from}})
    if valid_target_type_list:
        deep_update_dict(relationship_type_definition,
                         {vertex_type_tosca: {'valid_target_types': valid_target_type_list}})
    if properties.get('properties'):
        deep_update_dict(relationship_type_definition, {vertex_type_tosca: properties})
    if not (derived_from_vid or properties.get('properties')):
        deep_update_dict(relationship_type_definition, {vertex_type_tosca: 'None'})
    return relationship_type_definition


def form_output_template(vid):
    output_value = cwn.fetch_vertex(None, f'"{vid}"', 'output',
                                    'values', start_session=True)
    output_description = cwn.fetch_vertex(None, f'"{vid}"', 'output',
                                          'description', start_session=True)
    output_name = cwn.fetch_vertex(None, f'"{vid}"', 'output',
                                   'name', start_session=True)
    if output_value:
        try:
            output_value = ast.literal_eval(output_value)

        except ValueError:
            pass
        except SyntaxError:
            pass
    output_template = {output_name: {'value': output_value}}

    if output_description:
        deep_update_dict(output_template[output_name], {'description': output_description})
    return output_template


def form_inputs_template(vid):
    inputs_name = cwn.fetch_vertex(None, f'"{vid}"', 'inputs',
                                   'name', start_session=True)
    properties_list = cwn.find_destination(None, f'"{vid}"',
                                           'assignment_property', start_session=True, full_list=True)
    properties = form_properties(properties_list)
    inputs_template = {}
    if properties:
        properties = properties.get('properties')
        inputs_template = {inputs_name: properties}

    return inputs_template


def get_yaml(cluster_name):
    """
    ?????????????????? defention ??????????
    :return:
    """
    nodes_template_assignment = {}
    nodes_template_definition = {}
    capabilities_definition = {}
    relationship_templates = {}
    output_templates = {}
    inputs_templates = {}
    interfaces_definition = {}
    relationship_type_definition = {}
    assignment = cwn.find_destination(None, f'"{cluster_name}"', 'assignment', start_session=True, full_list=True)
    for vid in assignment:
        vid = vid.as_string()
        if 'AssignmentVertex' in vid:
            node_template = form_assignment_vertex(vid)
            deep_update_dict(nodes_template_assignment, node_template)

        elif 'RelationshipTemplate' in vid:
            relationship_template = form_relationship_template(vid)
            deep_update_dict(relationship_templates, relationship_template)
        elif 'output' in vid:
            output = form_output_template(vid)
            deep_update_dict(output_templates, output)
        elif 'inputs' in vid:
            inputs = form_inputs_template(vid)
            deep_update_dict(inputs_templates, inputs)
        else:
            return None
    definition = cwn.find_destination(None, f'"{cluster_name}"', 'definition', start_session=True, full_list=True)
    for vid in definition:
        vid = vid.as_string()
        if 'DefinitionVertex' in vid:
            deep_update_dict(nodes_template_definition, form_definition_vertex(vid))
        if 'DefinitionCapabilities' in vid:
            deep_update_dict(capabilities_definition, form_capabilities_definition(vid))
        if 'DefinitionInterface' in vid:
            deep_update_dict(interfaces_definition, form_definition_interface(vid))
        if 'RelationshipType' in vid:
            deep_update_dict(relationship_type_definition, form_definition_relationship_type(vid))
    if nodes_template_definition:
        nodes_template_definition = {'node_types': nodes_template_definition}
    if nodes_template_assignment:
        nodes_template_assignment = {'node_templates': nodes_template_assignment}
    if relationship_templates:
        relationship_templates = {'relationship_templates': relationship_templates}
        deep_update_dict(nodes_template_assignment, relationship_templates)
    if output_templates:
        output_templates = {'outputs': output_templates}
        deep_update_dict(nodes_template_assignment, output_templates)
    if inputs_templates:
        inputs_templates = {'inputs': inputs_templates}
        deep_update_dict(nodes_template_assignment, inputs_templates)
    template = nodes_template_definition
    if relationship_type_definition:
        deep_update_dict(template, {'relationship_types': relationship_type_definition})
    if interfaces_definition:
        deep_update_dict(template, {'interface_types': interfaces_definition})
    if capabilities_definition:
        deep_update_dict(template, {'capability_types': capabilities_definition})
    deep_update_dict(template, {'topology_template': nodes_template_assignment})
    with open('./output.yaml', 'w') as file:
        documents = yaml.dump(template, file)
    return template


def separated_vertex(vid):
    template = {}
    # Assignment_vertex
    if 'AssignmentVertex' in vid:
        template = form_assignment_vertex(vid)
    elif 'RelationshipTemplate' in vid:
        template = form_relationship_template(vid)
    elif 'DefinitionVertex' in vid:
        template = form_definition_vertex(vid)
    elif 'DefinitionCapabilities' in vid:
        template = form_capabilities_definition(vid)
    elif 'DefinitionInterface' in vid:
        template = form_definition_interface(vid)
    elif 'RelationshipType' in vid:
        template = form_definition_relationship_type(vid)
    elif 'output' in vid:
        template = form_output_template(vid)
    else:
        pass
    return template
