
import json

from malac.hd import ConvertMaster, list_i_o_modules
from malac.models.fhir import utils as utils, r4 as supermod
from malac.transformer.fhir.r4 import structuremap as transformer
from malac.hd.core.fhir.base.generator.resource import parse_factory

from ...r5.generator.structuremap import PythonGenerator as PythonGeneratorR5

class PythonGenerator(supermod.StructureMap, ConvertMaster):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.skipped_groups = None
        self.transform_default_needed = None
        self.translate_dict_py_code = None
        self.get_group = None
        self.default_types_maps = None
        self.default_types_maps_plus = None
        self.default_types_maps_subtypes = None

    def convert(self, *args, **kwargs):
        tgt = PythonGeneratorR5()
        transformer.StructureMap(self, tgt)
        kwargs["parse_wrapper"] = parse
        tgt.i_module = getattr(self, "i_module", None)
        tgt.o_module = getattr(self, "o_module", None)
        result = tgt.convert(*args, **kwargs)
        self.skipped_groups = tgt.skipped_groups
        self.transform_default_needed = tgt.transform_default_needed
        self.translate_dict_py_code = tgt.translate_dict_py_code
        self.get_group = tgt.get_group
        self.default_types_maps = tgt.default_types_maps
        self.default_types_maps_plus = tgt.default_types_maps_plus
        self.default_types_maps_subtypes = tgt.default_types_maps_subtypes
        return result


parse, parseEtree, parseString, parseLiteral = parse_factory(supermod)
