from malac.hd import ConvertMaster
from malac.hd.core.fhir.base.generator.fml import StructureMapGeneratorBase, parse_factory
from malac.hd.core.fhir.r5.generator.structuremap import parseString as structureMapParseString
from malac.hd.core.fhir.r5.parser.mappingLexer import mappingLexer
from malac.hd.core.fhir.r5.parser.mappingListener import mappingListener
from malac.hd.core.fhir.r5.parser.mappingParser import mappingParser

import lxml.etree as ET


class StructureMapGenerator(StructureMapGeneratorBase, mappingListener):

    mappingParser = mappingParser

    # Enter a parse tree produced by mappingParser#const.
    def enterConst(self, ctx):
        const = ET.SubElement(self.xml_root, "const")
        name = ET.SubElement(const, "name")
        name.attrib["value"] = ctx.children[1].getText()
        name = ET.SubElement(const, "value")
        name.attrib["value"] = ctx.children[3].getText()

    def create_condition(self, ctx):
        condition = ET.SubElement(self.ruleitem, "condition")
        condition.attrib["value"] = self._escapeFhirPath(ctx.children[2])

    def create_dependent_param(self, ctx):
        param = ET.SubElement(self.dependent_map, "parameter")
        val = ET.SubElement(param, "valueString")
        val.attrib["value"] = ctx.children[0].getText()
        return param

    def create_relationship(self, ctx, target):
        return ET.SubElement(target, "relationship")


parse, parseString = parse_factory(mappingLexer, mappingParser, StructureMapGenerator, structureMapParseString)
