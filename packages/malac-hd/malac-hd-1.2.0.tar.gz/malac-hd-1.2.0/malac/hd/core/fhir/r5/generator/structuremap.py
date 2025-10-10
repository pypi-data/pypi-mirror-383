import os
import sys
import builtins
import inspect
import datetime
import re
import threading
import ast
from urllib.parse import urlparse

from malac.hd import ConvertMaster, list_i_o_modules
from malac.hd.core.fhir.base.generator.resource import parse_factory

from . import fhirpath
from .conceptmap import PythonGenerator as ConceptMapPythonGenerator

from malac.models.fhir import utils as utils, r5 as supermod

thread_local = threading.local()
thread_local.importing = set()
thread_local.wildcard_importing = set()

class PythonGenerator(supermod.StructureMap, ConvertMaster):

    additional_header = ""
    uuid_method = "str(uuid.uuid4())"
    now_method = "datetime.now()"
    fhir_version = supermod.__name__.split(".")[-1]
    keyword_list = ["type", "class", "import"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.var_types = {}
        self.expected_types = {}
        self.none_check = set()
        self.list_var = set()
        self.list_var_resolved = set()
        self.group_types = {}
        self.default_types_maps = {}
        self.default_types_maps_plus = {}
        self.default_types_maps_subtypes = {}
        self.o_module = None
        self.i_module = None
        self.py_code = ""
        self.indent = 0
        self.transform_default_needed = False
        self.translate_multi_needed = True # TODO:sbe also check imports
        self.translate_single_needed = True # TODO:sbe also check imports
        self.aliases = {}
        self.all_groups = []
        self.temp_filename = None
        self.concept_model = None

    def convert(self, silent=True, source=".", standalone=True, all_groups=None, parse_wrapper=None): # TODO:sbe replace source with context, to make more generic
        for structure in self.get_structure():
            s = structure.get_url().value
            r_name = s[s.rfind('/') + 1:]
            if structure.get_alias():
                self.aliases[structure.get_alias().value] = r_name
            else:
                self.aliases[r_name] = r_name

        if standalone:
            jurisdiction = None
            for use_ctx in self.get_useContext():
                code = use_ctx.get_code()
                vals = use_ctx.get_valueCodeableConcept()
                if code and vals and code.get_system() and code.get_system().value == "http://terminology.hl7.org/CodeSystem/usage-context-type" and code.get_code() and code.get_code().value == "jurisdiction":
                    for val in vals.get_coding():
                        if val.get_system() and val.get_system().value == "urn:iso:std:iso:3166" and val.get_code():
                            jurisdiction = val.get_code().value
            if jurisdiction is None and self.get_url() and self.get_url().value:
                domain = urlparse(self.get_url().value).netloc
                jurisdiction = domain.split(".")[-1].upper()
            first_group = self.get_group()[0]
            for i in first_group.get_input():
                t = i.get_type().value
                mod = None
                for structure in self.get_structure():
                    s = structure.get_url().value
                    if s == t or (structure.get_alias() and structure.get_alias().value == t):
                        try:
                            mod = list_i_o_modules[s[:s.rfind('/')]]
                        except KeyError:
                            raise BaseException(f"No module registered for {s}")
                        if isinstance(mod, dict):
                            mod = mod[jurisdiction]
                if not mod:
                    for structure in self.get_structure():
                        s = structure.get_url().value
                        s_short = s[s.rfind('/') + 1:]
                        if s_short == t:
                            try:
                                mod = list_i_o_modules[s[:s.rfind('/')]]
                            except KeyError:
                                raise BaseException(f"No module registered for {s}")
                            if isinstance(mod, dict):
                                mod = mod[jurisdiction]
                if not mod:
                    raise BaseException("Could find in/out module")
                if i.get_mode().value == "source":
                    self.i_module = mod
                else:
                    self.o_module = mod

        self.group_types.clear()
        self.default_types_maps.clear()
        self.default_types_maps_plus.clear()
        self.transform_default_needed = False
        self.all_groups = all_groups or []
        self.all_groups += self.get_group()

        self.py_code = ""
        imported_py_code = ""
        imported_skipped_groups = []
        if standalone:
            self._header()

        # add all the translates of the none, one or multiple conceptMaps of this strucutreMap
        if hasattr(self.i_module, "CodeableConcept"):
            self.concept_model = self.i_module
        elif hasattr(self.o_module, "CodeableConcept"):
            self.concept_model = self.o_module
        else:
            self.concept_model = supermod
        self.translate_dict_py_code = ""
        for contained in self.get_contained():
            if tmp := contained.get_ConceptMap():
                self.translate_dict_py_code += "\n"
                tmp.convert(silent=True, return_header_and_footer_for_standalone=False, return_translate_def = False, return_dict_add=True, model=self.concept_model)
                self.translate_dict_py_code += tmp.py_code

        thread_local.importing.add(source)

        for import_ in self.get_import():
            # search all files in the same directory for the url
            url = import_.value
            wildcard_importing = set(thread_local.wildcard_importing)
            if "*" in url:
                url = re.escape(url)
                url = url.replace("\*", ".*")
                wildcard_url = True
                thread_local.wildcard_importing.add(url) 
            else:
                wildcard_url = False
            dirname = os.path.dirname(os.path.abspath(source))
            basename = os.path.basename(source)
            ext = basename[basename.index("."):]
            found = False
            for filename in os.listdir(dirname):
                if filename != basename and filename.endswith(ext):
                    path = dirname + "/" + filename
                    url_matches = False
                    try:
                        if path not in thread_local.importing:
                            if parse_wrapper:
                                imported = parse_wrapper(path, silence=silent)
                            else:
                                imported = parse(path, silence=silent)
                            if wildcard_url:
                                if imported.get_url() and imported.get_url().value: # url not in wildcard_importing and 
                                    value = imported.get_url().value
                                    match = re.match(url, value)
                                    url_matches = bool(match)
                                else:
                                    url_matches = False
                            else:
                                url_matches = imported.get_url() and imported.get_url().value == url
                        else:
                            found = True
                    except:
                        continue
                    if url_matches:
                        imported.i_module = self.i_module
                        imported.o_module = self.o_module
                        thread_local.importing.add(path)
                        added_code = imported.convert(silent=silent, source=path, standalone=False, all_groups=self.all_groups)
                        imported_py_code += added_code
                        imported_skipped_groups += imported.skipped_groups
                        self.transform_default_needed = self.transform_default_needed or imported.transform_default_needed
                        self.translate_dict_py_code += imported.translate_dict_py_code
                        self.all_groups += imported.get_group()
                        self.default_types_maps.update(imported.default_types_maps)
                        self.default_types_maps_plus.update(imported.default_types_maps_plus)
                        self.default_types_maps_subtypes.update(imported.default_types_maps_subtypes)
                        found = True
                        if not wildcard_url:
                            break
            if not found and not wildcard_url:
                raise BaseException("Could not import %s, file not found." % url)

        if self.get_const():
            self._append_py()
        for s_map_const in self.get_const():
            self._handle_const(s_map_const)

        for s_map_group in self.get_group():
            if not s_map_group.typeMode or s_map_group.typeMode.value == "none":
                pass
            elif s_map_group.typeMode.value == "types":
                group_name = s_map_group.name.value
                types = []
                for s_map_input in s_map_group.get_input():
                    type_name = s_map_input.get_type().value
                    if s_map_input.get_mode().value == "target":
                        clazz = getattr(self.o_module, type_name)
                    elif s_map_input.get_mode().value == "source":
                        try:
                            clazz = getattr(self.i_module, type_name)
                        except BaseException:
                            try:
                                type_name_2 = "POCD_MT000040_" + type_name  # TODO avoid this
                                clazz = getattr(self.i_module, type_name_2)
                                type_name = type_name_2
                            except:
                                type_name_2 = "POCD_MT000040UV02_" + type_name  # TODO avoid this
                                clazz = getattr(self.i_module, type_name_2)
                                type_name = type_name_2
                    types.append(clazz)
                if len(types) != 2:
                    raise BaseException(f"Invalid default group: {group_name} does not have 2 parameters.")
                self.default_types_maps[tuple(types)] = group_name
            elif s_map_group.typeMode.value == "type+":
                group_name = s_map_group.name.value
                types = []
                for s_map_input in s_map_group.get_input():
                    type_name = s_map_input.get_type().value
                    if type_name in self.aliases:
                        type_name = self.aliases[type_name]
                    if s_map_input.get_mode().value == "target":
                        clazz = getattr(self.o_module, type_name)
                    elif s_map_input.get_mode().value == "source":
                        try:
                            clazz = getattr(self.i_module, type_name)
                        except BaseException:
                            try:
                                type_name_2 = "POCD_MT000040_" + type_name  # TODO avoid this
                                clazz = getattr(self.i_module, type_name_2)
                                type_name = type_name_2
                            except:
                                type_name_2 = "POCD_MT000040UV02_" + type_name  # TODO avoid this
                                clazz = getattr(self.i_module, type_name_2)
                                type_name = type_name_2
                    types.append(clazz)
                if len(types) != 2:
                    raise BaseException(f"Invalid default group: {group_name} does not have 2 parameters.")
                self.default_types_maps_plus[types[0]] = (types[1], group_name)
            else:
                raise BaseException(f"Unsupported typeMode {s_map_group.typeMode.value}")

        for (a_src_type, a_trg_type), a_group_name in self.default_types_maps.items():
            for (b_src_type, b_trg_type), b_group_name in self.default_types_maps.items():
                if a_src_type != b_src_type and a_trg_type == b_trg_type:
                    if issubclass(a_src_type, b_src_type):
                        if a_group_name not in self.default_types_maps_subtypes:
                            self.default_types_maps_subtypes[a_group_name] = []
                        self.default_types_maps_subtypes[a_group_name].append((b_src_type, b_group_name))

        group_queue = list(self.get_group()) + imported_skipped_groups
        postponed = []
        last_postponed = []
        failed_groups = []
        skipped_groups = []
        while group_queue:
            while group_queue:
                s_map_group = group_queue.pop(0)
                converted = self._handle_group(s_map_group)
                if not converted:
                    postponed.append(s_map_group)
            if postponed:
                if len(postponed) == len(last_postponed):
                    for p in postponed:
                        if p.name.value in self.group_types:
                            failed_groups.append(p)
                        else:
                            skipped_groups.append(p)
                    postponed = []
                group_queue = list(postponed)
                last_postponed = postponed
                postponed = []

        # add translate with its dictionary
        if standalone:
            self.py_code += ConceptMapPythonGenerator().convert(silent=True, return_header_and_footer_for_standalone=False, return_translate_def=True, return_dict_add=False, model=self.concept_model)
            self.py_code += self.translate_dict_py_code
        
        self.py_code += imported_py_code
        if standalone:
            self._footer()

        if not silent:
            print("\n%s" % self.py_code)

        if failed_groups:
            group_names = ", ".join([p.name.value for p in failed_groups])
            raise BaseException(
                f"Too little type information. Please provide types for groups on one or more of these groups: {group_names}")
        elif skipped_groups:
            group_names = ", ".join([p.name.value for p in skipped_groups])
            print(f"Skipped not called groups because of missing type info: {group_names}", file=sys.stderr)

        self.skipped_groups = skipped_groups

        if standalone:
            thread_local.importing.clear()
            thread_local.wildcard_importing.clear()

        return self.py_code

    def _header(self):
        self.py_code += '''
import sys
import argparse
import time
import uuid
import builtins
import re
import io
import json
from datetime import datetime
from malac.utils import date as dateutil
from html import escape as html_escape
'''
        self.py_code += "import "+self.i_module.__name__+"\n"
        if self.o_module.__name__ != self.i_module.__name__:
            self.py_code += "import "+self.o_module.__name__+"\n"
        if getattr(self.o_module, "string", None):
            self.py_code += "from "+self.o_module.__name__+" import string, base64Binary, markdown, code, dateTime, uri, boolean, decimal\n"  # TODO check if there is a better solution
        elif getattr(self.i_module, "string", None):
            self.py_code += "from "+self.i_module.__name__+" import string, base64Binary, markdown, code, dateTime, uri, boolean, decimal\n"  # TODO check if there is a better solution
        self.py_code += '''from malac.models.fhir import utils\n'''
        self.py_code += '''from malac.utils import fhirpath

'''
        self.py_code += "description_text = \"This has been compiled by the MApping LAnguage compiler for Health Data, short MaLaC-HD. See arguments for more details.\"\n"
        self.py_code += "one_timestamp = %s\n" % self.now_method
        self.py_code += "fhirpath_utils = fhirpath.FHIRPathUtils(%s)\n" % (self.o_module if getattr(self.o_module, "string", None) else self.i_module).__name__ # TODO has to be some FHIR module 
        self.py_code += "shared_vars = {}\n"
        self.py_code += "\n"
        self.py_code += self.additional_header

        self.py_code += "def init_argparse() -> argparse.ArgumentParser:\n"
        self.py_code += "    parser = argparse.ArgumentParser(description=description_text)\n"
        self.py_code += "    parser.add_argument(\n"
        self.py_code += "       '-s', '--source', help='the source file path', required=True\n"
        self.py_code += "    )\n"
        self.py_code += "    parser.add_argument(\n"
        self.py_code += "       '-t', '--target', help='the target file path the result will be written to', required=True\n"
        self.py_code += "    )\n"
        self.py_code += "    return parser\n"
        self.py_code += "\n"

        self.py_code += "def transform(source_path, target_path):\n"
        self.py_code += "    start = time.time()\n"
        self.py_code += "    print('+++++++ Transformation from '+source_path+' to '+target_path+' started +++++++')\n"
        self.py_code += "\n"

        s_map_group = self.get_group()[0]
        group_name = s_map_group.get_name().value
        for s_map_input in s_map_group.get_input():
            if s_map_input.get_mode().value == "target":
                target = s_map_input.get_type().value
                target_name = s_map_input.get_name().value
            if s_map_input.get_mode().value == "source":
                source_name = s_map_input.get_name().value
        self.py_code += "    if source_path.endswith('.xml'):\n"
        self.py_code += "        " + source_name + " = "+self.i_module.__name__+".parse(source_path, silence=True)\n"
        if "fhir" in self.i_module.__name__.split("."):
            self.py_code += "    elif source_path.endswith('.json'):\n"
            self.py_code += "        with open(source_path, 'r', newline='', encoding='utf-8') as f:\n"
            self.py_code += "            " + source_name + " = utils.parse_json(" + self.i_module.__name__ + ", json.load(f))\n"
        self.py_code += "    else:\n"
        self.py_code += "        raise BaseException('Unknown source file ending: ' + source_path)\n"
        if target in self.aliases:
            target = self.aliases[target]
        try:
            clazz = getattr(self.o_module, target)
        except BaseException:
            try:
                type_name_2 = "POCD_MT000040_" + target  # TODO avoid this
                clazz = getattr(self.o_module, type_name_2)
                target = type_name_2
            except:
                type_name_2 = "POCD_MT000040UV02_" + target  # TODO avoid this
                clazz = getattr(self.o_module, type_name_2)
                target = type_name_2
        self.py_code += "    " + target_name + " = "+self.o_module.__name__+"."+target+"()\n"
        self.py_code += "    "+group_name+"("+source_name+", "+target_name+")\n"
        self.py_code += "    with open(target_path, 'w', newline='', encoding='utf-8') as f:\n"
        self.py_code += "        if target_path.endswith('.xml'):\n"
        self.py_code += "            f.write('<?xml version=\"1.0\" encoding=\"UTF-8\"?>\\n')\n"
        self.py_code += "            "+ target_name+ ".export(f, 0, namespacedef_='xmlns=\"http://hl7.org/fhir\" xmlns:v3=\"urn:hl7-org:v3\"')\n"
        if "fhir" in self.o_module.__name__.split("."):
            self.py_code += "        elif target_path.endswith('.json'):\n"
            self.py_code += "            json.dump("+ target_name +".exportJson(), f)\n"
        self.py_code += "        else:\n"
        self.py_code += "            raise BaseException('Unknown target file ending')\n"
        self.py_code += "\n"
        self.py_code += "    print('altogether in '+str(round(time.time()-start,3))+' seconds.')\n"
        self.py_code += "    print('+++++++ Transformation from '+source_path+' to '+target_path+' ended  +++++++')\n"

    def _footer(self):
        model = self.o_module.__name__
        self.py_code += "\ndef unpack_container(resource_container):\n"
        self.py_code += "    if resource_container is None:\n"
        self.py_code += "        return None\n"
        cclass = getattr(self.o_module, "ResourceContainer", getattr(self.i_module, "ResourceContainer", None))
        for name, elem_type in inspect.get_annotations(cclass.__init__).items():
            if name != "gds_collector_":
                self.py_code += "    if resource_container.%s is not None:\n" % name
                self.py_code += "        return resource_container.%s\n" % name
        self.py_code += "    return None\n"

        if self.transform_default_needed:
            self.py_code += "\n"
            self.py_code += "default_types_maps = {\n"
            for types, name in self.default_types_maps.items():
                self.py_code += "    (%s.%s, %s.%s): %s,\n" % (types[0].__module__, types[0].__name__, types[1].__module__, types[1].__name__, name)
            self.py_code += "}\n"
            self.py_code += "default_types_maps_plus = {\n"
            for type_src, (type_trg, name) in self.default_types_maps_plus.items():
                self.py_code += "    %s.%s: %s,\n" % (type_src.__module__, type_src.__name__, name)
            self.py_code += "}\n"
            self.py_code += '''
def transform_default(source, target, target_type=None):
    target_type = target_type or type(target)
    source_type = type(source)
    while source_type is not None:
        default_map = default_types_maps.get((source_type, target_type))
        if default_map:
            default_map(source, target)
            return
        source_type = source_type.__bases__[0] if source_type.__bases__ else None
    source_type = type(source)
    while source_type is not None:
        default_map_plus = default_types_maps_plus.get(source_type)
        if default_map_plus:
            default_map_plus(source, target)
            return
        source_type = source_type.__bases__[0] if source_type.__bases__ else None
    raise BaseException('No default transform found for %s -> %s' % (type(source), target_type))
'''

        if self.translate_single_needed:
            self.py_code += "\n"
            # TODO:sbe extract special cases into separate file
            self.py_code += "def translate_unmapped(url, code):\n"
            self.py_code += "    if url == 'http://hl7.org/fhir/ConceptMap/special-oid2uri': return [{'uri': 'urn:oid:%s' % code}]\n"
            self.py_code += "    if url == 'OIDtoURI': return [{'code': 'urn:oid:%s' % code}]\n"
            self.py_code += "    if url == 'StructureMapGroupTypeMode': return [{'code': 'none'}]\n"
            self.py_code += "    if url == 'AllergyCategoryMap': return [{'code': None}]\n"
            self.py_code += "    raise BaseException('Code %s could not be mapped to any code in concept map %s and no exception defined' % (code, url))\n"

            relationship_key = ConceptMapPythonGenerator.get_key_4_r5relationsship_r4equivalence(self.concept_model)

            # from https://hl7.org/fhir/mapping-language.html:
            # Params:
            #    source, 
            #    map_uri, 
            #    output	
            # use the translate operation. The source is some type of code or coded datatype, and the source and map_uri are passed to the translate operation. 
            # The output determines what value from the translate operation is used for the result of the operation (code, system, display, Coding, or CodeableConcept)
            self.py_code += f'''
def translate_single(url, code, out_type):
    trans_out = translate(url=url, code=code, silent=True)
    matches = [match['concept'] for match in trans_out['match'] if match['{relationship_key}']=='equivalent' or match['{relationship_key}']=='equal']
    # if there are mutliple 'equivalent' or 'equal' matches and CodeableConcept is not the output param, than throw an error
    if len(matches) > 1:
        raise BaseException("There are multiple 'equivalent' or 'equal' matches in the results of the translate and output type is not CodeableConcept!")
    elif len(matches) == 0:
        matches = translate_unmapped(url=url, code=code)
    if out_type == "Coding":
        return {model}.Coding(system=({model}.uri(value=matches[0]['system']) if "system" in matches[0] else None), 
                              version=({model}.string(value=matches[0]['version']) if "version" in matches[0] else None), 
                              code=({model}.string(value=matches[0]['code']) if "code" in matches[0] else None), 
                              display=({model}.string(value=matches[0]['display']) if "display" in  matches[0] else None), 
                              userSelected=({model}.string(value=matches[0]['userSelected']) if "userSelected" in matches[0] else None))
    else:
        return matches[0][out_type]
'''
        if self.translate_multi_needed:
            self.py_code += f'''
def translate_multi(url, code):
    trans_out = translate(url=url, code=code, silent=True)
    matches = [match['concept'] for match in trans_out['match'] if match['{relationship_key}']=='equivalent' or match['{relationship_key}']=='equal']
    return {model}.CodeableConcept(coding=[{model}.Coding(system=({model}.uri(value=matches[0]['system']) if "system" in matches[0] else None), 
                                                          version=({model}.string(value=matches[0]['version']) if "version" in matches[0] else None), 
                                                          code=({model}.string(value=matches[0]['code']) if "code" in matches[0] else None), 
                                                          display=({model}.string(value=matches[0]['display']) if "display" in  matches[0] else None), 
                                                          userSelected=({model}.string(value=matches[0]['userSelected']) if "userSelected" in matches[0] else None)
                                                          ) for match in matches])

'''
        self.py_code += f'''
if __name__ == "__main__":
    parser = init_argparse()
    args = parser.parse_args()
    transform(args.source, args.target)
'''

    def _handle_group(self, s_map_group):
        self.indent = 0
        self.var_types.clear()
        self.none_check.clear()
        self.list_var.clear()
        self.list_var_resolved.clear()
        group_name = s_map_group.get_name().value
        names = []
        types = []
        for s_map_input in s_map_group.get_input():
            var_name = s_map_input.get_name().value
            type_name = s_map_input.get_type().value if s_map_input.get_type() else None
            if not type_name:
                if group_name in self.group_types and var_name in self.group_types[group_name]:  # lookup type from calls
                    clazz = self.group_types[group_name][var_name]
                else:
                    return False
            elif s_map_input.get_mode().value == "target":
                type_name = self.aliases.get(type_name, type_name).replace("-", "_")
                try:
                    clazz = getattr(self.o_module, type_name)
                except BaseException:
                    try:
                        type_name_2 = "POCD_MT000040_" + type_name  # TODO avoid this
                        clazz = getattr(self.o_module, type_name_2)
                        type_name = type_name_2
                    except:
                        type_name_2 = "POCD_MT000040UV02_" + type_name  # TODO avoid this
                        clazz = getattr(self.o_module, type_name_2)
                        type_name = type_name_2
            elif s_map_input.get_mode().value == "source":
                type_name = self.aliases.get(type_name, type_name).replace("-", "_")
                if type_name == "Base":
                    type_name = "GeneratedsSuper"
                try:
                    clazz = getattr(self.i_module, type_name)
                except BaseException:
                    try:
                        type_name_2 = "POCD_MT000040_" + type_name  # TODO avoid this
                        clazz = getattr(self.i_module, type_name_2)
                        type_name = type_name_2
                    except:
                        type_name_2 = "POCD_MT000040UV02_" + type_name  # TODO avoid this
                        clazz = getattr(self.i_module, type_name_2)
                        type_name = type_name_2
            names.append(var_name)
            types.append(clazz.__module__ + "." + clazz.__name__)
            self.var_types[var_name] = clazz

        self._append_py()
        self._append_py("def %s(%s):" % (group_name, ", ".join(names)))
        self.indent = 4
        rule_queue = list(s_map_group.get_rule())

        if s_map_group.get_extends():
            base_group = None
            base_name = s_map_group.get_extends().value
            for s_map_group_2 in self.all_groups:
                if s_map_group_2.get_name().value == base_name:
                    base_group = s_map_group_2
                    break
            if base_group is None:
                raise BaseException("Base group %s not found" % base_name)
            base_names = []
            for s_map_input in base_group.get_input():
                base_names.append(s_map_input.get_name().value)
            if len(names) > len(base_names):
                self._append_py("%s(%s)" % (base_name, ", ".join(base_names)))
                self._save_group_types(base_group.name.value, base_names)
            else:
                self._append_py("%s(%s)" % (base_name, ", ".join(names)))
                self._save_group_types(base_group.name.value, names)
        elif rule_queue == []:
            self._append_py("pass")

        while rule_queue != []:
            s_map_rule = rule_queue.pop(0)
            if isinstance(s_map_rule, int):
                self.indent += s_map_rule
                continue
            elif isinstance(s_map_rule, tuple):
                self.list_var.add(s_map_rule[0])
                self.list_var_resolved.discard(s_map_rule[0])
                self.none_check.discard(s_map_rule[0])
                self._append_py("%s = %s" % s_map_rule)
                continue
            elif isinstance(s_map_rule, str):
                self.none_check.add(s_map_rule)
                self.list_var_resolved.discard(s_map_rule)
                continue

            add_indent = 0
            remove_indent = 0
            checked_none = []
            resolved_list = []

            for s_source in s_map_rule.get_source():
                ctx = s_source.get_context()
                if ctx and ctx.value in self.none_check:
                    self._append_py("if %s:" % ctx.value)
                    self.none_check.discard(ctx.value)
                    checked_none.append(ctx.value)
                    remove_indent += -4
                    self.indent += 4
                elif ctx and ctx.value in self.list_var:
                    self._append_py("for _%s in %s:" % (ctx.value, ctx.value))
                    self.var_types["_%s" % ctx.value] = self.var_types.get(ctx.value, None)
                    self.list_var.discard(ctx.value)
                    self.list_var_resolved.add(ctx.value)
                    resolved_list.append(ctx.value)
                    remove_indent += -4
                    self.indent += 4
                if s_source.get_variable() or s_source.get_condition():
                    if s_map_rule.get_target() or s_map_rule.get_rule():
                        indents = self._handle_source(s_source)
                    else:
                        indents = self._handle_source_no_rules(s_source)
                    add_indent += indents[0]
                    remove_indent += indents[1]

            for s_map_target in s_map_rule.get_target():
                transform = s_map_target.get_transform()
                # all values from http://hl7.org/fhir/valueset-map-transform.html have to be handled
                ctx = s_map_target.get_context()
                target_indent = 0
                target_checked = []
                target_resolved = []
                target_after = []
                out_var_after = False
                out_var_insert = None
                if ctx and ctx.value in self.none_check:
                    self._append_py("if %s:" % ctx.value)
                    self.none_check.discard(ctx.value)
                    target_checked.append(ctx.value)
                    if s_map_target.get_variable():
                        target_after.insert(0, (" " * self.indent) + "    %s = None" % s_map_target.get_variable().value)
                        target_after.insert(0, (" " * self.indent) + "else:")
                        target_checked.append(s_map_target.get_variable().value)
                    target_indent += -4
                    self.indent += 4
                elif ctx and ctx.value in self.list_var:
                    if s_map_target.get_variable():
                        self._append_py("%s = []" % (s_map_target.get_variable().value))
                        self.list_var.discard(s_map_target.get_variable().value)
                        self.list_var_resolved.add(s_map_target.get_variable().value)
                        target_resolved.append(s_map_target.get_variable().value)
                        out_var_insert = (" " * self.indent) + "    %s.append(_%s)" % (s_map_target.get_variable().value, s_map_target.get_variable().value)
                        target_after.insert(0, out_var_insert)
                        out_var_after = True
                    self._append_py("for _%s in %s:" % (ctx.value, ctx.value))
                    self.var_types["_%s" % ctx.value] = self.var_types.get(ctx.value, None)
                    self.list_var.discard(ctx.value)
                    self.list_var_resolved.add(ctx.value)
                    target_resolved.append(ctx.value)
                    target_indent += -4
                    self.indent += 4
                if not transform or transform.value != "append":
                    for param in s_map_target.get_parameter():
                        if param.valueId and param.valueId.value in self.none_check:
                            self.none_check.discard(param.valueId.value)
                            target_checked.append(param.valueId.value)
                            if s_map_target.get_variable():
                                target_after.insert(0, (" " * self.indent) + "    %s = None" % self._get_out_var(s_map_target.get_variable().value))
                                target_after.insert(0, (" " * self.indent) + "else:")
                                target_checked.append(s_map_target.get_variable().value)
                            target_indent += -4
                            self.indent += 4
                        elif param.valueId and param.valueId.value in self.list_var:
                            if s_map_target.get_variable() and not out_var_after:
                                self._append_py("%s = []" % (s_map_target.get_variable().value))
                                self.list_var.discard(s_map_target.get_variable().value)
                                self.list_var_resolved.add(s_map_target.get_variable().value)
                                target_resolved.append(s_map_target.get_variable().value)
                                if out_var_after:
                                    target_after.remove(out_var_insert)
                                out_var_insert = (" " * self.indent) + "    %s.append(_%s)" % (s_map_target.get_variable().value, s_map_target.get_variable().value)
                                target_after.insert(0, out_var_insert)
                                out_var_after = True
                            self._append_py("for _%s in %s:" % (param.valueId.value, param.valueId.value))
                            self.var_types["_%s" % param.valueId.value] = self.var_types.get(param.valueId.value, None)
                            self.list_var.discard(param.valueId.value)
                            self.list_var_resolved.add(param.valueId.value)
                            target_resolved.append(param.valueId.value)
                            target_indent += -4
                            self.indent += 4
                if s_map_target.get_listMode() and (transform is not None or s_map_target.get_listMode()[0].value != "share"):
                    raise NotImplementedError("Target list mode '%s' not implemented yet (for transform %s)" % (s_map_target.get_listMode()[0].value, transform))
                if transform is None:
                    self._handle_target_assign(s_map_rule.get_source()[0], s_map_target)
                elif transform.value == "cast":
                    self._handle_target_cast(s_map_target)
                elif transform.value == "uuid":
                    self._handle_target_uuid(s_map_target)
                elif transform.value == "append":
                    self._handle_target_append(s_map_target)
                elif transform.value == "copy":
                    self._handle_target_copy(s_map_rule.get_source()[0], s_map_target)
                elif transform.value == "evaluate":
                    self._handle_target_evaluate(s_map_target)
                elif transform.value == "create":
                    self._handle_target_create(s_map_rule.get_source()[0], s_map_target)
                elif transform.value == "reference":
                    self._handle_target_reference(s_map_target)
                elif transform.value == "truncate":
                    self._handle_target_truncate(s_map_target)
                elif transform.value == "pointer":
                    self._handle_target_pointer(s_map_target)
                elif transform.value == "cc":
                    self._handle_target_cc(s_map_target)
                elif transform.value == "c":
                    self._handle_target_c(s_map_target)
                elif transform.value == "id":
                    self._handle_target_id(s_map_target)
                elif transform.value == "qty":
                    self._handle_target_qty(s_map_target)
                elif transform.value == "cp":
                    self._handle_target_cp(s_map_target)
                elif transform.value == "translate":
                    self._handle_target_translate(s_map_target)
                elif transform.value in ["pointer", "cc", "c"]:
                    raise NotImplementedError("Transform '%s' is not yet implemented" % transform.value)
                elif transform.value in ["escape", "dateop"]:
                    raise NotImplementedError("Transform '%s' is not yet supported" % transform.value)
                else:
                    raise BaseException("Unknown transform '%s'" % transform.value)
                self.indent += target_indent
                for target in target_checked:
                    self.none_check.add(target)
                    self.list_var.discard(target)
                for target in target_resolved:
                    self.none_check.discard(target)
                    self.list_var.add(target)
                    self.list_var_resolved.discard(target)
                for target in target_after:
                    self.py_code += target + "\n"

            for d in s_map_rule.get_dependent():
                target_indent = 0
                target_checked = []
                target_resolved = []
                d_name = d.name.value
                var_names = [v.valueString.value for v in d.get_parameter()]
                for var_name in var_names:
                    if var_name in self.none_check:
                        self.none_check.discard(var_name)
                        target_checked.append(var_name)
                        target_indent += -4
                        self.indent += 4
                    elif var_name in self.list_var:
                        self._append_py("for _%s in %s:" % (var_name, var_name))
                        self.var_types["_%s" % var_name] = self.var_types.get(var_name, None)
                        self.list_var.discard(var_name)
                        self.list_var_resolved.add(var_name)
                        target_resolved.append(var_name)
                        target_indent += -4
                        self.indent += 4
                self._append_py("%s(%s)" % (d_name, ", ".join([self._get_out_var(var_name) for var_name in var_names])))
                self._save_group_types(d_name, var_names, group=s_map_group)
                self.indent += target_indent
                for target in target_checked:
                    self.none_check.add(target)
                    self.list_var.discard(target)
                for target in target_resolved:
                    self.none_check.discard(target)
                    self.list_var.add(target)
                    self.list_var_resolved.discard(target)

            rule_queue = [add_indent] + s_map_rule.get_rule() + [remove_indent] + checked_none + resolved_list + rule_queue

        return True

    def _save_group_types(self, group_name, variables, group=None):
        group_vars = None
        for s_map_group in self.all_groups:
            if s_map_group.get_name().value == group_name:
                group_vars = [i.get_name().value for i in s_map_group.get_input()]
                if len(variables) != len(group_vars):
                    raise BaseException(f"Invalid group call {group_name}: parameters do not match. Expected {group_vars}, got {variables} ({group.name.value if group else 'Unknown group'})")
                break
        if not group_vars:
            raise BaseException(f"Invalid group call {group_name}: group not found.")
        group_types = self.group_types.get(group_name, {})
        idx = 0
        for v in variables:
            if v in self.var_types:
                group_types[group_vars[idx]] = self.var_types[v]
            idx += 1
        self.group_types[group_name] = group_types

    def _handle_const(self, s_map_const):
        result = self._handle_fhirpath(s_map_const.get_value().value, None, None, condition=True)
        self._append_py(f"{s_map_const.get_name().value} = {result[0]}")

    def _handle_condition(self, condition, s_source):
        result = self._handle_fhirpath(condition, None, s_source, condition=True)
        return result[0]

    def _handle_source(self, s_source):
        indent = 0
        just_expected = False
        expected_type = None
        if s_source.get_type() and s_source.get_type().value:
            expected_type = s_source.get_type().value
            if expected_type == "Resource":
                expected_type = "ResourceContainer"
        if s_source.get_variable():
            src = self._path(s_source, expected_type=expected_type)
            list_mode = s_source.get_listMode()
            in_var = s_source.get_variable().value
            s_type, is_list = self._get_type(src, set_var_type=False)
            if not s_type and s_source.get_element() and s_source.get_element().value in ["dataString", "other", "dataBase64Binary", "xmlText"]:
                # fallback for EN, ...
                s_source.get_element().value = "valueOf_"
                src = self._path(s_source) + ".strip()"
                s_type = str
            self.var_types[in_var] = s_type
            indent += 4
            if s_type and not is_list:
                if in_var == "vvv":
                    s_source.get_variable().value = src
                    if s_type and s_type.__name__ == "ResourceContainer":
                        self._append_py("%s = unpack_container(%s)" % (src, src))
                    self._append_py("if %s:" % src)
                    self.var_types[src] = s_type
                    in_var = src
                else:
                    if s_type and s_type.__name__ == "ResourceContainer":
                        self._append_py("%s = unpack_container(%s)" % (in_var, src))
                    else:
                        self._append_py("%s = %s" % (in_var, src))
                    self._append_py("if %s:" % (in_var))
                self.indent += 4
            else:
                if not list_mode:
                    if in_var == "vvv":
                        elem = s_source.get_element().value
                        if elem in dir(builtins) or elem in self.keyword_list:
                            elem += "_"
                        while elem in self.var_types:
                            elem += "_" # TODO better GC for var_types (once all dependent rules are processed, remove from var_types)
                        else:
                            self.var_types[elem] = s_type
                        in_var = elem
                        s_source.get_variable().value = elem
                    if s_type:
                        self._append_py("for %s in %s or []:" % (in_var, src))
                    else:
                        self._append_py("for %s in (%s if isinstance(%s, list) else ([] if not %s else [%s])):" % tuple([in_var] + ([src] * 4)))
                elif list_mode.value == "first":
                    self._append_py("if len(%s) > 0:" % (src))
                    self._append_py("    %s = %s[0]" % (in_var, src))
                elif list_mode.value == "last":
                    self._append_py("if len(%s) > 0:" % (src))
                    self._append_py("    %s = %s[-1]" % (in_var, src))
                elif list_mode.value == "not_first":
                    self._append_py("for %s in %s[1:]:" % (in_var, src))
                elif list_mode.value == "not_last":
                    self._append_py("for %s in %s[:-1]:" % (in_var, src))
                elif list_mode.value == "only_one":
                    self._append_py("if len(%s) == 1:" % (src))
                    self._append_py("    %s = %s[0]" % (in_var, src))
                else:
                    raise BaseException("Unknown list mode %s" % list_mode.value)
                self.indent += 4
                if s_type and s_type.__name__ == "ResourceContainer":
                    self._append_py("%s = unpack_container(%s)" % (in_var, in_var))
            if expected_type:
                self.expected_types[in_var] = expected_type
                just_expected = True
            else:
                self.expected_types[in_var] = None
        if expected_type:
            if just_expected or (in_var in self.expected_types and self.expected_types[in_var] == expected_type):
                self._append_py("if isinstance(%s, %s.%s):" % (in_var, self.i_module.__name__, expected_type))
                self.var_types[in_var] = getattr(self.i_module, expected_type)
                self.indent += 4
                indent += 4
        if s_source.get_condition():
            condition = self._handle_condition(s_source.get_condition().value, s_source)
            if condition is not None:
                self._append_py("if %s:" % condition)
                self.indent += 4
                indent += 4
        return 0, -1 * indent

    def _handle_source_no_rules(self, s_source):
        if not s_source.get_variable():
            indent = 0
            if s_source.get_condition():
                condition = self._handle_condition(s_source.get_condition().value, s_source)
                if condition is not None:
                    self._append_py("if %s:" % condition)
                    self.indent += 4
                    indent += 4
            return 0, -1 * indent
        else:
            in_var = s_source.get_variable().value
            src = self._path(s_source)
            var_type = self.var_types.get(s_source.get_context().value)
        if var_type:
            elem = s_source.get_element().value
            var_type = getattr(var_type(), elem)
            if isinstance(var_type, list):
                self._append_py("for %s in %s:" % (in_var, src))
                self.indent += 4
                var_type, __ = self._get_type(s_source, set_var_type=False)
                if var_type and var_type.__name__ == "ResourceContainer":
                    self._append_py("%s = unpack_container(%s)" % (in_var, in_var))
                indent = 4
                if s_source.get_type():
                    type_ = s_source.get_type().value
                    if not (in_var in self.expected_types and self.expected_types[in_var] == type_):
                        self._append_py("if isinstance(%s, %s.%s):" % (in_var, self.i_module.__name__, type_))
                        self.var_types[in_var] = getattr(self.i_module, type_)
                        self.indent += 4
                        indent += 4
                if s_source.get_condition():
                    condition = self._handle_condition(s_source.get_condition().value, s_source)
                    if condition is not None:
                        self._append_py("if %s:" % condition)
                        self.indent += 4
                        indent += 4
                return 0, -1 * indent
            else:
                var_type, __ = self._get_type(s_source, set_var_type=False)
                if var_type and var_type.__name__ == "ResourceContainer":
                    self._append_py("%s = unpack_container(%s)" % (in_var, src))
                else:
                    self._append_py("%s = %s" % (in_var, src))
                self._append_py("if %s:" % in_var)
                self.indent += 4
                indent = 4
                if s_source.get_type():
                    type_ = s_source.get_type().value
                    if not (in_var in self.expected_types and self.expected_types[in_var] == type_):
                        self._append_py("if isinstance(%s, %s.%s):" % (in_var, self.i_module.__name__, type_))
                        self.var_types[in_var] = getattr(self.i_module, type_)
                        self.indent += 4
                        indent += 4
                if s_source.get_condition():
                    condition = self._handle_condition(s_source.get_condition().value, s_source)
                    if condition is not None:
                        self._append_py("if %s:" % condition)
                        self.indent += 4
                        indent += 4
                return 0, -1 * indent
        else:
            self._append_py("# could not check if list (norules)")
            self._append_py("for %s in (%s if isinstance(%s, list) else ([] if not %s else [%s])):" % tuple([in_var] + ([src] * 4)))
            self.indent += 4
            var_type, __ = self._get_type(s_source, set_var_type=False)
            if var_type and var_type.__name__ == "ResourceContainer":
                self._append_py("%s = unpack_container(%s)" % (in_var, src))
            else:
                self._append_py("%s = %s" % (in_var, src))
            indent = 4
            if s_source.get_type():
                type_ = s_source.get_type().value
                if not (in_var in self.expected_types and self.expected_types[in_var] == type_):
                    self._append_py("if isinstance(%s, %s.%s):" % (in_var, self.i_module.__name__, type_))
                    self.var_types[in_var] = getattr(self.i_module, type_)
                    self.indent += 4
                    indent += 4
            if s_source.get_condition():
                condition = self._handle_condition(s_source.get_condition().value, s_source)
                if condition is not None:
                    self._append_py("if %s:" % condition)
                    self.indent += 4
                    indent += 4
            return 0, -1 * indent

    def _get_out_var(self, out_var):
        if out_var in self.list_var_resolved:
            return "_" + out_var
        else:
            return out_var

    def _handle_target_assign(self, s_map_source, s_map_target):
        if s_map_target.get_variable():
            out_var = self._get_out_var(s_map_target.get_variable().value)
            trg = self._path(s_map_target)
            var_type, is_list = self._get_type(s_map_target)
        else:
            out_var = self._path(s_map_target)
            if s_map_source.get_variable():
                trg = self._get_out_var(s_map_source.get_variable().value)
            else:
                trg = self._path(s_map_source)
            var_type, is_list = self._get_type(s_map_source)
        shared_rule_id = None
        if s_map_target.get_listMode() and s_map_target.get_listMode()[0].value == "share":
            shared_rule_id = s_map_target.get_listRuleId().value
            self._append_py("if '%s' in shared_vars:" % shared_rule_id)
            self._append_py("    %s = shared_vars['%s']" % (out_var, shared_rule_id))
            self._append_py("else:")
            self.indent += 4
        if not var_type:
            self._append_py("%s = %s # unknown type" % (out_var, trg))
        else:
            if is_list:
                self._append_py("%s = %s()" % (out_var, var_type.__module__ + "." + var_type.__name__))
                self._append_py("%s.append(%s)" % (trg, out_var))
            elif out_var == trg:
                self._append_py("%s = %s()" % (trg, var_type.__module__ + "." + var_type.__name__))
            else:
                self._append_py("if %s is None:" % trg)
                self._append_py("    %s = %s()" % (trg, var_type.__module__ + "." + var_type.__name__))
                self._append_py("%s = %s" % (out_var, trg))
        if shared_rule_id:
            self.indent -= 4
            self._append_py("    shared_vars['%s'] = %s" % (shared_rule_id, out_var))

    def _handle_target_cast(self, s_map_target):
        out_var = self._get_out_var(s_map_target.get_variable().value) if s_map_target.get_variable() else None
        in_var = self._get_out_var(s_map_target.get_parameter()[0].valueId.value)
        out_type = s_map_target.get_parameter()[1].valueString.value
        trg = self._path(s_map_target)
        var_type, __ = self._get_type(s_map_target)
        var_type_name = var_type.__name__ if var_type else None
        if not var_type:
            elems = {}
            if s_map_target.get_element():
                ctxType = self.var_types.get(s_map_target.get_context().value)
                for name, elem_type in inspect.get_annotations(ctxType.__init__).items():
                    if name.startswith(s_map_target.get_element().value):
                        elems[elem_type] = name
            elem = elems.get(out_type)
            if elem:
                trg = self._get_out_var(s_map_target.get_context().value) + "." + elem
                var_type_name = out_type
        # TODO implement other types: https://github.com/hapifhir/org.hl7.fhir.core/blob/890737e17b6922e7fe2bf5674675251dd258994b/org.hl7.fhir.r5/src/main/java/org/hl7/fhir/r5/utils/structuremap/StructureMapUtilities.java#L1822
        if out_type == "string":
            if var_type_name == "datetime":
                out_transform = "dateutil.parse(str(%s))" % in_var
            elif var_type_name == "dateString":
                out_transform = "dateutil.parse(str(%s)).isoformat()" % in_var
            elif var_type_name == "dateTime":
                out_transform = "dateTime(value=dateutil.parse(%s).isoformat())" % in_var
            elif var_type_name == "str":
                out_transform = in_var
            elif var_type_name == "int":
                out_transform = "str(%s)" % in_var
            elif var_type_name in ["string", "code"]:
                if hasattr(self._get_module(var_type), "string"):
                    out_transform = "string(value=str(%s))" % in_var
                else:
                    out_transform = in_var
            else:
                if hasattr(self._get_module(var_type), "string"):
                    out_transform = "string(value=str(%s)) # unknown cast %s -> string" % (in_var, var_type_name)
                else:
                    out_transform = "%s # unknown cast %s -> string" % (in_var, var_type_name)
            if out_var:
                self._append_py("%s = %s" % (out_var, out_transform))
                out_transform = out_var
            self._append_py("%s = %s" % (trg, out_transform))
        else:
            raise NotImplementedError("Unsupported cast %s -> %s (%s = %s)" % (var_type_name, out_type, trg, in_var))

    def _handle_target_uuid(self, s_map_target):
        trg = self._path(s_map_target)
        out_var = s_map_target.get_variable()
        if out_var:
            out_var = self._get_out_var(out_var.value)
            if hasattr(self.o_module, "string"):
                self._append_py("%s = string(value=%s)" % (out_var, self.uuid_method))
            else:
                self._append_py("%s = %s" % (out_var, self.uuid_method))
            self._append_py("%s = %s" % (trg, out_var))
            self.var_types[s_map_target.get_variable().value] = self.o_module.string
        else:
            if hasattr(self.o_module, "string"):
                self._append_py("%s = string(value=%s)" % (trg, self.uuid_method))
            else:
                self._append_py("%s = %s" % (trg, self.uuid_method))
        self.var_types[self._path(s_map_target, orig_var=True)] = self.o_module.string

    def _handle_target_append(self, s_map_target):
        out_var = self._get_out_var(s_map_target.get_variable().value) if s_map_target.get_variable() else None
        trg = self._path(s_map_target)
        var_type, is_list = self._get_type(s_map_target)
        var_type_name = var_type.__name__ if var_type else None
        params = []
        for param in s_map_target.get_parameter():
            if param.valueString:
                params.append("'%s'" % param.valueString.value)
            elif param.valueId:
                param_type, is_list_src = self._get_type(param.valueId.value, set_var_type=False)
                param_type = param_type.__name__ if param_type else None
                param = self._get_out_var(param.valueId.value)
                if param_type == "StrucDoc_Text":
                    params.append("%s.valueOf_" % (param))
                elif param_type == "TS":
                    params.append("%s.value" % (param))
                elif param_type == "id":
                    params.append("%s.value" % (param))
                elif param_type == "ST":
                    params.append(param) # params.append("%s.valueOf_" % (param))
                elif param_type == "str":
                    params.append(param)
                elif param_type == "string":
                    params.append("%s.value" % (param))
                else:
                    # TODO: add warning
                    params.append("getattr(%s, 'value', %s or '')" % (param, param))
            else:
                params.append("'unknown append type %s'" % param)
        if var_type_name == "string":
            if hasattr(self._get_module(var_type), "string"):
                out_transform = "string(value=(%s))" % " + ".join(params)
            else:
                out_transform = " + ".join(params)
        elif var_type_name == "dateString":
            if hasattr(utils.get_module(var_type), "string"):
                out_transform = "string(value=(%s))" % " + ".join(params)
            else:
                out_transform = " + ".join(params)
        elif var_type_name == "uri":
            out_transform = "uri(value=(%s))" % " + ".join(params)
        elif var_type_name == "div":
            out_transform = "utils.builddiv(%s, %s)" % (self.o_module.__name__, " + ".join(params))
        elif var_type_name == "str":
            out_transform = " + ".join(params)
        else:
            raise NotImplementedError("Unsupported type %s for append" % var_type_name)
        if out_var:
            self._append_py("%s = %s" % (out_var, out_transform))
            out_transform = out_var
        self._append_py("%s = %s" % (trg, out_transform))

    def _handle_target_copy(self, s_map_source, s_map_target):
        out_var = self._get_out_var(s_map_target.get_variable().value) if s_map_target.get_variable() else None
        src = s_map_target.get_parameter()[0]
        if s_map_target.get_context():
            var_type, is_list = self._get_type(s_map_target)
        elif src.valueId:
            var_type, is_list = self._get_type(src.valueId.value, set_var_type=False)
        var_type_name = var_type.__name__ if var_type else None
        if src.valueString:
            trg = self._path(s_map_target, expected_type="string")
            if var_type_name is None:
                var_type, is_list = self._get_type(trg)
                var_type_name = var_type.__name__ if var_type else None
            # TODO add support for other types
            if var_type_name in ["string", "code", "canonical"]:
                if hasattr(self._get_module(var_type), "string"):
                    out_transform = "string(value='%s')" % src.valueString.value
                else:
                    out_transform = "'%s'" % src.valueString.value
            elif var_type_name == "markdown":
                out_transform = "%s.markdown(value='%s')" % (self._get_module(var_type).__name__, src.valueString.value)
            elif var_type_name == "uri":
                out_transform = "uri(value='%s')" % src.valueString.value
            elif var_type_name == "str":
                out_transform = "'%s'" % src.valueString.value
            elif var_type_name == "bool":
                out_transform = src.valueString.value.title()
            elif var_type_name == "boolean":
                out_transform = "boolean(value=%s)" % src.valueString.value.title()
            elif var_type_name == "int":
                out_transform = src.valueString.value
            elif var_type_name == "decimal":
                out_transform = "decimal(value=%s)" % src.valueString.value
            elif var_type_name == "dateTime":
                out_transform = "dateTime(value='%s')" % src.valueString.value
            elif var_type_name == "dateString":
                out_transform = "'%s'" % src.valueString.value
            elif var_type_name == "datetime":
                out_transform = "'%s'" % src.valueString.value
            elif var_type_name == "ST":
                out_transform = "'%s'" % src.valueString.value
            elif var_type_name == "BL":
                out_transform = "%s" % src.valueString.value.title()
            elif var_type_name == "StrucDoc_Text":
                out_transform = "%s.StrucDoc_Text(value='%s')" % (self.o_module.__name__, str(src.valueString.value))
            elif var_type_name == "URL":
                out_transform = "'%s'" % src.valueString.value
            elif var_type_name == "CS":
                out_transform = "'%s'" % src.valueString.value
            elif var_type_name and inspect.get_annotations(var_type.__init__).get("value", "") == var_type_name + "Enum":
                if hasattr(self._get_module(var_type), "string"):
                    out_transform = "string(value='%s')" % src.valueString.value
                else:
                    out_transform = "'%s'" % src.valueString.value
            elif var_type_name is None:
                if hasattr(self.o_module, "string"):
                    out_transform = "string(value='%s')" % src.valueString.value
                else:
                    out_transform = "'%s'" % src.valueString.value
            elif issubclass(var_type, str):
                out_transform = "'%s'" % src.valueString.value
            else:
                raise NotImplementedError("Unsupported type %s for copy string (%s = '%s')" % (var_type_name, trg, src.valueString.value))
        elif src.valueBoolean:
            trg = self._path(s_map_target, expected_type="boolean")
            if var_type_name is None:
                var_type, is_list = self._get_type(trg)
                var_type_name = var_type.__name__ if var_type else None
            if var_type_name == "bool":
                out_transform = str(src.valueBoolean.value)
            elif var_type_name == "boolean":
                out_transform = "boolean(value=%s)" % str(src.valueBoolean.value)
            elif var_type_name == "BL":
                out_transform = "%s.BL(value=%s)" % (self.o_module.__name__, str(src.valueBoolean.value))
            else:
                raise NotImplementedError("Unsupported type %s for copy boolean (%s = %s)" % (var_type_name, trg, src.valueBoolean.value))
        elif src.valueInteger:
            trg = self._path(s_map_target, expected_type="integer")
            if var_type_name is None:
                var_type, is_list = self._get_type(trg)
                var_type_name = var_type.__name__ if var_type else None
            if var_type_name == "int":
                out_transform = str(src.valueInteger.value)
            elif var_type_name == "integer":
                out_transform = "integer(value=%s)" % str(src.valueInteger.value)
            elif var_type_name == "decimal":
                out_transform = "%s.decimal(value=%s)" % (self.o_module.__name__, str(src.valueInteger.value))
            else:
                raise NotImplementedError("Unsupported type %s for copy integer (%s = %s)" % (var_type_name, trg, src.valueInteger.value))
        elif src.valueId:
            if s_map_target.get_context():
                trg = self._path(s_map_target, expected_type=None)
                src_type, is_list_src = self._get_type(src.valueId.value, set_var_type=False)
                src_type_name = src_type.__name__ if src_type else None
                src = self._get_out_var(src.valueId.value)
            else:
                trg = src.valueId.value
                src_type, is_list_src = self._get_type(s_map_source, set_var_type=False)
                src_type_name = src_type.__name__ if src_type else None
                src = self._path(s_map_source, expected_type=None)
            if not var_type_name:
                elems = {}
                if s_map_target.get_element():
                    ctxType = self.var_types.get(s_map_target.get_context().value)
                    for name, elem_type in inspect.get_annotations(ctxType.__init__).items():
                        if name.startswith(s_map_target.get_element().value):
                            elems[elem_type] = name
                elem = elems.get(src_type_name)
                if not elem and src_type_name in ["str", "TS"]:
                    elem = elems.get("dateTime")
                    src_type_name = "dateTime"
                if elem:
                    trg = self._get_out_var(s_map_target.get_context().value) + "." + elem
                    var_type_name = src_type_name
                elif s_map_target.get_element().value == "xmlText":
                    var_type_name = "string"
            if var_type_name in ["str", "string"]:
                if src_type_name == "str":
                    if var_type_name == "string" and hasattr(self._get_module(var_type), "string"):
                        out_transform = "string(value=%s)" % src
                    else:
                        out_transform = src
                elif src_type_name == "string":
                    if var_type_name == "string" and hasattr(self._get_module(var_type), "string"):
                        out_transform = src
                    else:
                        out_transform = "%s.value" % src
                elif src_type_name in ["uri", "markdown", "canonical", "id", "code", "base64Binary", "url"]:
                    if var_type_name == "string" and hasattr(self._get_module(var_type), "string"):
                        out_transform = "string(value=%s.value)" % src
                    else:
                        out_transform = "%s.value" % src
                elif src_type_name == "ST":
                    if var_type_name == "string" and hasattr(self._get_module(var_type), "string"):
                        out_transform = "(string(value=%s) if isinstance(%s, str) else string(value=%s.valueOf_))" % (src, src, src)
                    else:
                        out_transform = "(%s if isinstance(%s, str) else %s.valueOf_)" % (src, src, src)
                elif src_type_name == "CS":
                    if var_type_name == "string" and hasattr(self._get_module(var_type), "string"):
                        out_transform = "(string(value=%s) if isinstance(%s, str) else string(value=%s.code))" % (src, src, src)
                    else:
                        out_transform = "%s.code" % src
                elif src_type_name == "TEL":
                    if var_type_name == "string" and hasattr(self._get_module(var_type), "string"):
                        out_transform = "string(value=%s.code)" % src
                    else:
                        out_transform = "%s.code" % src
                elif src_type_name == "StrucDoc_Text":
                    if var_type_name == "string" and hasattr(self._get_module(var_type), "string"):
                        out_transform = "string(value=%s.valueOf_)" % src
                    else:
                        out_transform = "%s.valueOf_" % src
                elif src_type_name and inspect.get_annotations(src_type.__init__).get("value", "") == src_type_name + "Enum":
                    if var_type_name == "string" and hasattr(self._get_module(var_type), "string"):
                        out_transform = "string(value=%s.value)" % src
                    else:
                        out_transform = "%s.value" % src
                elif src_type_name is None:
                    if var_type_name == "string" and hasattr(self.o_module, "string"):
                        out_transform = "(string(value=%s) if isinstance(%s, str) else string(value=%s.value))" % (src, src, src)
                    else:
                        out_transform = "%s" % src
                else:
                    raise BaseException("Unknown source type '%s' for copy string" % src_type_name)
            elif var_type_name == "dateTime":
                out_transform = "dateTime(value=dateutil.parse(%s).isoformat())" % src
            elif var_type_name == "code":
                if hasattr(self._get_module(var_type), "string"):
                    out_transform = "string(value=%s)" % src
                else:
                    out_transform = src
            elif var_type_name == "bool":
                if hasattr(self.i_module, "boolean"):
                    out_transform = "%s.value" % src
                else:
                    out_transform = src
            elif var_type_name == "int":
                if hasattr(self.i_module, "integer"):
                    out_transform = "%s.value" % src
                else:
                    out_transform = src
            elif var_type_name == "integer":
                out_transform = "%s.integer(value=%s)" % (self.o_module.__name__, src)
            elif var_type_name == "unsignedInt":
                out_transform = "%s.unsignedInt(value=%s)" % (self.o_module.__name__, src)
            elif var_type_name == "decimal":
                out_transform = "%s.decimal(value=%s)" % (self.o_module.__name__, src)
            elif var_type_name == "datetime":
                if hasattr(utils.get_module(src_type), "dateTime"):
                    out_transform = "%s.value" % src
                else:
                    out_transform = src
            elif var_type_name == "dateString":
                if hasattr(utils.get_module(src_type), "dateTime"):
                    out_transform = "%s.value" % src
                else:
                    out_transform = src
            elif var_type_name == "markdown":
                if src_type_name == "ED":
                    out_transform = "utils.ed2markdown(%s, %s)" % (self.o_module.__name__, src)
                elif src_type_name == "StrucDoc_Text":
                    out_transform = "utils.strucdoctext2markdown(%s, %s)" % (self.o_module.__name__, src)
                elif src_type_name == "str":
                    out_transform = "markdown(value=%s)" % src
                else:
                    raise BaseException("Unknown source type '%s' for copy markdown" % src_type_name)
            elif var_type_name == "div":
                if src_type_name == "StrucDoc_Text":
                    out_transform = "utils.strucdoctext2html(%s, %s)" % (self.o_module.__name__, src)
                elif src_type_name == "ED":
                    out_transform = "utils.ed2html(%s, %s)" % (self.o_module.__name__, src)
                else:
                    out_transform = "string(value=%s) # unknown source type for div %s" % (src, src_type_name)
            elif var_type_name == "URL":
                if src_type_name == "url":
                    out_transform = "%s.value" % src
                else:
                    out_transform = src
            elif var_type_name == "Decimal":
                if src_type_name == "decimal":
                    out_transform = "%s.value" % src
                else:
                    out_transform = src
            else:
                out_transform = src
        else:
            trg = self._path(s_map_target, expected_type=None)
            raise NotImplementedError("Unsupported parameter type for copy (%s = ?)" % trg)
        if out_var:
            self._append_py("%s = %s" % (out_var, out_transform))
            out_transform = out_var
        if is_list:
            self._append_py("%s.append(%s)" % (trg, out_transform))
        else:
            self._append_py("%s = %s" % (trg, out_transform))

    def _handle_target_reference(self, s_map_target):
        out_var = self._get_out_var(s_map_target.get_variable().value) if s_map_target.get_variable() else None
        src = self._get_out_var(s_map_target.get_parameter()[0].valueId.value)
        trg = self._path(s_map_target)
        var_type, is_list = self._get_type(s_map_target)
        self._append_py(f"if not {src}.id:")
        self._append_py(f"    {src}.id = string(value={self.uuid_method})")
        out_transform = f"string(value=type({src}).__name__ + '/' + {src}.id.value)"
        if out_var:
            self._append_py("%s = %s" % (out_var, out_transform))
            out_transform = out_var
        if is_list:
            self._append_py("%s.append(%s)" % (trg, out_transform))
        else:
            self._append_py("%s = %s" % (trg, out_transform))

    def _handle_target_truncate(self, s_map_target):
        out_var = self._get_out_var(s_map_target.get_variable().value) if s_map_target.get_variable() else None
        trg = self._path(s_map_target)
        var_type, is_list = self._get_type(s_map_target)
        var_type_name = var_type.__name__ if var_type else None
        srcId = self._get_out_var(s_map_target.get_parameter()[0].valueId.value)
        param_type, is_list_src = self._get_type(srcId, set_var_type=False)
        param_type = param_type.__name__ if param_type else None
        if param_type == "StrucDoc_Text":
            param = "%s.valueOf_" % (srcId)
        elif param_type == "TS":
            param = srcId # "%s.value" % (srcId)
        elif param_type == "string" or param_type == "str":
            param = "('' if %s is None else %s if isinstance(%s, str) else %s.value)" % tuple([srcId] * 4)
        elif param_type == "dateStringV3":
            param = "('' if %s is None else str(dateutil.parse(%s if isinstance(%s, str) else %s.value).isoformat()))" % tuple([srcId] * 4)
        else:
            # TODO: add warning
            param = srcId
        srcLen = s_map_target.get_parameter()[1].valueInteger.value
        param += "[:%s]" % srcLen
        if var_type_name == "string" or var_type_name == "dateString":
            if hasattr(self._get_module(var_type), "string"):
                out_transform = "%s.string(value=(%s))" % (self.o_module.__name__, param)
            else:
                out_transform = param
        elif var_type_name == "date":
            out_transform = "%s.date(value=(%s))" % (self.o_module.__name__, param)
        elif var_type_name == "uri":
            out_transform = "%s.uri(value=(%s))" % (self.o_module.__name__, param)
        else:
            raise NotImplementedError("Unsupported type %s for truncate" % var_type_name)
        if out_var:
            self._append_py("%s = %s" % (out_var, out_transform))
            out_transform = out_var
        if is_list:
            self._append_py("%s.append(%s)" % (trg, out_transform))
        else:
            self._append_py("%s = %s" % (trg, out_transform))

    def _handle_target_pointer(self, s_map_target):
        out_var = self._get_out_var(s_map_target.get_variable().value) if s_map_target.get_variable() else None
        src = self._get_out_var(s_map_target.get_parameter()[0].valueId.value)
        trg = self._path(s_map_target)
        var_type, is_list = self._get_type(s_map_target)
        # TODO assign random UUID to id if None?
        out_transform = f"string(value='urn:uuid:' + {src}.id.value)"
        if out_var:
            self._append_py("%s = %s" % (out_var, out_transform))
            out_transform = out_var
        if is_list:
            self._append_py("%s.append(%s)" % (trg, out_transform))
        else:
            self._append_py("%s = %s" % (trg, out_transform))

    def _handle_target_cc(self, s_map_target):
        out_var = self._get_out_var(s_map_target.get_variable().value) if s_map_target.get_variable() else None
        trg = self._path(s_map_target)
        var_type, is_list = self._get_type(s_map_target)
        params = []
        for param in s_map_target.get_parameter():
            if param.valueId:
                param = self._get_out_var(param.valueId.value)
                param = f"({param} if isinstance({param}, str) else {param}.value)"
            else:
                param = f"'{param.valueString.value}'"
            params.append(param)
        mod = self.o_module.__name__
        if len(params) == 1:
            out_transform = f"{mod}.CodeableConcept(text={mod}.string(value={params[0]}))"
        else:
            type_param = f", display={mod}.string(value={params[2]})" if len(params) > 2 else ""
            out_transform = f"{mod}.CodeableConcept(coding=[{mod}.Coding(system={mod}.uri(value={params[0]}), code={mod}.string(value={params[1]}){type_param})])"
        if out_var:
            self._append_py("%s = %s" % (out_var, out_transform))
            out_transform = out_var
        if is_list:
            self._append_py("%s.append(%s)" % (trg, out_transform))
        else:
            self._append_py("%s = %s" % (trg, out_transform))

    def _handle_target_c(self, s_map_target):
        out_var = self._get_out_var(s_map_target.get_variable().value) if s_map_target.get_variable() else None
        trg = self._path(s_map_target)
        var_type, is_list = self._get_type(s_map_target)
        params = []
        for param in s_map_target.get_parameter():
            if param.valueId:
                param = self._get_out_var(param.valueId.value)
                param = f"({param} if isinstance({param}, str) else {param}.value)"
            else:
                param = f"'{param.valueString.value}'"
            params.append(param)
        mod = self.o_module.__name__
        type_param = f", display={mod}.string(value={params[2]})" if len(params) > 2 else ""
        out_transform = f"{mod}.Coding(system={mod}.uri(value={params[0]}), code={mod}.string(value={params[1]}){type_param})"
        if out_var:
            self._append_py("%s = %s" % (out_var, out_transform))
            out_transform = out_var
        if is_list:
            self._append_py("%s.append(%s)" % (trg, out_transform))
        else:
            self._append_py("%s = %s" % (trg, out_transform))

    def _handle_target_id(self, s_map_target):
        out_var = self._get_out_var(s_map_target.get_variable().value) if s_map_target.get_variable() else None
        trg = self._path(s_map_target)
        var_type, is_list = self._get_type(s_map_target)
        params = []
        for param in s_map_target.get_parameter():
            if param.valueId:
                param = self._get_out_var(param.valueId.value)
                param = f"({param} if isinstance({param}, str) else {param}.value)"
            else:
                param = f"'{param.valueString.value}'"
            params.append(param)
        mod = self.o_module.__name__
        type_param = f", type_={mod}.CodeableConcept(coding=[{mod}.Coding(system={mod}.uri(value='http://terminology.hl7.org/3.1.0/CodeSystem-v2-0203'), code={mod}.string(value={params[2]}))])" if len(params) > 2 else ""
        out_transform = f"{mod}.Identifier(system={mod}.uri(value={params[0]}), value={mod}.string(value={params[1]}){type_param})"
        if out_var:
            self._append_py("%s = %s" % (out_var, out_transform))
            out_transform = out_var
        if is_list:
            self._append_py("%s.append(%s)" % (trg, out_transform))
        else:
            self._append_py("%s = %s" % (trg, out_transform))

    def _handle_target_qty(self, s_map_target):
        out_var = self._get_out_var(s_map_target.get_variable().value) if s_map_target.get_variable() else None
        trg = self._path(s_map_target)
        var_type, is_list = self._get_type(s_map_target)
        params = []
        for param in s_map_target.get_parameter():
            if param.valueId:
                param = self._get_out_var(param.valueId.value)
                param = f"({param} if isinstance({param}, str) else {param}.value)"
            else:
                param = f"'{param.valueString.value}'"
            params.append(param)
        mod = self.o_module.__name__
        if len(params) == 1:
            out_transform=f"utils.qty_from_str({mod}, {param})"
        else:
            system_code = f", system={mod}.uri(value={params[2]}), code={mod}.string(value={params[3]})" if len(params) > 2 else ""
            out_transform = f"{mod}.Quantity(value={mod}.decimal(value={params[0]}), unit={mod}.string(value={params[1]}){system_code})"
        if out_var:
            self._append_py("%s = %s" % (out_var, out_transform))
            out_transform = out_var
        if is_list:
            self._append_py("%s.append(%s)" % (trg, out_transform))
        else:
            self._append_py("%s = %s" % (trg, out_transform))

    def _handle_target_cp(self, s_map_target):
        out_var = self._get_out_var(s_map_target.get_variable().value) if s_map_target.get_variable() else None
        trg = self._path(s_map_target)
        var_type, is_list = self._get_type(s_map_target)
        params = []
        for param in s_map_target.get_parameter():
            if param.valueId:
                param = self._get_out_var(param.valueId.value)
                param = f"({param} if isinstance({param}, str) else {param}.value)"
            else:
                param = f"'{param.valueString.value}'"
            params.append(param)
        mod = self.o_module.__name__
        if len(params) == 1:
            out_transform = f"{mod}.ContactPoint(value={mod}.string(value={params[0]}))"
        else:
            out_transform = f"{mod}.ContactPoint(system={mod}.uri(value={params[0]}), value={mod}.string(value={params[1]}))"
        if out_var:
            self._append_py("%s = %s" % (out_var, out_transform))
            out_transform = out_var
        if is_list:
            self._append_py("%s.append(%s)" % (trg, out_transform))
        else:
            self._append_py("%s = %s" % (trg, out_transform))

    def _handle_fhirpath(self, s_value, var_type_, this=None, target_list=False, condition=False):
        lists = {}
        this_elem = {}
        var_types = dict(self.var_types)
        if this:
            src = self._path(this)
            src_type, src_list = self._get_type(this, set_var_type=False)
            for elem, type_str in inspect.get_annotations(src_type.__init__).items():
                this_elem[elem] = utils.get_type(src_type, elem)
            var_types["$this"] = src_type
            lists["$this"] = src_list
            var_types[src.split(".")[-1]] = src_type
            lists[src.split(".")[-1]] = src_list
            in_var = this.get_variable().value if this.get_variable() else None
            if in_var:
                src = in_var
        else:
            src = None
            src_list = False

        generator = fhirpath.parseString(s_value)
        ctx = fhirpath.FHIRPathContext(var_types, self.list_var, self.o_module if getattr(self.o_module, "string", None) else self.i_module, src, this_elem)
        py_code = generator.convert(context=ctx)

        if target_list:
            result = generator._get_new_varname()
        else:
            result = py_code.code
            comp = ast.parse(result, mode="eval")
            if result.startswith("['") and result.endswith("']"):
                result = result[1:-1]
            elif condition and result.startswith("[bool("):
                result = result[6:-2]
            elif condition and re.search("^\[\(*bool\(", result):
                result = result[1:-1]
            elif condition and (result.endswith("is None)]") or result.endswith("is not None)]")):
                result = result[2:-2]
            elif condition and result.startswith("fhirpath_utils.bool_not([bool("):
                result = f"not {result[30:-3]}"
            elif condition and result.startswith("[("):
                if len(comp.body.elts) == 1 and isinstance(comp.body.elts[0], ast.BoolOp):
                    result = result[2:-2]
                elif len(comp.body.elts) == 1 and isinstance(comp.body.elts[0], ast.Call) and isinstance(comp.body.elts[0].func.value, ast.BoolOp):
                    result = result[1:-1]
                else:
                    result = "fhirpath.single(%s)" % result
            elif condition and isinstance(comp.body, ast.List) and len(comp.body.elts) == 1 and isinstance(comp.body.elts[0], ast.Compare):
                result = result[1:-1]
            elif result.startswith("[all(") or result.startswith("[bool(") or result.startswith("[len("):
                result = result[1:-1]
            elif result.startswith("[not("):
                result = f"not {result[5:-2]}"
            elif result.startswith("["):
                if isinstance(comp.body, ast.List) and len(comp.body.elts) == 1:
                    result = result[1:-1]
                else:
                    result = "fhirpath.single(%s)" % result
            else:
                result = "fhirpath.single(%s)" % result

        if condition:
            return result, None, None

        if not var_type_:
            # TODO improve type support
            out_type = py_code.out_type
            out_type_name = out_type.__name__ if out_type else None
            if out_type_name in ["str", "string"]:
                out_type = getattr(self.o_module, "string")
                var_type_name = "string"
            elif out_type_name == "boolean" or out_type_name == "bool":
                out_type = getattr(self.o_module, "boolean")
                var_type_name = "boolean"
            elif out_type_name == "dateTime" or out_type_name == "datetime":
                out_type = getattr(self.o_module, "dateTime")
                var_type_name = "dateTime"
            else:
                var_type_name = out_type_name
        else:
            out_type = var_type_
            value_annotation = inspect.get_annotations(var_type_.__init__).get("value", "")
            if value_annotation == var_type_.__name__ + "Enum":
                var_type_name = "enum"
            else:
                var_type_name = var_type_.__name__

        # TODO improve type support
        if var_type_name == "uri":
            target_value = 'uri(value=%s)' % result
        elif var_type_name == "enum":
            if py_code.out_type == str:
                target_value = "%s.%s(value=%s)" % (out_type.__module__, out_type.__name__, result)
            elif py_code.out_type == getattr(self.o_module, "string"):
                target_value = "%s.%s(value=%s.value)" % (out_type.__module__, out_type.__name__, result)
            else:
                target_value = "%s.%s(value=str(%s))" % (out_type.__module__, out_type.__name__, result)
        elif var_type_name == "string":
            if py_code.out_type == str:
                target_value = "string(value=%s)" % result
            elif py_code.out_type == getattr(self.o_module, "string"):
                target_value = result
            else:
                target_value = "string(value=str(%s))" % result
        elif var_type_name == "id":
            if py_code.out_type == str:
                target_value = "%s.id(value=%s)" % (self.o_module.__name__, result)
            elif py_code.out_type == getattr(self.o_module, "id"):
                target_value = result
            else:
                target_value = "%s.id(value=str(%s))" % (self.o_module.__name__, result)
        elif var_type_name == "str":
            if py_code.out_type == str:
                target_value = result
            elif py_code.out_type == getattr(self.o_module, "string", str):
                target_value = "%s.value" % result
            else:
                target_value = "str(%s)" % result
        elif var_type_name == "base64Binary":
            target_value = 'base64Binary(value=%s)' % result
        elif var_type_name == "boolean":
            if py_code.out_type == bool:
                target_value = "boolean(value=%s)" % result
            elif py_code.out_type == getattr(self.o_module, "bool", bool):
                target_value = result
            else:
                target_value = "boolean(value=str(%s))" % result
        elif var_type_name == "bool":
            if py_code.out_type == bool:
                target_value = result
            elif py_code.out_type == getattr(self.o_module, "bool", bool):
                target_value = "%s.value" % result
            else:
                target_value = "bool(%s)" % result
        elif var_type_name == "instant":
            if py_code.out_type == datetime.datetime:
                target_value = "%s.instant(value=%s)" % (self.o_module.__name__, result)
            elif py_code.out_type == getattr(self.o_module, "instant", None):
                target_value = result
            else:
                target_value = "%s.instant(value=dateutil.parse(str(%s)))" % (self.o_module.__name__, result)
        elif var_type_name == "dateTime":
            if py_code.out_type == datetime.datetime:
                target_value = "dateTime(value=%s.isoformat())" % result
            elif py_code.out_type == getattr(self.o_module, "dateTime", datetime.datetime):
                target_value = result
            else:
                target_value = "dateTime(value=dateutil.parse(str(%s)).isoformat())" % result
        elif var_type_name == "datetime":
            if py_code.out_type == datetime.datetime:
                target_value = result
            elif py_code.out_type == getattr(self.o_module, "dateTime", datetime.datetime):
                target_value = "dateutil.parse(%s.value)" % result
            else:
                target_value = "dateutil.parse(str(%s))" % result
        elif var_type_name == "code":
            if py_code.out_type == str:
                target_value = "%s.code(value=%s)" % (self.o_module.__name__, result)
            elif py_code.out_type == getattr(self.o_module, "code"):
                target_value = result
            else:
                target_value = "%s.code(value=str(%s))" % (self.o_module.__name__, result)
        elif var_type_name == "markdown":
            if py_code.out_type == str:
                target_value = "%s.markdown(value=%s)" % (self.o_module.__name__, result)
            elif py_code.out_type == getattr(self.o_module, "markdown"):
                target_value = result
            else:
                target_value = "%s.markdown(value=str(%s))" % (self.o_module.__name__, result)
        elif var_type_name == "decimal":
            if py_code.out_type == str:
                target_value = "%s.decimal(value=%s)" % (self.o_module.__name__, result)
            elif py_code.out_type == getattr(self.o_module, "decimal"):
                target_value = result
            else:
                target_value = "%s.decimal(value=str(%s))" % (self.o_module.__name__, result)
        elif var_type_name in ["instant", "INT", "BL", "URL"]:
            target_value = result # TODO:sbe deal with FHIR native types
        else:
            target_value = result

        if target_list:
            if target_value == result:
                return py_code.code, out_type, result
            else:
                return "[%s for %s in %s]" % (target_value, result, py_code.code), out_type, generator._get_new_varname()
        else:
            return target_value, out_type, generator._get_new_varname()

    def _handle_target_evaluate(self, s_map_target):
        out_var = s_map_target.get_variable()
        s_value = s_map_target.get_parameter()[0].valueString.value
        if s_map_target.get_context():
            var_type, is_list = self._get_type(s_map_target)
            var_type_name = var_type.__name__ if var_type else None
            is_list = self._is_list(s_map_target)
        else:
            var_type = None
            var_type_name = None
            is_list = True
        target_value, out_type, var_name = self._handle_fhirpath(s_value, var_type, target_list=is_list)
        if out_var:
            out_var = self._get_out_var(out_var.value)
        if out_type and not var_type_name:
            var_type_name = out_type.__name__
            if out_var:
                self.var_types[s_map_target.get_variable().value] = out_type

        if out_var:
            if is_list:
                self.list_var.add(out_var)
                self.none_check.discard(out_var)
            else:
                self.none_check.add(out_var)
                self.list_var.discard(out_var)
        if not is_list and s_map_target.get_context():
            self.none_check.add(self._path(s_map_target))
            self.list_var.discard(self._path(s_map_target))

        if not s_map_target.get_context():
            self._append_py("%s = %s" % (out_var, target_value))
        elif is_list:
            trg = self._path(s_map_target, expected_type=out_type)
            if out_var:
                self._append_py("%s = %s" % (out_var, target_value))
                target_value = out_var
            self._append_py("for %s in %s:" % (var_name, target_value))
            if var_type and var_type.__name__ == "ResourceContainer":
                var_name = "%s.ResourceContainer(%s=%s)" % (self.o_module.__name__, var_type_name, var_name)
            self._append_py("    %s.append(%s)" % (trg, var_name))
        else:
            self._assign_or_append(s_map_target, self._is_list(s_map_target), target_value, var_type_name, check_none=True)

    def _handle_target_create(self, s_map_source, s_map_target):
        src = self._path(s_map_source)
        src_var = s_map_source.get_variable()
        src_var = self._get_out_var(src_var.value) if src_var else None
        trg = self._path(s_map_target, expected_type=self.expected_types.get(src_var, None))
        src = src_var or src
        out_var = s_map_target.get_variable()
        out_var = self._get_out_var(out_var.value) if out_var else None
        if not s_map_target.get_parameter():
            var_type, is_list = self._get_type(s_map_target, set_var_type=False, source_type=s_map_source)
            source_type, __ = self._get_type(src)
            if var_type:
                var_type_name = var_type.__module__ + "." + var_type.__name__
                if var_type.__name__ in ["ConceptMap", "StructureMap"]:
                    var_type_constructor = f"({var_type_name}.subclass or {var_type_name})"
                else:
                    var_type_constructor = var_type_name
                if is_list:
                    if out_var is not None and out_var != "vvv":
                        self._append_py("%s = %s()" % (out_var, var_type_constructor))
                        self._append_py("%s.append(%s)" % (trg, out_var))
                        trg = out_var
                    else:
                        self._append_py("%s.append(%s())" % (trg, var_type_constructor))
                        trg = trg + "[-1]"
                else:
                    if out_var is not None and out_var != "vvv":
                        self._append_py("%s = %s()" % (out_var, var_type_constructor))
                        self._append_py("%s = %s" % (trg, out_var))
                    else:
                        self._append_py("%s = %s()" % (trg, var_type_constructor))
                if inspect.get_annotations(var_type.__init__).get(
                        "value") == var_type.__name__ + "Enum":  # special handling for required codes in FHIR
                    target_type = getattr(self.o_module, "code")
                    var_type_name = target_type.__module__ + "." + target_type.__name__
                else:
                    var_type_name = None
            else:
                var_type_name = None
            target_type = var_type
            if source_type:
                group_name = self.default_types_maps.get((source_type, target_type))
                if not group_name or group_name in self.default_types_maps_subtypes:
                    self.transform_default_needed = True
                    if var_type_name:
                        self._append_py("transform_default(%s, %s, %s)" % (src, trg, var_type_name))
                    else:
                        self._append_py("transform_default(%s, %s)" % (src, trg))
                else:
                    self._append_py("%s(%s, %s)" % (group_name, src, trg))
            elif var_type_name:
                self.transform_default_needed = True
                self._append_py("transform_default(%s, %s, %s)" % (src, trg, var_type_name))
            else:
                self.transform_default_needed = True
                self._append_py("transform_default(%s, %s)" % (src, trg))
        else:
            type_param = s_map_target.get_parameter()[0].get_valueString().value
            var_type = None
            if type_param == "BackboneElement":
                var_type, is_list = self._get_type(s_map_target, set_var_type=False)
                if var_type is not None:
                    type_param = var_type.__name__
            if var_type is None:
                var_type = getattr(self.o_module, type_param)
            if out_var:
                self.var_types[s_map_target.get_variable().value] = var_type
            self._assign_or_append(s_map_target, self._is_list(s_map_target), "%s.%s()" % (self.o_module.__name__, type_param), type_param)

    def _handle_target_translate(self, s_map_target):
        # TODO handle if param.valueString.value.startswith("#"):
        # TODO check if parameter[0] could sometimes be a valueString instead of valueId.value 
        url = s_map_target.parameter[1].valueString.value
        url = url[1:] if url.startswith("#") else url # TODO:sbe better solution?
        code = s_map_target.parameter[0].valueId.value
        out_type = s_map_target.parameter[2].valueString.value
        if out_type == "CodeableConcept":
            translate = f"translate_multi(url='{url}', code=({code} if isinstance({code}, str) else {code}.value))"
            self.translate_multi_needed = True
        elif out_type in ["Coding", "code", "system", "display", "uri"]:
            self.translate_single_needed = True
            translate = f"translate_single('{url}', ({code} if isinstance({code}, str) else {code}.value), '{out_type}')"
        else: 
            raise BaseException("Following translate output param is unknown: "+out_type)

        if hasattr(self.o_module, "string") and out_type not in ["CodeableConcept", "Coding"]:
            self._assign_or_append(s_map_target, self._is_list(s_map_target), f"string(value={translate})", out_type)
        else:
            self._assign_or_append(s_map_target, self._is_list(s_map_target), translate, out_type)

    def _is_list(self, source_or_target):
        var_type = self.var_types.get(source_or_target.get_context().value)
        if var_type and source_or_target.get_element():
            if source_or_target.get_element().value:
                elem = source_or_target.get_element().value
                if elem in self.keyword_list:
                    elem += "_"
                var_type = getattr(var_type(), elem, None)
            if var_type is not None and isinstance(var_type, list):
                return True
        return False

    def _assign_or_append(self, s_map_target, is_list, py_code, out_type=None, check_none=False):
        trg = self._path(s_map_target, expected_type=out_type)
        out_var = s_map_target.get_variable()
        if out_var:
            out_var = self._get_out_var(out_var.value)
            self._append_py("%s = %s" % (out_var, py_code))
            py_code = out_var
        var_type, __ = self._get_type(s_map_target, set_var_type=False)
        indent = 0
        if is_list and check_none:
            indent += 4
        if var_type and var_type.__name__ == "ResourceContainer":
            py_code = "%s.ResourceContainer(%s=%s)" % (self.o_module.__name__, out_type, py_code)
        if is_list:
            self._append_py((" " * indent) + "%s.append(%s)" % (trg, py_code))
        else:
            self._append_py("%s = %s" % (trg, py_code))

    def _get_type(self, lookup, set_var_type=True, source_type=None):
        if isinstance(lookup, str):
            parts = lookup.split(".")
            context = parts[0]
            element = parts[1] if len(parts) == 2 else None
            variable = None
        else:
            context = lookup.get_context().value
            element = lookup.get_element().value if lookup.get_element() else None
            orig_var = lookup.get_variable().value if lookup.get_variable() else None
            variable = self._get_out_var(orig_var)
        parent_var_type = self.var_types.get(context)
        var_type, is_list = utils.get_type(parent_var_type, element)
        if var_type is None and source_type is not None and source_type.type_ is not None:
            module = utils.get_module(parent_var_type)
            type_name = source_type.type_.value
            var_type, is_list = utils.get_type(parent_var_type, element, type_name)
        if var_type is None and parent_var_type:
            choice_group_names = []
            for base_var_type in inspect.getmro(parent_var_type):
                choice_group_names += getattr(base_var_type, "choice_group_names", [])
            if element in choice_group_names:
                var_type = parent_var_type
                is_list = [] # choice_group
        if variable and set_var_type:
            self.var_types[orig_var] = var_type
        return var_type, is_list

    def _append_py(self, code=""):
        self.py_code += (" " * self.indent) + code + "\n"

    def _path(self, src_or_trg, expected_type=None, orig_var=False):
        elem = src_or_trg.get_element()
        elem_value = elem.value if elem else None
        if elem_value in self.keyword_list:
            elem_value += "_"
        ctx = src_or_trg.get_context()
        if ctx and elem:
            ctx = self._get_out_var(ctx.value) if not orig_var else ctx.value
            elem_type = self._get_type(src_or_trg, set_var_type=False)
            ctx_type = self._get_type(ctx, set_var_type=False)
            if elem_type[1] == []: # choice_group
                return ctx
            if elem_value in ["data", "xmlText"] and ctx_type[0] and elem_value not in inspect.get_annotations(ctx_type[0].__init__):
                elem_value = "valueOf_"
            if ctx_type[0] and not elem_type[0]:
                ex_type = expected_type[0].upper() + expected_type[1:] if expected_type else None
                if expected_type and self._get_type(ctx + "." + elem_value + ex_type, set_var_type=False):
                    elem_value = elem_value + ex_type
                else:
                    try:
                        dummy_instance = ctx_type[0]()
                        for key in dummy_instance.__dict__.keys():
                            if key.endswith("_nsprefix_"):
                                prefix = getattr(dummy_instance, key)
                                if prefix and elem_value.lower() == (prefix + key[:-10]).lower():
                                    elem_value = key[:-10]
                                    break
                    except BaseException:
                        pass
            return ctx + "." + elem_value
        elif elem:
            return elem_value
        else:
            return self._get_out_var(ctx.value) if not orig_var else ctx.value

    def _get_module(self, var_type):
        if var_type:
            return utils.get_module(var_type)
        else:
            return self.o_module


parse, parseEtree, parseString, parseLiteral = parse_factory(supermod)
