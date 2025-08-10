import os
import xml.etree.ElementTree as et
from markdown_c import generate_markdown, generate_markdown_treeview

_index_md = ('''---
build:
    list: never
    render: never
title: {directory_name}
---''')

_rendered_index_md = ('''---
title: {directory_name}
---''')

def __get_all_dir_xmls(xmlpath):
    return [ 
        x 
        for x in os.listdir(xmlpath) 
        if x.startswith("dir_") and x.endswith(".xml") 
    ]

def _generate__index_md(path, directory_name, isbasedir=False):
    out = _rendered_index_md if isbasedir else _index_md
    oua = out.replace('{directory_name}', directory_name)
    with open(path + '/_index.md', 'w') as f:
        f.write(out)
    
def _generate_base_directories(abspath, treeview):
    crawled = "/"
    relpath = ""
    for d in abspath.split('/'):
        newpath = os.path.join(crawled, d)
        if not os.path.exists(newpath):
            relpath = os.path.join(relpath, d)
            print("- Creating " + newpath)
            os.mkdir(newpath)
            # If last element
            if d == abspath.split('/')[-1]:
                _generate__index_md(newpath, d, True)
            else:
                _generate__index_md(newpath, d)
        elif os.path.exists(os.path.join(newpath, '_index.md')):
            relpath = os.path.join(relpath, d)
        crawled = newpath

    treeview_path = os.path.join(crawled, "headless/treeview")
    if not os.path.exists(treeview_path) and treeview:
        os.makedirs(treeview_path)

    return relpath

def _parse_dir_from_xml(xmlpath, filename):
    data = {}
    tree = et.parse(os.path.join(xmlpath, filename))
    root = tree.getroot().find("compounddef")

    data["name"] = root.find("compoundname").text
    data["path"] = root.find("location").get("file")

    return data

def _generate_dir_from_data(basepath, data):
    newpath = os.path.join(basepath, data["path"])

    if not os.path.exists(newpath):
        os.mkdir(newpath)

def _parse_innerfiles_from_xml(xmlpath, filename):
    files = {}
    tree = et.parse(os.path.join(xmlpath, filename))
    root = tree.getroot().find("compounddef")

    for f in root.findall("innerfile"):
        files[f.get("refid")] = f.text

    return files

def _generate_blank_file(path):
    if not os.path.exists(path):
        open(path, 'a').close()

### PARSING ###

def __get_enum_values(_def):
    return [ o.find("name").text for o in _def.findall("enumvalue") ]

def __get_variable_definition(_def):
    result = ""
    if _def.get("extern") == "yes":
        result += "extern "
    return result + __get_definition(_def)

def __get_type(_def):
    return _def.find("type").text

def __get_description(_def):
    return '\n\n'.join(
        [ x.text for x in _def.find("detaileddescription").findall("para") ]
    )

def __get_definition(_def):
    return _def.find("definition").text

def __get_args(_def):
    return _def.find("argsstring").text

def __get_params(_def):
    return [
        {
            'name': param.find("declname").text, 
            'type': ''.join(param.find("type").itertext())
        } for param in _def.findall("param") 
    ]

def __get_macro_params(_def):
    return [
        {
            'name': param.find("defname").text
        } for param in _def.findall("param")
    ]

def __get_return_description(_def):
    rd = _def.find("./detaileddescription/para/simplesect")
    if rd is None:
        return None
    return '\n\n'.join([x.text for x in rd.findall("para")])

def __get_name(_def):
    return _def.find("name").text

def __get_kind(_def):
    return _def.get("kind")

def __get_initializer(_def):
    initializer = _def.find("initializer")
    if initializer == None:
        return None
    return initializer.text

