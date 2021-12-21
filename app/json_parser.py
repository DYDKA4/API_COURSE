import dpath.util

list_of_relationship_type = [
    'DependsOn',
    'HostedOn',
    'ConnectsTo',
    'AttachesTo',
    'RoutesTo',
    'binding',
    'link'
]


def paths(some_dict, path=()):
    for key, value in some_dict.items():
        key_path = path + (key,)
        yield key_path
        if hasattr(value, 'items'):
            yield from paths(value, key_path)


# первое что надо найти где расположена часть с ключём node_templates
def find_node_templates(data):
    node_template = dpath.util.get(data, "topology_template/node_templates")
    return node_template


def separation(data):
    return data.split('.', -1)[-1]


def node_requirements(data, source):
    data = data.get('requirements')
    if data:
        data = data[0]  # пока не понятно когда список размера не 1
        depends = dpath.util.get(data, 'local_storage/node')
        type_of_depends = dpath.util.get(data, 'local_storage/relationship')
        if type(type_of_depends) == dict:
            type_of_depends = type_of_depends.get('type')
        else:  # поиск кастомного типа отношений и поиск в нем типа зависимости
            type_of_depends = dpath.util.get(source, f'topology_template/relationship_templates/{type_of_depends}/type')
        if type_of_depends not in list_of_relationship_type:  # определние кастомного отношнеия к 7 стандартным
            type_of_depends = dpath.util.get(source, f'relationship_types/{type_of_depends}/derived_from')
            if type_of_depends not in list_of_relationship_type:
                type_of_depends = type_of_depends.split('.', -1)[-1]

        return [depends, type_of_depends]
    return data


def port_requirements(data, source):
    data = data.get('requirements')
    if data:  # сделано не очень, мне не нравится
        result = []
        for link in data:
            if link.get('link'):
                result += [[link.get('link'), 'link']]
            elif link.get('binding'):
                result += [[link.get('binding'), 'binding']]
            else:
                return None
        return result
    return data


def local_storage_parser(data):
    # print(data)
    data = data.get('local_storage')
    node = data.get('node')
    relationship = data.get('relationship')
    if type(relationship) == dict:
        return [node, relationship.get('type')]
    else:
        return [node, relationship]


def requirements_parser(data):
    result = []
    if type(data) == dict:
        print('DICT')
        print(data.items())
    elif type(data) == list:
        for link in data:
            if 'local_storage' in link.keys():
                return local_storage_parser(link)
            else:
                for key in link:
                    result += [[key, link.get(key)]]
        return result
    else:
        print('ELSE')
    return


def find_requirements(data, source, node_type):
    # if node_type == "Compute":
    #     return node_requirements(data, source)
    # if node_type == 'Port':
    #     return port_requirements(data, source)
    # print(*paths(data), sep='\n')
    res = data.get('requirements')
    if res:
        # print(data.get('requirements'), '\n')

        return requirements_parser(res)
    return


def parser(data):  # возвращает массив где каждый элдемент сожержимт в себе информаию: имя, тип узла, завимости.
    # print(json.dumps(data, indent=2))
    node_templates = find_node_templates(data)
    # print(node_templates)
    answer = []
    for name_of_node, params in node_templates.items():
        ans = []
        node_type = params.get('type')
        node_type = separation(node_type)  #  упрощение типа ноды
        requirements = find_requirements(params, data, node_type)
        ans += [name_of_node]
        ans += [node_type]
        if requirements:
            ans += [requirements]
        answer += [ans]
    return answer