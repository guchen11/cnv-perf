import json


def load_template(filename):
    with open(filename, 'r') as file:
        template = json.load(file)
    return template


def modify_template(template, namespace_name):
    modified_template = template.copy()
    modified_template['metadata']['name'] = namespace_name
    return modified_template


def update_json_value(filename, key, new_value):
    with open(filename, 'r+') as json_file:
        data = json.load(json_file)
        data[key] = new_value
        json_file.seek(0)  # Move the file pointer to the beginning
        json.dump(data, json_file, indent=4)
        json_file.truncate()  # Remove any extra content beyond the updated data


def get_json_value(filename, key):
    with open(filename, 'r') as json_file:
        data = json.load(json_file)
        value = data.get(key)  # Retrieve the value for the specified key
        return value
