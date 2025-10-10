import inspect

from malac.hd.core.fhir.base.generator.fhirpath import PythonGeneratorBase, FHIRPathContext, compile_factory, evaluate_json_factory
from malac.models.fhir import utils, r5 as supermod
from malac.utils import fhirpath as fhirpath_utils

class PythonGenerator(PythonGeneratorBase):
    supermod = supermod

def parseString(inString, silence=False):
    return PythonGenerator(inString)

compile = compile_factory(parseString, supermod)
evaluate_json = evaluate_json_factory(supermod)
