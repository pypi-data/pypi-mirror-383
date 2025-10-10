
import sys
import json

from malac.hd import ConvertMaster
from malac.models.fhir import r4, r5
from malac.hd.core.fhir.base.generator.resource import parse_factory

supermod = r5

def value_from_getter_with_key(obj, key, prefix="get_", postfix=""):
    return getattr(obj,prefix+key+postfix)()

class PythonGenerator(supermod.ConceptMap, ConvertMaster):
    from collections import defaultdict

    # While generating the code, the conceptMap_as_6dimension_dict is beeing used. In one at the last steps, a dimension
    # is added at the top of the dictionary. This new dictionary is than beeing used in the generated code and beeing 
    # explained in the following lines.
    #
    # The conceptMap_as_7dimension_dict is a seven dimensional dictionary, for quickly finding the fitting translation
    # All dimensions except the last are optional, so a explicit NONE value will be used as key and 
    # interpreted as the default key, that always will be fitting, no matter what other keys are fitting.
    # If a version is included (purely optional), than the version will be added with a blank before to the key
    #
    # The 0th dimension is mandatory and stating the ConceptMap with its url (including the version).
    #
    # The 1st dimension is optional and stating the SOURCE valueset (including the version), as one conceptMap can only 
    # have a maximum of one SOURCE, this is reserved for MaLaC-HD ability to process multiple ConceptMaps in one output.
    #
    # The 2nd dimension is optional and stating the TARGET valueset (including the version), as one conceptMap can only 
    # have a maximum of one TARGET, this is reserved for MaLaC-HD ability to process multiple ConceptMaps in one output.
    #
    # The 3th dimension is optional and stating the SYSTEM (including the version) from the source valueset code, as one 
    # code could be used in multiple SYSTEMs from the source valueset to translate. 
    # Not stating a SYSTEM with a code, is not FHIR compliant and not a whole concept, but still a valid conceptmap.
    # As many conceptMaps exists that are worngly using this SYSTEM element as stating the valueset, that should be
    # stated in source, this case will still be supported by MaLaC-HD. Having a conceptMap with a source valueset 
    # and a different SYSTEM valueset will result in an impossible match and an error will not be recognized by MaLaC-HD.
    #
    # The 4th dimension is optional and stating the TARGET SYSTEM (including the version) from the target valueset code, as one 
    # code could be used in multiple SYSTEMs from the target valueset to translate. 
    # Not stating a TARGET SYSTEM with a code, is not FHIR compliant and not a whole concept, but still a valid conceptmap.
    # As many conceptMaps exists that are worngly using this TARGET SYSTEM element as stating the target valueset, that should be
    # stated in target, this case will still be supported by MaLaC-HD. Having a conceptMap with a target valueset 
    # and a different TARGET SYSTEM valueset will result in an impossible match and an error will not be recognized by MaLaC-HD.
    #   
    # The 5th dimension is optional and stating the CODE from the source valueset, as one conceptMap can have none or 
    # multiple CODEs from the source to translate. 
    #
    # The 6th dimension is NOT optional and stating the TARGET CODE from the target valueset. As one source code could be translated 
    # in multiple TARGET CODEs, the whole set have to be returend. 
    # For a translation with explicitly no TARGET CODE, because of an quivalence of unmatched or disjoint, NONE will be returned. 
    #   
    # a minimal example, translating "hi" to "servus": 
    # conceptMap_as_7dimension_dict = {"myConMap": {None: {None: {"hi": {None: {None: ["equivalent", "<coding><code>servus</code></coding>", "https://my.concept.map/conceptMap/my"]}}}}}
    #
    # TODO add a dimension for a specific dependsOn property
    # TODO add a solution for the unmapped element
    conceptMap_as_6dimension_dict = None

    def get_key_4_r5relationsship_r4equivalence(self):
        return "relationship"

    def key_4_sourceVS(self):
        return "sourceScope"
    
    def key_4_targetVS(self):
        return "targetScope"
    
    def values_4_translate_match_result_false(self):
        return "['not-related-to']"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
    
    # the source param is not beeing handled, because there are no known possbilities of importing/including conceptMaps in other conceptMaps
    def convert(self, silent=True, return_header_and_footer_for_standalone=True, source=".", return_translate_def=True, return_dict_add=True, model=None):  # TODO:sbe replace source and return_XXX with context/params, to make more generic
        model = model or supermod
        self.py_code = ""
        if return_header_and_footer_for_standalone:
            self._header_standalone(model)
        if return_translate_def:
            self._header_translate_def(model)
        if return_dict_add:
            self.conceptMap_as_6dimension_dict = self.nested_dict(5, list)
            for one_group in self.get_group():
                for one_element in one_group.get_element():
                    for one_target in one_element.get_target():
                        # prepare the match.concept results
                        concept = {}
                        if tmp := one_group.get_target(): concept["system"] = tmp.get_value()
                        #"version": "", # TODO version of codesystem out of url?
                        if tmp := one_target.get_code(): concept["code"] = tmp.get_value()
                        if tmp := one_target.get_display(): concept["display"] = tmp.get_value()
                        #"userSelected": False # Removed, as a Coding from a translation can never been selected by a user

                        # if the concept dict is empty, than skip this broken value and give a warning, that there is a empty group
                        if concept == {}:
                            # TODO do a warning, that it seems like the conceptmap is broken, because there is a empty group
                            continue
                        
                        # create the concept map as a six dimensional dict containing the match.concept results
                        self.conceptMap_as_6dimension_dict \
                            [tmp.get_value() if (tmp := value_from_getter_with_key(self, self.key_4_sourceVS(), postfix="Uri")) or (tmp := value_from_getter_with_key(self, self.key_4_sourceVS(), postfix="Canonical")) else "%"] \
                            [tmp.get_value() if (tmp := value_from_getter_with_key(self, self.key_4_targetVS(), postfix="Uri")) or (tmp := value_from_getter_with_key(self, self.key_4_targetVS(), postfix="Canonical")) else "%"] \
                            [tmp.get_value() if (tmp := one_group.get_source()) else "%"] \
                            [tmp.get_value() if (tmp := one_group.get_target()) else "%"] \
                            [tmp.get_value() if (tmp := one_element.get_code()) else "%"] \
                            .append({self.get_key_4_r5relationsship_r4equivalence():value_from_getter_with_key(one_target, self.get_key_4_r5relationsship_r4equivalence()).get_value(),
                                    "concept": concept,
                                    "source": tmp.get_value() if (tmp := self.get_url()) or (tmp := self.get_id()) else "%"})
                
                if unmapped := one_group.get_unmapped(): # using as many unsafe url characters here, that really should not be used as system id/url or codes of a real codesystem, like [ ] { } | \ ” % ~ # < >
                    tmp_r5relationsship_r4equivalence = ""
                    if model == r5 and unmapped.get_mode().get_value() != "other-map":
                        if tmp := unmapped.get_relationship():
                            tmp_r5relationsship_r4equivalence = tmp.get_value()
                        else:
                            raise BaseException("If the mode in R5 is not 'other-map', relationship inside the unmapped element must be provided, see https://www.hl7.org/fhir/conceptmap-definitions.html#ConceptMap.group.unmapped.relationship")
                    elif model == r4:
                        tmp_r5relationsship_r4equivalence = "inexact"
                    
                    tmp_code = ""
                    tmp_display = ""
                    tmp_code_lvl = ""
                    if unmapped.get_mode().get_value() == "use-source-code":
                        tmp_code_lvl = "|"
                        if model == r4:
                            tmp_r5relationsship_r4equivalence = "equal"
                        tmp_code = "|" + (tmp.get_value() if (tmp := unmapped.get_code()) else "") 
                    elif unmapped.get_mode().get_value() == "fixed":
                        tmp_code_lvl = "~"
                        tmp_code = "~"+unmapped.get_code().get_value() # must be given if fixed
                        tmp_display = unmapped.get_display().get_value() or ""
                    elif unmapped.get_mode().get_value() == "other-map":
                        #tmp_match = "lambda: translate(url="+unmapped.get_url()+", conceptMapVersion=conceptMapVersion, code=code, system=system, version=version, source=source, coding=coding, codeableConcept=codeableConcept, target=target, targetsystem=targetsystem, reverse=reverse, silent=silent)" # cant access the varibales inside the dict...
                        tmp_code_lvl = "#"
                        tmp_code = "#"+unmapped.get_url().get_value()
                    else:
                        raise BaseException(unmapped.get_mode().get_value()+" as mode for unmapped is not defined! Please use the modes from https://hl7.org/fhir/R4B/valueset-conceptmap-unmapped-mode.html .")
                    
                    # prepare the match.concept results
                    concept = {}
                    if tmp := one_group.get_source(): concept["system"] = tmp.get_value()
                    #"version": "", # TODO version of codesystem out of url?
                    if tmp_code: concept["code"] = tmp_code
                    if tmp_display: concept["display"] = tmp_display

                    # if the concept dict is empty, than skip this broken value and give a warning, that there is a empty group
                    if concept == {}:
                        # TODO do a warning, that it seems like the conceptmap is broken, because there is a empty group
                        continue

                    # create the concept map as a six dimensional dict containing the match.concept results
                    self.conceptMap_as_6dimension_dict \
                        [tmp.get_value() if (tmp := value_from_getter_with_key(self, self.key_4_sourceVS(), postfix="Uri")) or (tmp := value_from_getter_with_key(self, self.key_4_sourceVS(), postfix="Canonical")) else "%"] \
                        [tmp.get_value() if (tmp := value_from_getter_with_key(self, self.key_4_targetVS(), postfix="Uri")) or (tmp := value_from_getter_with_key(self, self.key_4_targetVS(), postfix="Canonical")) else "%"] \
                        [tmp.get_value() if (tmp := one_group.get_source()) else "%"] \
                        [tmp.get_value() if (tmp := one_group.get_target()) else "%"] \
                        [tmp_code_lvl] \
                        .append({self.get_key_4_r5relationsship_r4equivalence():tmp_r5relationsship_r4equivalence, 
                                "concept": concept,
                                "source": tmp.get_value() if (tmp := self.get_url()) or (tmp := self.get_id()) else "%"})

            self.py_code += "\n"
            j_dump = json.dumps(self.conceptMap_as_6dimension_dict, indent=4)
            # replace all the json lower case bools to python usual pascal case bools
            j_dump = j_dump.replace(": false",": False").replace(": true",": True")
            self.py_code += 'conceptMap_as_7dimension_dict["'+(tmp.get_value() if (tmp := self.get_url()) or (tmp := self.get_id()) else "%")+'"] = ' + j_dump
            
        if return_header_and_footer_for_standalone:
            self._footer_standalone()

        if not silent:
            print("\n%s" % self.py_code)
        
        return self.py_code

    # from https://stackoverflow.com/a/39819609/6012216
    def nested_dict(self, n, type): 
        if n == 1:
            return self.defaultdict(type)
        else:
            return self.defaultdict(lambda: self.nested_dict(n-1, type))  

    def _header_standalone(self, model):
        self.py_code += f'''import argparse
import time
import {model.__name__}
import sys

description_text = "This has been compiled by the MApping LAnguage Compiler for Health Data, short MaLaC-HD. See arguments for more details."

def init_argparse() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=description_text)
    parser.add_argument(
       '-c', '--code', help="""code --	
The code that is to be translated. If a code is provided, a system must be provided""",
        required=True
    )
    parser.add_argument(
       '-sys', '--system', help="""uri --	
The system for the code that is to be translated""",
        required=True
    )
    parser.add_argument(
       '-ver', '--version', help="""string --	
The version of the system, if one was provided in the source data""",
        required=True
    )
    parser.add_argument(
       '-s', '--source', help="""uri --	
Identifies the value set used when the concept (system/code pair) was chosen. 
May be a logical id, or an absolute or relative location. 
The source value set is an optional parameter because in some cases, the client cannot know what the source value set is. 
However, without a source value set, the server may be unable to safely identify an applicable concept map, 
and would return an error. For this reason, a source value set SHOULD always be provided. 
Note that servers may be able to identify an appropriate concept map without a source value set 
if there is a full mapping for the entire code system in the concept map, or by manual intervention""",
        required=True
    )
    parser.add_argument(
       '-cg', '--coding', help="""Coding --	
A coding to translate""",
        required=True
    )
    parser.add_argument(
       '-cc', '--codeableConcept', help="""CodeableConcept --	
A full codeableConcept to validate. The server can translate any of the coding values (e.g. existing translations) 
as it chooses""",
        required=True
    )
    parser.add_argument(
       '-t', '--target', help="""uri -- 
Identifies the value set in which a translation is sought. May be a logical id, or an absolute or relative location. 
If there's no target specified, the server should return all known translations, along with their source""", 
        required=True
    )
    parser.add_argument(
       '-ts', '--targetsystem', help="""uri -- 
Identifies a target code system in which a mapping is sought. This parameter is an alternative to the target parameter - 
only one is required. Searching for any translation to a target code system irrespective of the context (e.g. target valueset) 
may lead to unsafe results, and it is at the discretion of the server to decide when to support this operation""", 
        required=True
    )
    parser.add_argument(
       '-r', '--reverse', action="store_true", help="""boolean -- True if stated, else False -- 
If this is true, then the operation should return all the codes that might be mapped to this code. 
This parameter reverses the meaning of the source and target parameters""", 
        required=True
    )
    parser.add_argument(
       '-st', '--silent', action="store_true", help="""boolean -- True if stated, else False --
Do not print the converted python mapping to console""", 
        required=True
    )
    return parser
'''
    def _header_translate_def(self, model): 
        self.py_code += f'''
# output
# 1..1 result (boolean)
# 0..1 message with error details for human (string)
# 0..* match with (list)
#   0..1 equivalence/relationship
#   0..1 concept
#       0..1 system
#       0..1 version
#       0..1 code
#       0..1 display 
#       0..1 userSelected will always be false, because this is a translation
#   0..1 source (conceptMap url)
# TODO implement reverse
def translate(url=None, conceptMapVersion=None, code=None, system=None, version=None, source=None, coding=None, codeableConcept=None, target=None, targetsystem=None, reverse=None, silent=False)\
              -> dict [bool, str, list[dict[str, dict[str, str, str, str, bool], str]]]:
    start = time.time()
    
    # start validation and recall of translate in simple from
    if codeableConcept:
        if isinstance(codeableConcept, str): 
            codeableConcept = {model.__name__}.parseString(codeableConcept, silent)
        elif isinstance(coding, {model.__name__}.CodeableConcept):
            pass
        else:
            raise BaseException("The codeableConcept parameter has to be a string or a CodeableConcept Object (called method as library)!")
        # the first fit will be returned, else the last unfitted value will be returned
        # TODO check translate params
        for one_coding in codeableConcept.get_coding:
            if (ret := translate(url=url, source=source, coding=one_coding, 
                                 target=target, targetsystem=targetsystem, 
                                 reverse=reverse, silent=True))[0]:
                return ret
        else: return ret
    elif coding:
        if isinstance(coding, str): 
            coding = {model.__name__}.parseString(coding, silent)
        elif isinstance(coding, {model.__name__}.Coding):
            pass
        else:
            raise BaseException("The coding parameter has to be a string or a Coding Object (called method as library)!")
        # TODO check translate params
        return translate(url=url,  source=source, coding=one_coding, 
                         target=target, targetsystem=targetsystem, 
                         reverse=reverse, silent=True)'''
        self.py_code += '''
    elif code:
        if not isinstance(code,str): 
            raise BaseException("The code parameter has to be a string!")
    elif target:
        if not isinstance(code,str): 
            raise BaseException("The target parameter has to be a string!")
    elif targetsystem:
        if not isinstance(code,str): 
            raise BaseException("The targetsystem parameter has to be a string!")
    else:
        raise BaseException("At least codeableConcept, coding, code, target or targetSystem has to be given!")
    # end validation and recall of translate in simplier from

    # look for any information from the one ore more generated conceptMaps into conceptMap_as_7dimension_dict
    match = []
    unmapped = []
    if url and url not in conceptMap_as_7dimension_dict.keys():
        print('   #ERROR# ConceptMap with URL "'+ url +'" is not loaded to this compiled conceptMap #ERROR#')
    else:
        for url_lvl in conceptMap_as_7dimension_dict:
            if url_lvl == "%" or not url or url_lvl == str(url or ""):#+str(("/?version=" and conceptMapVersion) or ""):
                for source_lvl in conceptMap_as_7dimension_dict[url_lvl]:
                    if source_lvl == "%" or not source or source_lvl == source:
                        for target_lvl in conceptMap_as_7dimension_dict[url_lvl][source_lvl]:
                            if target_lvl == "%" or not target or target_lvl == target:
                                for system_lvl in conceptMap_as_7dimension_dict[url_lvl][source_lvl][target_lvl]:
                                    if system_lvl == "%" or not system or system_lvl == system:#+str(("/?version=" and version) or ""):
                                        for targetsystem_lvl in conceptMap_as_7dimension_dict[url_lvl][source_lvl][target_lvl][system_lvl]:
                                            if targetsystem_lvl == "%" or not targetsystem or targetsystem_lvl == targetsystem:
                                                for code_lvl in conceptMap_as_7dimension_dict[url_lvl][source_lvl][target_lvl][system_lvl][targetsystem_lvl]:
                                                    if code_lvl == "|" or code_lvl == "~" or code_lvl == "#":
                                                        unmapped += conceptMap_as_7dimension_dict[url_lvl][source_lvl][target_lvl][system_lvl][targetsystem_lvl][code_lvl]
                                                    if code_lvl == "%" or not code or code_lvl == code:
                                                        match += conceptMap_as_7dimension_dict[url_lvl][source_lvl][target_lvl][system_lvl][targetsystem_lvl][code_lvl]                
                                                    
    if not match:
        for one_unmapped in unmapped:
            tmp_system = ""
            tmp_version = ""
            tmp_code = ""
            tmp_display = ""
            # replace all "|" values with to translated code (provided from https://hl7.org/fhir/R4B/conceptmap-definitions.html#ConceptMap.group.unmapped.mode)
            if one_unmapped["concept"]["code"].startswith("|"):
                tmp_system = system
                tmp_version = version
                tmp_code = one_unmapped["concept"]["code"][1:] + code
            # replace all "~" values with fixed code (provided from https://hl7.org/fhir/R4B/conceptmap-definitions.html#ConceptMap.group.unmapped.mode)
            elif one_unmapped["concept"]["code"].startswith("~"):
                if tmp := one_unmapped["concept"]["system"]: tmp_system = tmp 
                tmp_code = one_unmapped["concept"]["code"][1:]
                tmp_display = one_unmapped["concept"]["display"]
            elif one_unmapped["concept"]["code"].startswith("#"):
                # TODO detect recursion like conceptMapA -> conceptMapB -> ConceptMapA -> ...
                return translate(one_unmapped["concept"]["code"][1:], None, code, system, version, source, 
                                 coding, codeableConcept, target, targetsystem, reverse, silent)'''
        self.py_code += '''
            # prepare the match.concept results
            concept = {}
            if tmp_system: concept["system"] = tmp_system
            if tmp_version: concept["version"] = tmp_version
            if tmp_code: concept["code"] = tmp_code
            if tmp_display: concept["display"] = tmp_display

            # if the concept dict is empty, than skip this broken value and give a warning, that there is a empty group
            if concept == {}:
                # TODO do a warning, that it seems like the conceptmap is broken, because there is a empty group
                continue
            
            match.append({"%s": one_unmapped["%s"], 
                          "concept": concept,
                          "source": one_unmapped["source"]})

    # see if any match is not in R4 "unmatched" or "disjoint" and in R5 "not-related-to"
    result = False
    message = ""
    for one_match in match:
        if one_match["%s"] not in %s:
            result = True 
            # for printing only, if no url was initially given use the conceptmap
            if not url:
                url = one_match["source"]
''' % tuple([self.get_key_4_r5relationsship_r4equivalence()] * 3 + [self.values_4_translate_match_result_false()])
        self.py_code += '''
    if not silent:
        print('Translation in '+str(round(time.time()-start,3))+' seconds for code "'+(code or "NONE")+'" with ConceptMap "'+url+'"')
    return {"result": result, "message": message, "match": match}

conceptMap_as_7dimension_dict = {}
'''

    def _footer_standalone(self): 
        self.py_code += '''
        
if __name__ == "__main__":
    parser = init_argparse()
    args = parser.parse_args()
    ret = translate(args.code, args.system, args.version, args.source, args.coding, 
    args.codeableConcept, args.target, args.targetsystem, args.reverse, args.silent)'''

parse, parseEtree, parseString, parseLiteral = parse_factory(supermod)
