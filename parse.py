#--generate base dirs w _index.md 
#-> 
#--find all dir files 
#->
#--setup dirs (mkdir)
#->
#parse dir files for innerfiles

import os
import xml.etree.ElementTree as et
from markdown import generate_markdown, generate_markdown_treeview

_basepath = '/doc/jarg/'
_index_md = ('''---
build:
    list: never
    render: never
title: {directory_name}
---''')

def __get_all_dir_xmls(xmlpath):
    return [ x for x in os.listdir(xmlpath) if x.startswith("dir_") and x.endswith(".xml") ]

def __allowed_dir(directory_data):
    return directory_data["name"] != "src"

def _generate__index_md(path, directory_name):
    out = _index_md
    out = out.replace('{directory_name}', directory_name)
    with open(path + '/_index.md', 'w') as f:
        f.write(out)
    
def _generate_base_directories(basepath, dirs):
    fullpath = os.getcwd()
    for d in basepath.split('/'):
        newpath = os.path.join(os.path.join(fullpath, d))
        if not os.path.exists(newpath):
            os.mkdir(newpath)
        _generate__index_md(newpath, d)
        fullpath = newpath

    treeview_path = os.path.join(fullpath, "headless/treeview")
    if not os.path.exists(treeview_path):
        os.makedirs(treeview_path)

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

def _generate_blank_file_from_xml(path):
    if not os.path.exists(path):
        open(path, 'a').close()

# PARSING

def _parse_xml_file(path):
    data = {}
    tree = et.parse(path)
    root = tree.getroot().find("compounddef")

    data["kind"] = root.get("kind")
    data["name"] = root.find("compoundname").text
    data["defs"] = {} 

    if data["kind"] == "file": 
        data["includes"] = [o.text for o in root.findall("includes")]
   
    for definition in root.findall("sectiondef"):
        for memberdef in definition.findall("memberdef"):
            cdef = memberdef.find("name").text
            kind = memberdef.get("kind")
            data["defs"][cdef] = {}
            data["defs"][cdef]["name"] = cdef
            data["defs"][cdef]["kind"] = kind

            if kind == "enum":
                data["defs"][cdef]["enum_values"] = [o.find("name").text for o in memberdef.findall("enumvalue")]

            if kind == "variable":
                data["defs"][cdef]["variable_definition"] = memberdef.find("definition").text
                if memberdef.get("extern") == "yes":
                    data["defs"][cdef]["variable_definition"] = (
                        "extern " + data["defs"][cdef]["variable_definition"] )
                data["defs"][cdef]["type"] = memberdef.find("type").text
                data["defs"][cdef]["description"] = '\n\n'.join([x.text for x in memberdef.find("detaileddescription").findall("para")])

            if kind == "function":
                data["defs"][cdef]["return_type"] = memberdef.find("type").text
                data["defs"][cdef]["definition"] = memberdef.find("definition").text
                data["defs"][cdef]["args"] = memberdef.find("argsstring").text
                data["defs"][cdef]["description"] = memberdef.find("detaileddescription").find("para").text
                data["defs"][cdef]["params"] = []
                for param in memberdef.findall("param"):
                    data["defs"][cdef]["params"].append({'name': param.find("declname").text, 'type': param.find("type").text})

                return_desc = memberdef.find("detaileddescription").find("para").find("simplesect")
                if return_desc is not None:
                    data["defs"][cdef]["return_description"] = '\n\n'.join([x.text for x in return_desc.findall("para")])

    return data

# // PARSING

def _steps(basepath, xmlpath):
    basepath = basepath.strip("/")
    _generate_base_directories(basepath, [])

    refid_outpath_map = {}
    refid_xmlpath_map = {}
    refid_markdown_map = {}

    for dirxmlpath in __get_all_dir_xmls(xmlpath):
        data = _parse_dir_from_xml(xmlpath, dirxmlpath)
        if not __allowed_dir(data):
            continue
        _generate_dir_from_data(basepath, data)
        files = _parse_innerfiles_from_xml(xmlpath, dirxmlpath)

        for refid,filename in files.items():
            path = os.path.join(basepath, data["name"], filename + ".md")
            _generate_blank_file_from_xml(path)
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
    dirs = []

    for dirxmlpath in __get_all_dir_xmls(xmlpath):
        data = _parse_dir_from_xml(xmlpath, dirxmlpath)
        if not __allowed_dir(data):
            continue
        data["files"] = _parse_innerfiles_from_xml(xmlpath, dirxmlpath)
        dirs.append(data)

    markdown = generate_markdown_treeview(basepath, dirs)

    with open(os.path.join(basepath, "headless/treeview/index.md"), 'w') as f:
        f.write(markdown)

_steps(_basepath, "xml")
