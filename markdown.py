def _generate_markdown_variable(unit, root):
    name = unit["name"]
    title = f'## variable {name}' if root["kind"] == "file" else ""
    description = unit["description"]

    if root["kind"] == "file":
        variable_definition = unit["variable_definition"]
    else:
        variable_definition = unit["variable_definition"].replace(root["name"] + "::", "")

    return (
        f'{title}\n'
        f'{description}\n'
        f'```c\n'
        f'{variable_definition}\n'
        f'```\n'
        f'---\n'
    )

def _generate_markdown_enum(unit):
    name = unit["name"]
    enums_formatted = ',\n\t'.join(unit["enum_values"])
    return (
        f'## enum - {name}\n'
        f'```c\n'
        f'enum {name} {{\n'
        f'\t{enums_formatted}\n'
        f'}}\n'
        f'```\n'
        f'---\n\n'
    )

def _generate_markdown_function_params(unit):
    params = ""

    if not unit:
        return params

    for param in unit:
        params += "-\t\n"
        params += "\t```c\n"
        params += "\t" + param["type"] + " " + param["name"] + "\n"
        params += "\t```\n"

    return (
        f'### parameters\n\n'
        f'{params}\n'
    )

def _generate_markdown_function(unit):
    name = unit["name"]
    definition = unit["definition"]
    args = "(...)" if unit["args"] != "()" else "()"
    description = unit["description"]
    params_formatted = _generate_markdown_function_params(unit["params"])
    return_type = unit["return_type"]
    return_description = unit["return_description"] if "return_description" in unit else ""
    return (
        f'## function - {name}\n\n'
        f'{description}\n'
        f'```c\n'
        f'{definition} {args}\n'
        f'```\n\n'
        f'{params_formatted}\n'
        f'### returns\n'
        f'```c\n'
        f'{return_type}\n'
        f'```\n'
        f'{return_description}\n\n'
        f'---\n'
    )

def _generate_markdown_includes(includes):
    includes = '\n'.join([ '#include "' + x + '"' for x in includes ])
    return (
        f'```c\n'
        f'{includes}\n'
        f'```\n'
    )

def generate_markdown(data: dict):
    markdown_units = []

    markdown_units.append("# " + data["kind"] + " - " + data["name"] + "\n")

    if "includes" in data:
        markdown_units.append(_generate_markdown_includes(data["includes"]))

    for _, v in data["defs"].items():
        match v["kind"]:
            case "function":
                markdown = _generate_markdown_function(v)
            case "enum":
                markdown = _generate_markdown_enum(v)
            case "variable":
                markdown = _generate_markdown_variable(v, data)
            case _:
                print("undefined markdown behavior for kind " + v["kind"])

        markdown_units.append(markdown)

    return "\n".join(markdown_units)

def _generate_markdown_treeview_dir_hugo_summary_start(dirname):
    return (
        f'{{{{< details summary="{dirname}" >}}}}'
    )

def _generate_markdown_treeview_dir_hugo_summary_end():
    return (
        '{{< /details >}}'
    )

def generate_markdown_treeview(project_name: str, directories):
    markdown_units = []

    markdown_units.append( (
        f'---\n'
        f'---\n'
    ))

    #print(files)

    for d in directories:
        dirname = d["name"]
        markdown_units.append(_generate_markdown_treeview_dir_hugo_summary_start(dirname))
        for refid,name in d["files"].items():
            markdown_units.append(f'- [{name}](/{project_name}/{dirname}/{name}/)')
        markdown_units.append(_generate_markdown_treeview_dir_hugo_summary_end())

    return "\n".join(markdown_units)

