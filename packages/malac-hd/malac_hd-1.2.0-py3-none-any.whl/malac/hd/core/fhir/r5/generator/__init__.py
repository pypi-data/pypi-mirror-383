from malac.models.fhir import r5 as supermod

from .structuremap import PythonGenerator as StructureMapPythonGenerator
from .conceptmap import PythonGenerator as ConceptMapPythonGenerator
from .structuredefinition import PythonGenerator as StructureDefinitionPythonGenerator

supermod.StructureMap.subclass = StructureMapPythonGenerator
supermod.ConceptMap.subclass = ConceptMapPythonGenerator
supermod.StructureDefinition.subclass = StructureDefinitionPythonGenerator