def _parse_memberdef(data, memberdef, innerclass=False):
    result = { 
        "name": data["name"],
        "kind": data["kind"],
    }

    ## ENUM ##
    if data["kind"] == "enum":
        result["enum_values"]           = __get_enum_values(memberdef)
    ## VARIABLE ##
    elif data["kind"] == "variable":
        result["variable_definition"]   = __get_variable_definition(memberdef)
        result["type"]                  = __get_type(memberdef)
        result["description"]           = __get_description(memberdef) 
    ## FUNCTION ##
    elif data["kind"] == "function":
        result["return_type"]           = __get_type(memberdef)
        result["definition"]            = __get_definition(memberdef) 
        result["args"]                  = __get_args(memberdef) 
        result["description"]           = __get_description(memberdef)
        result["params"]                = __get_params(memberdef)
        result["return_description"]    = __get_return_description(memberdef)
    ## DEFINES/MACROS ##
    elif data["kind"] == "define":
        result["params"]                = __get_macro_params(memberdef)
        result["initializer"]           = __get_initializer(memberdef)

    if innerclass:
        result["parent_refid"] = data["parent_refid"]
        result["parent_name"] = data["parent_name"]

    return result

def _parse_innerclass(refid, abspath):
    result = {}
    tree = et.parse(abspath)
    root = tree.getroot().find("compounddef")
    
    result = {}
    result[root.find("compoundname").text] = {
        "name": root.find("compoundname").text,
        "kind": root.get("kind")
    }

    for memberdef in root.findall("./sectiondef/memberdef"):
        result[memberdef.get("id")] = _parse_memberdef(
                {
                    "name": __get_name(memberdef),
                    "kind": __get_kind(memberdef),
                    "parent_refid": refid,
                    "parent_name": root.find("compoundname").text,
                },
                memberdef,
                innerclass=True
            )

    return result

def _parse_xml_file(abspath):
    result = {}
    tree = et.parse(abspath)
    root = tree.getroot().find("compounddef")
    xmldir = '/' + '/'.join(abspath.split("/")[0:-1])

    result["kind"] = root.get("kind")
    result["name"] = root.find("compoundname").text
    result["defs"] = {} 

    if result["kind"] == "file":
        result["includes"] = [o.text for o in root.findall("includes")]

    ## Find structs and unions
    for innerclass in root.findall("innerclass"):
        refid = innerclass.get("refid")
        result["defs"].update(_parse_innerclass(refid, os.path.join(xmldir, refid + ".xml")))
   
    for definition in root.findall("sectiondef"):
        for memberdef in definition.findall("memberdef"):
            result["defs"][__get_name(memberdef)] = _parse_memberdef(
                {
                    "name": __get_name(memberdef),
                    "kind": __get_kind(memberdef)
                },
                memberdef
            )
        
    return result

### // PARSING ###

def generate(basepath, xmlpath, treeview):
    relpath = _generate_base_directories(basepath, treeview)

    refid_outpath_map = {}
    refid_xmlpath_map = {}
    refid_markdown_map = {}

    for xml_filename in __get_all_dir_xmls(xmlpath):
        data = _parse_dir_from_xml(xmlpath, xml_filename)
        _generate_dir_from_data(basepath, data)
        files = _parse_innerfiles_from_xml(xmlpath, xml_filename)

        for refid,filename in files.items():
            path = os.path.join(basepath, data["name"], filename + ".md")
            _generate_blank_file(path)
            refid_outpath_map[refid] = path
            refid_xmlpath_map[refid] = os.path.join(xmlpath, refid + ".xml")

    # Parse xmls and generate markdown
    for refid, _xmlpath in refid_xmlpath_map.items():
        data = _parse_xml_file(_xmlpath)
        refid_markdown_map[refid] = generate_markdown(data)

    # Inject markdown in their respective .md files
    for refid, markdown in refid_markdown_map.items():
        with open(refid_outpath_map[refid], 'w') as f:
            f.write(markdown)

    ## Generate treeview ##

    # Do not generate treeview if false
    if treeview == False:
        return

    dirs = []

    # Parse directory xmls
    for xml_filename in __get_all_dir_xmls(xmlpath):
        data = _parse_dir_from_xml(xmlpath, xml_filename)
        data["files"] = _parse_innerfiles_from_xml(xmlpath, xml_filename)
        dirs.append(data)

    markdown = generate_markdown_treeview(relpath, dirs)
    with open(os.path.join(basepath, "headless/treeview/index.md"), 'w') as f:
        f.write(markdown)
