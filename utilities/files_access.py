import json


def load_template(filename):
    with open(filename, 'r') as file:
        template = json.load(file)
    return template


def modify_template(template, namespace_name):
    modified_template = template.copy()
    modified_template['metadata']['name'] = namespace_name
    return modified_template
