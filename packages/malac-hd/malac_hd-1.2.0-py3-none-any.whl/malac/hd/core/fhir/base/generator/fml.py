import os
import tempfile
import re
import threading

from antlr4 import *
from antlr4.tree.Tree import ParseTreeWalker
from antlr4.error.ErrorListener import ErrorListener

import lxml.etree as ET

thread_local = threading.local()
thread_local.import_cache = dict()
thread_local.temp_path = None

# This class defines a complete listener for a parse tree produced by mappingParser.
class StructureMapGeneratorBase(object):

    mappingParser = None # override in base

    def __init__(self):
        self.xml_root = ET.Element("StructureMap")
        self.structure = None
        self.group = None
        self.typeMode = None
        self.source = None
        self.ruleitem = None
        self.transform = None
        self.transforms = None
        self.contained = None
        self.concept_map = None
        self.concept_group = None
        self.concept_source = None
        self.concept_source_count = 0
        self.code = None
        self.concept_op = None
        self.element = None
        self.dependent = None
        self.condition = False
        self.currvar = 0
        self.group_stack = []
        self.url = None
        self.imports = []

    def _next_var(self):
        self.currvar += 1
        return "v" + str(self.currvar)

    def _escapeFhirPath(self, child):
        lines = child.start.source[1].strdata[child.start.start:child.stop.stop + 1].split("\n")
        fhirpath = []
        for line in lines:
            fhirpath.append(line.split(" //")[0]) # TODO:sbe better solution for comments
        return " ".join("\n".join(fhirpath).split())

    def xml(self):
        return ET.tostring(self.xml_root, pretty_print=True)

    # Exit a parse tree produced by mappingParser#mapId.
    def exitMapId(self, ctx):
        url = ET.SubElement(self.xml_root, "url")
        url_str = ctx.children[1].getText().strip('"`')
        url.attrib["value"] = url_str
        name = ET.SubElement(self.xml_root, "name")
        name.attrib["value"] = ctx.children[3].getText().strip('"`')
        self.url = url_str

    # Enter a parse tree produced by mappingParser#structure.
    def enterStructure(self, ctx):
        self.structure = ET.SubElement(self.xml_root, "structure")
        url = ET.SubElement(self.structure, "url")
        url.attrib["value"] = ctx.children[1].getText().strip('"`')

    # Exit a parse tree produced by mappingParser#structureAlias.
    def exitStructureAlias(self, ctx):
        alias = ET.SubElement(self.structure, "alias")
        alias.attrib["value"] = ctx.children[1].getText().strip('`')

    # Enter a parse tree produced by mappingParser#imports.
    def enterImports(self, ctx):
        import_ = ET.SubElement(self.xml_root, "import")
        url = ctx.children[1].getText().strip('"`')
        import_.attrib["value"] = url
        self.imports.append(url)

    # Enter a parse tree produced by mappingParser#group.
    def enterGroup(self, ctx):
        self.group = ET.SubElement(self.xml_root, "group")
        name = ET.SubElement(self.group, "name")
        name.attrib["value"] = ctx.children[1].getText()
        self.typeMode = ET.SubElement(self.group, "typeMode")
        self.typeMode.attrib["value"] = "none"

    # Enter a parse tree produced by mappingParser#rules.
    def enterRules(self, ctx):
        self.dependent = False

    # Enter a parse tree produced by mappingParser#typeMode.
    def enterTypeMode(self, ctx):
        self.typeMode.attrib["value"] = ctx.children[1].getText()

    # Enter a parse tree produced by mappingParser#extends.
    def enterExtends(self, ctx):
        extends = ET.SubElement(self.group, "extends")
        extends.attrib["value"] = ctx.children[1].getText()

    # Enter a parse tree produced by mappingParser#parameter.
    def enterParameter(self, ctx):
        input = ET.SubElement(self.group, "input")
        name = ET.SubElement(input, "name")
        name.attrib["value"] = ctx.children[1].getText()
        if len(ctx.children) > 2:
            type_ = ET.SubElement(input, "type")
            type_.attrib["value"] = ctx.children[2].children[1].getText()
        mode = ET.SubElement(input, "mode")
        mode.attrib["value"] = ctx.children[0].getText()

    # Exit a parse tree produced by mappingParser#parameter.
    def exitParameter(self, ctx):
        pass

    # Enter a parse tree produced by mappingParser#rule.
    def enterRule(self, ctx):
        self.rule = ET.SubElement(self.group, "rule")

    # Enter a parse tree produced by mappingParser#ruleName.
    def enterRuleName(self, ctx):
        pass # TODO implement

    # Exit a parse tree produced by mappingParser#ruleName.
    def exitRuleName(self, ctx):
        pass

    # Enter a parse tree produced by mappingParser#ruleSource.
    def enterRuleSource(self, ctx):
        self.source = self.ruleitem = ET.SubElement(self.rule, "source")

    # Exit a parse tree produced by mappingParser#ruleTargets.
    def exitRuleTargets(self, ctx):
        if self.transforms is None and not isinstance(ctx.parentCtx.children[3], self.mappingParser.DependentContext):
            var = "vvv" # self._next_var()
            variable = ET.SubElement(self.ruleitem, "variable")
            variable.attrib["value"] = var
            variable = ET.SubElement(self.source, "variable")
            variable.attrib["value"] = var
            transform = ET.SubElement(self.ruleitem, "transform")
            transform.attrib["value"] = "create"
        self.transforms = None

    # Enter a parse tree produced by mappingParser#sourceType.
    def enterSourceType(self, ctx):
        type_ = ET.SubElement(self.source, "type")
        type_.attrib["value"] = ctx.children[1].getText()

    # Exit a parse tree produced by mappingParser#sourceType.
    def exitSourceType(self, ctx):
        pass

    # Enter a parse tree produced by mappingParser#sourceCardinality.
    def enterSourceCardinality(self, ctx):
        raise NotImplementedError("source cardinality not implemented")

    # Exit a parse tree produced by mappingParser#sourceCardinality.
    def exitSourceCardinality(self, ctx):
        pass

    # Enter a parse tree produced by mappingParser#upperBound.
    def enterUpperBound(self, ctx):
        raise NotImplementedError("upper bound not implemented")

    # Exit a parse tree produced by mappingParser#upperBound.
    def exitUpperBound(self, ctx):
        pass

    # Exit a parse tree produced by mappingParser#ruleContext.
    def exitRuleContext(self, ctx):
        if self.transform is None:
            context = ET.SubElement(self.ruleitem, "context")
            context.attrib["value"] = ctx.children[0].getText().strip('`')
            if len(ctx.children) > 2:
                element = ET.SubElement(self.ruleitem, "element")
                element.attrib["value"] = ctx.children[2].getText().strip('`')
        else:
            self.transform.attrib["value"] = "copy"
            parameter = ET.SubElement(self.ruleitem, "parameter")
            valueId = ET.SubElement(parameter, "valueId")
            valueId.attrib["value"] = ctx.children[0].getText()

    # Enter a parse tree produced by mappingParser#sourceDefault.
    def enterSourceDefault(self, ctx):
        raise NotImplementedError("source default not implemented")

    # Exit a parse tree produced by mappingParser#sourceDefault.
    def exitSourceDefault(self, ctx):
        pass

    # Enter a parse tree produced by mappingParser#alias.
    def enterAlias(self, ctx):
        variable = ET.SubElement(self.ruleitem, "variable")
        variable.attrib["value"] = ctx.children[1].getText()

    # Enter a parse tree produced by mappingParser#whereClause.
    def enterWhereClause(self, ctx):
        self.create_condition(ctx)
        self.condition = True

    # Enter a parse tree produced by mappingParser#checkClause.
    def enterCheckClause(self, ctx):
        raise NotImplementedError("check clause not implemented")

    # Exit a parse tree produced by mappingParser#checkClause.
    def exitCheckClause(self, ctx):
        pass

    # Enter a parse tree produced by mappingParser#log.
    def enterLog(self, ctx):
        pass # raise NotImplementedError("log not implemented")

    # Exit a parse tree produced by mappingParser#log.
    def exitLog(self, ctx):
        pass

    # Enter a parse tree produced by mappingParser#dependent.
    def enterDependent(self, ctx):
        self.dependent = True
        self.group_stack.append(self.group)
        #if self.condition:
        self.group = self.rule

    # Exit a parse tree produced by mappingParser#dependent.
    def exitDependent(self, ctx):
        self.dependent = False
        self.group = self.group_stack.pop()


    # Enter a parse tree produced by mappingParser#ruleTarget.
    def enterRuleTarget(self, ctx):
        self.ruleitem = ET.SubElement(self.rule, "target")

    def exitRuleTarget(self, ctx):
        pass

    # Enter a parse tree produced by mappingParser#transform.
    def enterTransform(self, ctx):
        self.transform = ET.SubElement(self.ruleitem, "transform")
        self.transforms = True
        if ctx.children is not None and isinstance(ctx.children[0], self.mappingParser.MapliteralContext):
            self.transform.attrib["value"] = "copy"
            parameter = ET.SubElement(self.ruleitem, "parameter")
            text = ctx.children[0].getText()
            if text.startswith("'"):
                valueString = ET.SubElement(parameter, "valueString")
                valueString.attrib["value"] = text.strip("'")
            elif text in ["true", "false"]:
                valueBoolean = ET.SubElement(parameter, "valueBoolean")
                valueBoolean.attrib["value"] = text
            elif text.startswith("@"):
                if text[1] == "T":
                    valueTime = ET.SubElement(parameter, "valueTime")
                    valueTime.attrib["value"] = text[1:]
                elif "T" in text[1]:
                    valueDateTime = ET.SubElement(parameter, "valueDateTime")
                    valueDateTime.attrib["value"] = text[1:]
                else:
                    valueDate = ET.SubElement(parameter, "valueDate")
                    valueDate.attrib["value"] = text[1:]
            elif "." in text:
                valueInteger = ET.SubElement(parameter, "valueDecimal")
                valueInteger.attrib["value"] = text
            else:
                valueInteger = ET.SubElement(parameter, "valueInteger")
                valueInteger.attrib["value"] = text

    # Exit a parse tree produced by mappingParser#transform.
    def exitTransform(self, ctx):
        self.transform = None

    # Enter a parse tree produced by mappingParser#evaluate.
    def enterEvaluate(self, ctx):
        self.transform.attrib["value"] = "evaluate"
        parameter = ET.SubElement(self.ruleitem, "parameter")
        valueString = ET.SubElement(parameter, "valueString")
        valueString.attrib["value"] = self._escapeFhirPath(ctx.children[1])

    # Enter a parse tree produced by mappingParser#mapinvocation.
    def enterMapinvocation(self, ctx):
        if self.transform is not None:
            self.transform.attrib["value"] = ctx.children[0].getText()
        elif self.dependent:
            self.dependent_map = ET.SubElement(self.rule, "dependent")
            name = ET.SubElement(self.dependent_map, "name")
            name.attrib["value"] = ctx.children[0].getText()
        else:
            pass

    # Enter a parse tree produced by mappingParser#param.
    def enterParam(self, ctx):
        try:
            type_ = ctx.children[0].symbol.type
        except:
            type_ = ctx.children[0].children[0].symbol.type
        if self.transform is not None:
            param = ET.SubElement(self.ruleitem, "parameter")
            value = ctx.children[0].getText()
            if type_ == self.mappingParser.IDENTIFIER:
                val = ET.SubElement(param, "valueId")
                val.attrib["value"] = value
            elif type_ == self.mappingParser.STRING:
                val = ET.SubElement(param, "valueString")
                val.attrib["value"] = value.strip("'")
            elif type_ == self.mappingParser.INTEGER:
                val = ET.SubElement(param, "valueInteger")
                val.attrib["value"] = value
            elif type_ == self.mappingParser.NUMBER:
                val = ET.SubElement(param, "valueDecimal")
                val.attrib["value"] = value
            elif type_ == self.mappingParser.BOOL:
                val = ET.SubElement(param, "valueBoolean")
                val.attrib["value"] = value
            elif type_ == self.mappingParser.DATETIME:
                val = ET.SubElement(param, "valueDateTime")
                val.attrib["value"] = value[1:]
            elif type_ == self.mappingParser.DATE:
                val = ET.SubElement(param, "valueDate")
                val.attrib["value"] = value[1:]
            elif type_ == self.mappingParser.TIME:
                val = ET.SubElement(param, "valueTime")
                val.attrib["value"] = value[1:]
            else:
                raise NotImplementedError("Param type %s not implemented" % type_)
        elif self.dependent:
            param = self.create_dependent_param(ctx)
            if type_ == self.mappingParser.IDENTIFIER:
                url = ET.SubElement(param, "extension")
                url.attrib["url"] = "http://hl7.org/fhir/tools/StructureDefinition/original-item-type"
                val = ET.SubElement(url, "valueUrl")
                val.attrib["value"] = "id"
        else:
            pass

    # Enter a parse tree produced by mappingParser#sourceListMode.
    def enterSourceListMode(self, ctx):
        listMode = ET.SubElement(self.ruleitem, "listMode")
        listMode.attrib["value"] = ctx.children[0].getText()

    # Enter a parse tree produced by mappingParser#targetListMode.
    def enterTargetListMode(self, ctx):
        raise NotImplementedError("target listmode not implemented")

    # Exit a parse tree produced by mappingParser#targetListMode.
    def exitTargetListMode(self, ctx):
        pass

    # Exit a parse tree produced by mappingParser#modelMode.
    def exitModelMode(self, ctx):
        alias = ET.SubElement(self.structure, "mode")
        alias.attrib["value"] = ctx.getText()

    # Enter a parse tree produced by mappingParser#conceptMap.
    def enterConceptMap(self, ctx):
        self.contained = ET.SubElement(self.xml_root, "contained")
        self.concept_map = ET.SubElement(self.contained, "ConceptMap")
        self.id = ET.SubElement(self.concept_map, "id")
        self.id.attrib["value"] = ctx.children[1].getText().strip('"`')
        self.status = ET.SubElement(self.concept_map, "status")
        self.status.attrib["value"] = "draft"
        self.concept_group = ET.SubElement(self.concept_map, "group")
        self.concept_source_count = 0
        self.concept_source = None
        self.concept_op = None
        self.element = None

    # Enter a parse tree produced by mappingParser#prefix.
    def enterPrefix(self, ctx):
        if self.concept_source is None:
            elem = ET.SubElement(self.concept_group, "source")
            self.concept_source = elem
        else:
            elem = ET.SubElement(self.concept_group, "target")
        elem.attrib["value"] = ctx.children[3].getText().strip('"')

    def enterConceptMapping(self, ctx):
        self.element = ET.SubElement(self.concept_group, "element")
        self.code = ET.SubElement(self.element, "code")
        if self.concept_source_count % 2 == 0:
            op = ctx.children[3].getText()
            if op not in ["==", "-"]:
                raise NotImplementedError("concept mapping operation %s not supported" % op)
            self.concept_op = op

    # Enter a parse tree produced by mappingParser#field.
    def enterField(self, ctx):
        field = ctx.getText().strip('"')
        if self.concept_source_count % 2 == 0:
            self.code.attrib["value"] = field
        else:
            op = self.concept_op
            target = ET.SubElement(self.element, "target")
            code = ET.SubElement(target, "code")
            code.attrib["value"] = field
            equivalence = self.create_relationship(ctx, target)
            if op in ["==", "-"]:
                equivalence.attrib["value"] = "equivalent"
            else:
                raise NotImplementedError("concept mapping operation %s not implemented" % op)
        self.concept_source_count += 1

    def create_condition(self, ctx):
        raise NotImplementedError("Override in base")
    
    def create_dependent_param(self, ctx):
        raise NotImplementedError("Override in base")

    def create_relationship(self, ctx, target):
        raise NotImplementedError("Override in base")


