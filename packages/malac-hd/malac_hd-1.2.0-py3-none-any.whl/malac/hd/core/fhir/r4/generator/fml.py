from malac.hd.core.fhir.base.generator.fml import StructureMapGeneratorBase, parse_factory
from malac.hd.core.fhir.r4.generator.structuremap import parseString as structureMapParseString
from malac.hd.core.fhir.r4.parser.mappingLexer import mappingLexer
from malac.hd.core.fhir.r4.parser.mappingListener import mappingListener
from malac.hd.core.fhir.r4.parser.mappingParser import mappingParser

import lxml.etree as ET


class StructureMapGenerator(StructureMapGeneratorBase, mappingListener):

    mappingParser = mappingParser

    def create_condition(self, ctx):
        condition = ET.SubElement(self.ruleitem, "condition")
        condition.attrib["value"] = self._escapeFhirPath(ctx.children[1])

    def create_dependent_param(self, ctx):
        param = ET.SubElement(self.dependent_map, "variable")
        param.attrib["value"] = ctx.children[0].getText()
        return param

    def create_relationship(self, ctx, target):
        return ET.SubElement(target, "equivalence")


parse, parseString = parse_factory(mappingLexer, mappingParser, StructureMapGenerator, structureMapParseString)
