def __generate_markdown_hugo_summary_start(dirname):
    return '{{< details summary="{d}" >}}'.replace("{d}", dirname)

def __generate_markdown_hugo_summary_end():
    return '{{< /details >}}'

def _generate_markdown_struct(unit):
    name = unit["name"]
    return f'## struct - {name}\n\n'

def _generate_markdown_union(unit):
    name = unit["name"]
    return f'## union - {name}\n\n'

def _generate_markdown_variable(unit, root, parent_refid):
    name = unit["name"]
    title = (
        f'## variable {name}' 
        if root["kind"] == "file" and parent_refid == None else 
        ""
    )
    linebreak = '---\n' if parent_refid == None else '\n'
    description = unit["description"]

    if root["kind"] != "file" or parent_refid == None:
        variable_definition = unit["variable_definition"]
    else:
        variable_definition = unit["variable_definition"].replace(
                unit["parent_name"] + "::", ""
        )

    return (
        f'{linebreak}'
        f'{title}\n'
        f'{description}\n'
        f'```c\n'
        f'{variable_definition}\n'
        f'```\n'
    )

def _generate_markdown_enum(unit):
    name = unit["name"]
    enums_formatted = ',\n\t'.join(unit["enum_values"])
    return (
        f'---                \n'
        f'## enum - {name}   \n'
        f'```c               \n'
        f'enum {name} {{     \n'
        f'\t{enums_formatted}\n'
        f'}}                 \n'
        f'```                \n'
        f'                   \n'
    )

def _generate_markdown_function_params(unit):
    params = ""

    if not unit:
        return params

    for param in unit:
        _type = param["type"]
        _name = param["name"]
        params += (
            f'-\t\n'
            f'  ```c           \n'
            f'  {_type} {_name}\n'
            f'  ```            \n'
        )

    return (
        f'### parameters\n\n'
        f'{params}\n'
    )

def _generate_markdown_function(unit):
    name = unit["name"]
    definition = unit["definition"]
    if unit["args"] != "()":
        args = "(" + ','.join([ x["type"] for x in unit["params"] ]) + ")"
        title_args = '...'
    else:
        args = "()"
        title_args = ''
    description = unit["description"]
    params_formatted = _generate_markdown_function_params(unit["params"])
    return_type = unit["return_type"]
    return_description = (
            unit["return_description"] 
            if unit["return_description"] is not None else 
            ""
    )
    
    return (
        f'---                                \n'
        f'## function - {name} ({title_args})\n'
        f'{description}                      \n'
        f'```c                               \n'
        f'{definition} {args}                \n'
        f'```                                \n'
        f'                                   \n'
        f'{params_formatted}                 \n'
        f'### returns                        \n'
        f'```c                               \n'
        f'{return_type}                      \n'
        f'```                                \n'
        f'{return_description}               \n'
        f'                                   \n'
    )

def _generate_markdown_includes(includes):
    includes = '\n'.join([ '#include "' + x + '"' for x in includes ])
    return (
        f'```c      \n'
        f'{includes}\n'
        f'```       \n'
    )

def generate_markdown(data: dict):
    markdown_units = []

    markdown_units.append("# " + data["kind"] + " - " + data["name"] + "\n")

    if data["includes"]:
        markdown_units.append(_generate_markdown_includes(data["includes"]))

    for _, v in data["defs"].items():
        parent_refid = v["parent_refid"] if "parent_refid" in v else None
        match v["kind"]:
            case "struct":
                markdown = _generate_markdown_struct(v)
            case "union":
                markdown = _generate_markdown_union(v)
            case "function":
                markdown = _generate_markdown_function(v)
            case "enum":
                markdown = _generate_markdown_enum(v)
            case "variable":
                markdown = _generate_markdown_variable(v, data, parent_refid)
            case _:
                markdown = "undefined markdown behavior for kind " + v["kind"]

        markdown_units.append(markdown)

    return "\n".join(markdown_units)


def generate_markdown_treeview(project_name: str, directories):
    markdown_units = []

    markdown_units.append( (
        f'---\n'
        f'---\n'
    ))

    for d in directories:
        dirname = d["name"]
        markdown_units.append(__generate_markdown_hugo_summary_start(dirname))
        for refid,name in d["files"].items():
            markdown_units.append(
                    f'[{name}](/{project_name}/{dirname}/{name}/)'
            )
        markdown_units.append(__generate_markdown_hugo_summary_end())

    return "\n".join(markdown_units)