def parse_factory(mappingLexer, mappingParser, structureMapGenerator, parseStringFhir):

    def _parse(inString):
        def recover(e):
            raise e

        generator = structureMapGenerator()
        errorListener = ErrorListener()

        textStream =  InputStream(inString)

        lexer = mappingLexer(textStream)
        lexer.recover = recover
        lexer.removeErrorListeners()
        lexer.addErrorListener(errorListener)

        parser = mappingParser(CommonTokenStream(lexer))
        parser.buildParseTrees = True
        parser.removeErrorListeners()
        parser.addErrorListener(errorListener)

        walker = ParseTreeWalker()
        walker.walk(generator, parser.structureMap())

        return generator

    def _generate(generator, silence, output, source_path):
        for url in generator.imports:
            if "*" in url:
                url = re.escape(url)
                url = url.replace("\*", ".*")
                wildcard_url = True
            else:
                wildcard_url = False

            # search all files in the same directory for the url
            dirname = os.path.dirname(os.path.abspath(source_path))
            basename = os.path.basename(source_path)
            ext_min = basename[basename.rfind("."):]
            found = False

            for filename in os.listdir(dirname):
                if filename.endswith(ext_min) and filename != basename:
                    path = dirname + "/" + filename
                    url_matches = False

                    try:
                        if path:
                            if path in thread_local.import_cache:
                                imported = thread_local.import_cache[path]
                            else:
                                fmlContent = open(path, "r", encoding='utf-8').read()
                                imported = _parse(fmlContent)
                                thread_local.import_cache[path] = imported
                            if wildcard_url:
                                if imported.url:
                                    match = re.match(url, imported.url)
                                    url_matches = bool(match)
                                else:
                                    url_matches = False
                            else:
                                url_matches = imported.url == url
                    except BaseException as ex:
                        continue

                    if url_matches:
                        out_path = thread_local.temp_path + "/" + filename.replace(ext_min, ".xml")
                        if not os.path.isfile(out_path):
                            _generate(imported, silence, "structuremap", path)
                            with open(out_path, 'wb') as f:
                                f.write(imported.xml())
                        found = True
                        break
            if not wildcard_url and not found:
                raise BaseException("Could not import %s, file not found." % url)

        if output == "structuremap":
            return generator
        else:
            out_mod = parseStringFhir(generator.xml(), silence=silence)
            out_mod.temp_filename = thread_local.temp_path + "/" + os.path.basename(source_path).replace(ext_min, ".xml")
            return out_mod

    def parseString(inString, silence=False, output="fhir", source_path="."):
        thread_local.temp_path = tempfile.mkdtemp()
        thread_local.import_cache.clear()
        generator = _parse(inString)
        return _generate(generator, silence, output, source_path)
    
    def parse(inFilename, silence=False, output="fhir"):
        fmlContent = open(inFilename, "r", encoding='utf-8').read()
        return parseString(fmlContent, silence=silence, output=output, source_path=inFilename)

    return parse, parseString
