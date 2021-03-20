# https://github.com/openstack/rally/blob/7153e0cbc5b0e6433313a3bc6051b2c0775d3804/rally/common/plugin/info.py#L63-L110

import os
import re
import sys

PARAM_OR_RETURNS_REGEX = re.compile(":(?:param|return)")
RETURNS_REGEX = re.compile(":return: (?P<doc>.*)", re.S)
PARAM_REGEX = re.compile(":param (?P<name>[\*\w]+): (?P<doc>.*?)"
                         "(?:(?=:param)|(?=:return)|(?=:raises)|\Z)", re.S)


def trim(docstring):
    """trim function from PEP-257"""
    if not docstring:
        return ""
    # Convert tabs to spaces (following the normal Python rules)
    # and split into a list of lines:
    lines = docstring.expandtabs().splitlines()
    # Determine minimum indentation (first line doesn't count):
    indent = sys.maxsize
    for line in lines[1:]:
        stripped = line.lstrip()
        if stripped:
            indent = min(indent, len(line) - len(stripped))
    # Remove indentation (first line is special):
    trimmed = [lines[0].strip()]
    if indent < sys.maxsize:
        for line in lines[1:]:
            trimmed.append(line[indent:].rstrip())
    # Strip off trailing and leading blank lines:
    while trimmed and not trimmed[-1]:
        trimmed.pop()
    while trimmed and not trimmed[0]:
        trimmed.pop(0)

    # Current code/unittests expects a line return at
    # end of multiline docstrings
    # workaround expected behavior from unittests
    if "\n" in docstring:
        trimmed.append("")

    # Return a single string:
    return "\n".join(trimmed)


def reindent(string):
    """
    Add the same tab size for each line in a block of lines
    :param string: String, Line to apply the format. Ie, 
        "
            This is a block
                of lines with
          different tabs
        "
    :return: String, Line with format. Ie, 
        "
            This is a block
            of lines with
            different tabs
        "
    """
    return "\n".join(l.strip() for l in string.strip().split("\n"))


def clean_multiple_white_spaces(string):
    """
    Merge multiple white spaces in only one
    :param string: String, Line to apply the format. Ie, "   some    string with   spaces"
    :return: String, Line with format. Ie, " some string with spaces"
    """
    return ' '.join(string.split())


def pre_process(docstring):
    """Parse the docstring into its components.
    :return: a dictionary with format
              {
                  "short_description": ...,
                  "long_description": ...,
                  "params": [{"name": ..., "doc": ..., "example": ..., "type": ...}, ...],
                  "returns": ...
              }
    """
    processed_text = []

    if docstring:
        # Replace
        docstring = docstring.replace("'", "\"")

        trim_text = trim(docstring)
        text_splitted = trim_text.split('\n')
        new_line = ""

        for line in text_splitted:
            if not line or ':param' in line or ':return' in line:
                processed_text.append(new_line)
                new_line = ""

            new_line += line + " "

    return "\n".join(processed_text)


def parse_docstring(docstring):
    """
    Parse the docstring into its components.
    :parmam docstring: String, docstring content
    :return: a dictionary of form. Ie,
        {
            "short_description": ...,
            "long_description": ...,
            "params": [{"name": ..., "doc": ..., "example": ..., "type": ...}, ...],
            "returns": ...
        }
    """

    short_description = long_description = returns = ""
    params_type_list = ['String', 'string', 'Str', 'str',
                        'Integer', 'integer', 'Int', 'int',
                        'Boolean, boolean, Bool, bool',
                        'Dict', 'dict', 'Dictionary', 'dictionary',
                        'List', 'list', 'Lst', 'lst',
                        'JSON', 'Json', 'json']
    params = []

    if docstring:
        docstring = pre_process(trim(docstring))

        lines = docstring.split("\n", 1)
        short_description = lines[0]

        if len(lines) > 1:
            long_description = lines[1].strip()

            params_returns_desc = None

            match = PARAM_OR_RETURNS_REGEX.search(long_description)
            if match:
                long_desc_end = match.start()
                params_returns_desc = long_description[long_desc_end:].strip()
                long_description = long_description[:long_desc_end].rstrip()

            # Params
            if params_returns_desc:
                params = []

                for name, doc in PARAM_REGEX.findall(params_returns_desc):
                    example = ""

                    for word in ['Ie ', 'Ie.', 'Ie,', 'ie.', 'ie', 'IE.', 'IE']:
                        if word in doc:
                            doc = doc.replace(word, 'Ie,')
                            doc, example = doc.split('Ie,')
                            example = example.replace(
                                '\n', '')  # Clean end of line
                            example = clean_multiple_white_spaces(
                                example)  # Clean multiple white spaces
                            example = example.replace('...', '')
                            break

                    doc = doc.replace('\n', '')

                    # Define params type
                    param_type = doc.split(' ', 1)[0]

                    for char in ['.', ',']:
                        if char in param_type:
                            param_type = param_type.replace(char, '')

                    if param_type in params_type_list:
                        doc = ' '.join(doc.split(' ')[1:])
                    else:
                        param_type = ''

                    params.append({"name": name, "doc": trim(
                        doc), "example": example, "type": param_type})

                # Return
                match = RETURNS_REGEX.search(params_returns_desc)
                if match:
                    returns = reindent(match.group("doc"))
                    return_doc = ''
                    return_example = ''

                    for word in ['Ie ', 'Ie.', 'Ie,', 'ie.', 'ie', 'IE.', 'IE']:
                        if word in returns:
                            returns = returns.replace(word, 'Ie,')
                            return_doc, return_example = returns.split('Ie,')
                            return_example = return_example.replace(
                                '\n', '')  # Clean end of line
                            return_example = clean_multiple_white_spaces(
                                return_example)  # Clean multiple white spaces
                            return_example = return_example.replace('...', '')
                            break

                    # Define return type
                    return_type = return_doc.split(' ', 1)[0]

                    for char in ['.', ',']:
                        if char in return_type:
                            return_type = return_type.replace(char, '')

                    if return_type in params_type_list:
                        return_doc = ' '.join(return_doc.split(' ')[1:])
                    else:
                        return_type = ''

                    returns = {"doc": trim(return_doc),
                               "example": return_example, "type": return_type}

    return {
        "short_description": short_description,
        "long_description": long_description,
        "params": params,
        "returns": returns
    }


