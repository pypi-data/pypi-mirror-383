
from malac.hd import ConvertMaster, list_i_o_modules
from malac.models.fhir import r4, utils as utils
from malac.transformer.fhir.r4 import conceptmap as transformer
from malac.hd.core.fhir.base.generator.resource import parse_factory

from ...r5.generator.conceptmap import PythonGenerator as PythonGeneratorR5

supermod = r4

#class PythonGenerator(supermod.ConceptMap, ConvertMaster):
#
#    def convert(self, *args, **kwargs):
#        tgt = PythonGeneratorR5()
#        transformer.ConceptMap(self, tgt) # TODO:sbe keep equivalence codes if model is R4
#        kwargs.update({"model": supermod})
#        return tgt.convert(*args, **kwargs)

class PythonGenerator(supermod.ConceptMap, PythonGeneratorR5):

    def get_key_4_r5relationsship_r4equivalence(self):
        return "equivalence"
    
    def key_4_sourceVS(self):
        return "source"
    
    def key_4_targetVS(self):
        return "target"
    
    def values_4_translate_match_result_false(self):
        return "['unmatched' , 'disjoint']" 

    def convert(self, *args, **kwargs):
        kwargs.update({"model": supermod})
        return super().convert(*args, **kwargs)

parse, parseEtree, parseString, parseLiteral = parse_factory(supermod)