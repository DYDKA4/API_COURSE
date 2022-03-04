from app import communication_with_nebula as cwn


class Vertex:
    def __init__(self, name, vertex_type_tosca):
        self.vid = None
        self.vertex_type_tosca = vertex_type_tosca
        self.vertex_type_system = 'Vertex'
        self.name = name
        self.requirements = {}  # хз как сделать лучше
        self.capabilities = []
        self.properties = []

    def generate_vid(self):
        if self.vertex_type_system is None:
            assert 0, 'vertex_type_system is None'
        else:
            self.vid = self.vertex_type_system + str(
                cwn.number_of_entities(cwn.chose_of_space(), self.vertex_type_system))

    def set_vid(self, session):
        identification = cwn.number_of_entities(session, self.vertex_type_system)
        self.vid = '"' + self.vertex_type_system + str(identification) + '"'

    def __str__(self):
        return f'{hex(id(self))}, {self.vid}, {self.vertex_type_tosca}, {self.vertex_type_system}, {self.name}, {self.requirements}, ' \
               f'{self.capabilities}, {self.properties}'

    def __repr__(self):
        return repr(vars(self))


class AssignmentVertex(Vertex):
    def __init__(self, name, vertex_type_tosca='AssignmentVertex'):
        super().__init__(name, vertex_type_tosca)
        self.vertex_type_system = 'AssignmentVertex'

    def add_requirements(self, obj, link_type):
        # проверка condition для дочерних классов
        self.requirements[obj] = link_type

    def add_capabilities(self, obj):
        self.capabilities.append(obj)

    def add_properties(self, obj):
        self.properties.append(obj)

    def __repr__(self):
        return hex(id(self))


class ClusterName(Vertex):
    def __init__(self, name, pure_yaml, list_of_definition_vertex, list_of_assignment_vertex, definition_capabilities,
                 interfaces_vertex, relationship_type):
        super().__init__(name, 'ClusterName')
        self.vid = '"' + name + '"'
        self.vertex_type_system = 'ClusterName'
        self.pure_yaml = pure_yaml
        self.definition_vertex = list_of_definition_vertex
        self.assignment_vertex = list_of_assignment_vertex
        self.definition_capabilities = definition_capabilities
        self.interfaces_vertex = interfaces_vertex
        self.relationship_type = relationship_type

    def __str__(self):
        return f'{hex(id(self))}, {self.vid}, {self.vertex_type_tosca}, {self.vertex_type_system}, {self.name}, {self.definition_vertex}, ' \
               f'{self.assignment_vertex}, {self.pure_yaml}'


class AssignmentCapabilities(Vertex):
    def __init__(self, name, vertex_type_tosca='AssignmentCapabilities'):
        super().__init__(name, vertex_type_tosca)
        self.vertex_type_system = 'AssignmentCapabilities'

    def add_properties(self, obj):
        self.properties.append(obj)

    def __str__(self):
        return f'{self.vid}, {self.vertex_type_tosca}, {self.vertex_type_system}, {self.name}, {self.requirements}, ' \
               f'{self.capabilities}, {self.properties}'


class AssignmentProperties(Vertex):
    def __init__(self, value_name, value, vertex_type_tosca='AssignmentProperties'):
        super().__init__('noname', vertex_type_tosca)
        self.value_name = value_name
        self.value = value
        self.vertex_type_system = 'AssignmentProperties'

    def __str__(self):
        return f'{self.vid}, {self.vertex_type_tosca}, {self.vertex_type_system}, {self.name}, {self.requirements}, ' \
               f'{self.capabilities}, {self.properties}'


class DefinitionCapabilities(Vertex):
    def __init__(self, vertex_type_tosca):
        super().__init__('noname', vertex_type_tosca)
        self.vertex_type_system = 'DefinitionCapabilities'
        self.derived_from = []

    def add_properties(self, obj):
        self.properties.append(obj)

    def add_derived_from(self, obj):
        self.derived_from.append(obj)

    def __repr__(self):
        return hex(id(self))


class DefinitionVertex(Vertex):
    def __init__(self, vertex_type_tosca):
        super().__init__('noname', vertex_type_tosca)
        self.vertex_type_system = 'DefinitionVertex'
        self.derived_from = []
        self.interfaces = {}

    def add_requirements(self, obj, link_type):
        # проверка condition для дочерних классов
        self.requirements[obj] = link_type

    def add_capabilities(self, obj):
        self.capabilities.append(obj)

    def add_properties(self, obj):
        self.properties.append(obj)

    def add_derived_from(self, obj):
        self.derived_from.append(obj)

    def add_interface(self, obj, link_type):
        self.interfaces[obj] = link_type

    def __repr__(self):
        return hex(id(self))


class DefinitionProperties(Vertex):
    def __init__(self, name, value_name, value, vertex_type_tosca='DefinitionProperties'):
        super().__init__(name, vertex_type_tosca)
        self.value_name = str(value_name)
        self.value = str(value)
        self.vertex_type_system = 'DefinitionProperties'

    def __str__(self):
        return f'{self.vid}, {self.vertex_type_tosca}, {self.vertex_type_system}, {self.name}, {self.requirements}, ' \
               f'{self.capabilities}, {self.properties}'


class DefinitionInterface(Vertex):
    def __init__(self, vertex_type_tosca):
        super().__init__('noname', vertex_type_tosca)
        self.derived_from = []
        self.vertex_type_system = 'DefinitionInterface'

    def add_derived_from(self, obj):
        self.derived_from.append(obj)


class RelationshipType(Vertex):
    def __init__(self, vertex_type_tosca):
        super().__init__('noname', vertex_type_tosca)
        self.derived_from = []
        self.vertex_type_system = 'RelationshipType'
        self.properties = []
        self.valid_target_types = []

    def add_derived_from(self, obj):
        self.derived_from.append(obj)

    def add_properties(self, obj):
        self.properties.append(obj)

    def add_valid_target_types(self, obj):
        self.valid_target_types.append(obj)
