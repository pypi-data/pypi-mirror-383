from malac.hd import ConvertMaster
from malac.models.fhir import r5 as supermod
from malac.hd.core.fhir.base.generator.resource import parse_factory

class PythonGenerator(supermod.StructureDefinition, ConvertMaster):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def convert(self, input, o_module):
        pass

parse, parseEtree, parseString, parseLiteral = parse_factory(supermod)
