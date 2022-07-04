import json

from werkzeug.exceptions import abort

from parser.linker.LinkByName import link_by_type_name
from parser.parser.tosca_v_1_3.assignments.CapabilityAssignment import CapabilityAssignment
from parser.parser.tosca_v_1_3.assignments.PropertyAssignment import PropertyAssignment
from parser.parser.tosca_v_1_3.assignments.RequirementAssignment import RequirementAssignment
from parser.parser.tosca_v_1_3.definitions.InterfaceDefinition import InterfaceDefinition
from parser.parser.tosca_v_1_3.definitions.ServiceTemplateDefinition import ServiceTemplateDefinition
from parser.parser.tosca_v_1_3.definitions.TemplateDefinition import TemplateDefinition
from parser.parser.tosca_v_1_3.others.NodeTemplate import NodeTemplate
from parser.parser.tosca_v_1_3.others.RelationshipTemplate import RelationshipTemplate


def set_get_property(property_assignment: PropertyAssignment, destination_property_assignment: PropertyAssignment):
    if property_assignment.vertex_type_system != 'PropertyAssignment':
        abort(400)
    property_assignment.get_property = {'get_property': [property_assignment,
                                                         destination_property_assignment]}
    property_assignment.value = json.dumps(property_assignment.value)
    return


def find_in_property_list(property_assignment: PropertyAssignment, destination_property_assignment_list: list,
                          value: str):
    for destination_property_assignment in destination_property_assignment_list:
        destination_property_assignment: PropertyAssignment
        if destination_property_assignment.name == value:
            print(destination_property_assignment.name, value)
            set_get_property(property_assignment, destination_property_assignment)
            return True
    return


def link_property_assignment(service_template: ServiceTemplateDefinition,
                             property_assignment: PropertyAssignment) -> None:
    template_definition: TemplateDefinition = service_template.topology_template
    if type(property_assignment.value) == dict:
        value = property_assignment.value
    else:
        return
    if value.get('get_property'):
        value = value.get('get_property')
    else:
        abort(501)
    target_name = ''
    if value[0] == 'SELF':
        abort(501)
    elif value[0] == 'SOURCE':
        abort(501)
    elif value[0] == 'TARGET':
        abort(501)
    elif value[0] == 'HOST':
        abort(501)
    else:
        target_name = value[0]
        value = value[1:]

    for relationship_template in template_definition.relationship_templates:
        relationship_template: RelationshipTemplate
        if relationship_template.name == target_name:
            if find_in_property_list(property_assignment, relationship_template.properties, value[0]):
                return
            if len(value) > 1:
                for interface in relationship_template.interfaces:
                    interface: InterfaceDefinition
                    if interface.name == value[0]:
                        if find_in_property_list(property_assignment, interface.inputs, value[1]):
                            return

    for node_template in template_definition.node_templates:
        node_template: NodeTemplate
        if node_template.name == target_name:
            if find_in_property_list(property_assignment, node_template.properties, value[0]):
                return
            if len(value) > 1:
                for interface in node_template.interfaces:
                    interface: InterfaceDefinition
                    if interface.name == value[0]:
                        if find_in_property_list(property_assignment, interface.inputs, value[1]):
                            return
                for requirement_assignment in node_template.requirements:
                    requirement_assignment: RequirementAssignment
                    if requirement_assignment.name == value[0]:
                        if find_in_property_list(property_assignment, requirement_assignment.properties, value[1]):
                            return
                for capability_assignment in node_template.capabilities:
                    capability_assignment: CapabilityAssignment
                    if capability_assignment.name == value[0]:
                        if find_in_property_list(property_assignment, capability_assignment.properties, value[1]):
                            return

    if type(property_assignment.value) == dict and property_assignment.get_property is None:
        property_assignment.value = json.dumps(property_assignment.value)