def add_tabs_to_yaml(yaml_string, tab_size):
    """
    Add tabs for each line in a block of strings
    :param yaml_string: String, text with yaml format. Ie, 
        "
        Create lead owners and create lead guarantors person if the client has the property active
        ---
        parameters:
         - name: client_id
           in: path
           description: Client identifier.
           required: true
           type: int
           default: 3
        "
    :param tab_size: Integer, Tab size. Ie, 1
    :return: String, text yaml with tab size added. Ie, 
        "
            Create lead owners and create lead guarantors person if the client has the property active
            ---
            parameters:
            - name: client_id
            in: path
            description: Client identifier.
            required: true
            type: int
            default: 3
        "
    """
    tab = '    ' * tab_size

    yaml_string = yaml_string.replace('***', tab)
    return yaml_string


def docstring_to_yaml(docstring_dict, tab_size=1):
    """
    Transform a docstring in yaml format
    :param docstring_dict: Dict, Docstring Ie,
        {
            "short_description": ...,
            "long_description": ...,
            "params": [{"name": ..., "doc": ..., "example": ..., "type": ...}, ...],
            "returns": ...
        }
    :param tab_size: Integer, Tab size. Ie, 1
    :return String, docstring in yaml format Ie,
        "
        Create lead owners and create lead guarantors person if the client has the property active 
        ---
        parameters:
        - name: client_id
           in: path 
           description: Client identifier.
           required: true
           type: int
           default: 3
        "
    """
    parameters_yaml = ''
    responses_yaml = ''
    yaml = ''
    is_params_enabled = 'params' in docstring_dict and docstring_dict['params']
    is_returns_enabled = 'returns' in docstring_dict and docstring_dict['returns']

    if 'short_description' in docstring_dict and docstring_dict[
            'short_description']:
        yaml += '***' + docstring_dict['short_description']

    if 'long_description' in docstring_dict and docstring_dict[
            'long_description']:
        yaml += '\n***' + docstring_dict['long_description']

    if is_params_enabled or is_returns_enabled:
        yaml += '\n***---'

    if is_params_enabled:
        params = docstring_dict['params']
        parameters_yaml = '***parameters:'

        for param in params:
            # Name
            if 'name' in param and param['name']:
                parameters_yaml += '\n***  - name: ' + param['name']
            # Origin
            parameters_yaml += '\n***    in: path '
            # Description
            if 'doc' in param and param['doc']:
                parameters_yaml += '\n***    description: ' + \
                    param['doc']
            # Required?
            parameters_yaml += '\n***    required: true'
            # Type
            if 'type' in param and param['type']:
                parameters_yaml += '\n***    type: ' + param['type']
            # Example
            if 'example' in param and param['example']:
                parameters_yaml += '\n***    default: ' + \
                    param['example']

        yaml += '\n' + parameters_yaml

    if is_returns_enabled:
        returns = docstring_dict['returns']
        responses_yaml = '***responses:\n***  200:'

        if 'doc' in returns and returns['doc']:
            responses_yaml += '\n***    description: ' + returns['doc']

        if 'example' in returns and returns['example']:
            responses_yaml += '\n***    example: ' + returns['example']

        if 'type' in returns and returns['type']:
            responses_yaml += '\n***    type: ' + returns['type']

        yaml += '\n' + responses_yaml
    yaml += '\n'

    return add_tabs_to_yaml(yaml, tab_size)