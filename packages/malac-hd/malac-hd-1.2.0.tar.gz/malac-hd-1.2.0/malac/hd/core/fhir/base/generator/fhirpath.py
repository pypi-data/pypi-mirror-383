import datetime
import decimal
from collections import OrderedDict
import inspect
import re
import ast

from antlr4 import *
from antlr4.tree.Tree import ParseTreeWalker, TerminalNodeImpl
from antlr4.error.ErrorListener import ErrorListener

import malac
from malac.models.fhir import utils
from malac.utils import fhirpath as fhirpath_utils, date as dateutil

from malac.hd import ConvertMaster
from malac.hd.core.fhir.base.parser.fhirpathListener import fhirpathListener
from malac.hd.core.fhir.base.parser.fhirpathParser import fhirpathParser
from malac.hd.core.fhir.base.parser.fhirpathLexer import fhirpathLexer


class PythonGeneratorBase(fhirpathListener, ConvertMaster):

    supermod = None

    def __init__(self, input_string):
        self.input_string = input_string
        self.var_types = {}
        self.list_var = set()
        self.this = {}
        self.this_elem = None
        self.o_module = None
        self.resolve_ctx = None
        self.where_vars = None
        self.counter = 0
        self.parentStack = None

    def convert(self, silent=True, context=None, standalone=True):
        self.resolve_ctx = set()
        self.where_vars = []
        self.counter = 0
        self.parentStack = [{"py_code": {}}]
        if context:
            self.var_types = context.var_types
            self.list_var = context.list_var
            self.this = context.this
            self.this_elem = context.this_elem
            self.o_module = context.o_module
            if context.this:
                self.resolve_ctx.add(context.this)
        else:
            self.var_types = {}
            self.list_var = set()
            self.this = {}
            self.this_elem = None
            self.o_module = None or supermod
        self.utils = fhirpath_utils.FHIRPathUtils(self.o_module)

        def recover(e):
                raise e
        errorListener = ErrorListener()

        textStream = InputStream(self.input_string)
        lexer = fhirpathLexer(textStream)
        lexer.recover = recover
        lexer.removeErrorListeners()
        lexer.addErrorListener(errorListener)

        parser = fhirpathParser(CommonTokenStream(lexer))
        parser.buildParseTrees = True
        parser.removeErrorListeners()
        parser.addErrorListener(errorListener)

        walker = ParseTreeWalker()
        walker.walk(self, parser.expression())

        py_code = next(iter(self.parentStack[0]["py_code"].values()))
        py_code.code = py_code.code.replace("🔥", ("[%s]" if py_code.list_func else "%s") % self.this)
        return py_code

    # Enter a parse tree produced by fhirpathParser#indexerExpression.
    def enterIndexerExpression(self, ctx: fhirpathParser.IndexerExpressionContext):
        self._enter(ctx)

    # Exit a parse tree produced by fhirpathParser#indexerExpression.
    def exitIndexerExpression(self, ctx: fhirpathParser.IndexerExpressionContext):
        node, parentNode, code = self._exit(ctx)
        new_code = None
        if re.search("^\\[[0-9]+\\]$", code[1].code) and code[0].code.startswith("fhirpath_utils.get(") and len(code[0].code.split(",")) == 2:
            parts = code[0].code[19:-1].split(",")
            var_type = self.var_types.get(parts[0], None)
            elem_type, is_list = utils.get_type(var_type, parts[1][1:-1]) if var_type else (None, None)
            if elem_type and is_list and code[1].code == "[0]":
                params_code = f"{parts[0]}.{parts[1][1:-1]}"
                new_code = f"({params_code} or [])[:1]"
        if not new_code:
            new_code = f"fhirpath_utils.at_index({code[0].code}, {code[1].code})"
        parentNode["py_code"][ctx] = PythonCode(new_code, code[0].out_type)

    # Enter a parse tree produced by fhirpathParser#polarityExpression.
    def enterPolarityExpression(self, ctx: fhirpathParser.PolarityExpressionContext):
        self._enter(ctx)

    # Exit a parse tree produced by fhirpathParser#polarityExpression.
    def exitPolarityExpression(self, ctx: fhirpathParser.PolarityExpressionContext):
        node, parentNode, code = self._exit(ctx)
        if ctx.children[0].getText() == "-":
            new_code = None
            if re.search("^\\[[0-9]+\\]$", code[0].code):
                new_code = f"[-{code[0].code[1:-1]}]"
            if not new_code:
                new_code = "fhirpath_utils.negate(%s)" % code[0].code
            parentNode["py_code"][ctx] = PythonCode(new_code, int)
        else:
            parentNode["py_code"][ctx] = code[0]

    # Enter a parse tree produced by fhirpathParser#additiveExpression.
    def enterAdditiveExpression(self, ctx: fhirpathParser.AdditiveExpressionContext):
        self._enter(ctx)

    # Exit a parse tree produced by fhirpathParser#additiveExpression.
    def exitAdditiveExpression(self, ctx: fhirpathParser.AdditiveExpressionContext):
        node, parentNode, code = self._exit(ctx)
        operator = ctx.children[1].getText()
        if operator == "+":
            new_code = f"fhirpath_utils.add({code[0].code}, {code[1].code})"
            if code[0].code.startswith("fhirpath_utils.add("):
                new_code = f"{code[0].code[:-1]}, {code[1].code})"
            parentNode["py_code"][ctx] = PythonCode(new_code, code[0].out_type)
        elif operator == "-":
            parentNode["py_code"][ctx] = PythonCode(f"fhirpath_utils.subtract({code[0].code}, {code[1].code})", code[0].out_type)
        elif operator == "&":
            parentNode["py_code"][ctx] = PythonCode(f"fhirpath_utils.concat({code[0].code}, {code[1].code})", code[0].out_type)

    # Enter a parse tree produced by fhirpathParser#multiplicativeExpression.
    def enterMultiplicativeExpression(self, ctx: fhirpathParser.MultiplicativeExpressionContext):
        self._enter(ctx)

    # Exit a parse tree produced by fhirpathParser#multiplicativeExpression.
    def exitMultiplicativeExpression(self, ctx: fhirpathParser.MultiplicativeExpressionContext):
        node, parentNode, code = self._exit(ctx)
        operator = ctx.children[1].getText()
        if operator == "*":
            parentNode["py_code"][ctx] = PythonCode(f"fhirpath_utils.multiply({code[0].code}, {code[1].code})", code[0].out_type)
        elif operator == "/":
            parentNode["py_code"][ctx] = PythonCode(f"fhirpath_utils.divide({code[0].code}, {code[1].code})", code[0].out_type)
        elif operator == "div":
            parentNode["py_code"][ctx] = PythonCode(f"fhirpath_utils.div({code[0].code}, {code[1].code})", int)
        elif operator == "mod":
            parentNode["py_code"][ctx] = PythonCode(f"fhirpath_utils.mod({code[0].code}, {code[1].code})", int)

    # Enter a parse tree produced by fhirpathParser#unionExpression.
    def enterUnionExpression(self, ctx: fhirpathParser.UnionExpressionContext):
        self._enter(ctx)

    # Exit a parse tree produced by fhirpathParser#unionExpression.
    def exitUnionExpression(self, ctx: fhirpathParser.UnionExpressionContext):
        node, parentNode, code = self._exit(ctx)
        parentNode["py_code"][ctx] = PythonCode("fhirpath_utils.union(%s, %s)" % (code[0].code, code[1].code), code[0].out_type)

    # Enter a parse tree produced by fhirpathParser#orExpression.
    def enterOrExpression(self, ctx: fhirpathParser.OrExpressionContext):
        self._enter(ctx)

    # Exit a parse tree produced by fhirpathParser#orExpression.
    def exitOrExpression(self, ctx: fhirpathParser.OrExpressionContext):
        node, parentNode, code = self._exit(ctx)
        op = ctx.children[1].getText()
        b0, c0 = self._is_bool(code[0].code, ast.Or if op == "or" else None)
        b1, c1 = self._is_bool(code[1].code, ast.Or if op == "or" else None)
        if b0 and b1:
            pycode = "[(%s %s %s)]" % (c0, "or" if op == "or" else "!=", c1)
        elif code[0].code.startswith("fhirpath_utils.bool_%s(" % op):
            pycode = "%s, %s)" % (code[0].code[:-1], code[1].code)
        else:
            pycode = "fhirpath_utils.bool_%s(%s, %s)" % (op, code[0].code, code[1].code)
        parentNode["py_code"][ctx] = PythonCode(pycode, bool)

    # Enter a parse tree produced by fhirpathParser#andExpression.
    def enterAndExpression(self, ctx: fhirpathParser.AndExpressionContext):
        self._enter(ctx)

    # Exit a parse tree produced by fhirpathParser#andExpression.
    def exitAndExpression(self, ctx: fhirpathParser.AndExpressionContext):
        node, parentNode, code = self._exit(ctx)
        b0, c0 = self._is_bool(code[0].code, ast.And)
        b1, c1 = self._is_bool(code[1].code, ast.And)
        if b0 and b1:
            pycode = "[(%s and %s)]" % (c0, c1)
        elif code[0].code.startswith("fhirpath_utils.bool_and("):
            pycode = "%s, %s)" % (code[0].code[:-1], code[1].code)
        else:
            pycode = "fhirpath_utils.bool_and(%s, %s)" % (code[0].code, code[1].code)
        parentNode["py_code"][ctx] = PythonCode(pycode, bool)

    def _is_bool(self, code, op):
        is_bool = False
        comp = ast.parse(code, mode="eval")
        if code.startswith("[bool(") or code.startswith("[not(") or re.search("^\\[\\(*bool\\(", code) or code.endswith(" is None)]") or code.endswith(" is not None)]"):
            is_bool = True
        elif code.startswith("[("):
            if len(comp.body.elts) == 1 and isinstance(comp.body.elts[0], ast.BoolOp):
                if isinstance(comp.body.elts[0].op, op):
                    return True, code[2:-2]
                is_bool = True
            elif len(comp.body.elts) == 1 and isinstance(comp.body.elts[0], ast.Call) and isinstance(comp.body.elts[0].func.value, ast.BoolOp):
                is_bool = True
        elif isinstance(comp.body, ast.List) and len(comp.body.elts) == 1:
            is_bool = True
        if not is_bool:
            reduced = code
        elif code.endswith(" is None)]") or code.endswith(" is not None)]"):
            reduced = code[2:-2]
        elif code.startswith("[bool("):
            reduced = code[6:-2]
        elif code.startswith("[not("):
            reduced = "not " + code[5:-2]
        elif code.startswith("[("):
            reduced = code[1:-1]
        else:
            reduced = code[1:-1]
        return is_bool, reduced

    # Enter a parse tree produced by fhirpathParser#membershipExpression.
    def enterMembershipExpression(self, ctx: fhirpathParser.MembershipExpressionContext):
        self._enter(ctx)

    # Exit a parse tree produced by fhirpathParser#membershipExpression.
    def exitMembershipExpression(self, ctx: fhirpathParser.MembershipExpressionContext):
        node, parentNode, code = self._exit(ctx)
        op = ctx.children[1].getText()
        if op == "in":
            parentNode["py_code"][ctx] = PythonCode("fhirpath_utils.membership(%s, %s)" % (code[0].code, code[1].code), None)
        elif op == "contains":
            parentNode["py_code"][ctx] = PythonCode("fhirpath_utils.containership(%s, %s)" % (code[0].code, code[1].code), None)
        else:
            raise BaseException("Invalid membership operation %s" % op)

    # Enter a parse tree produced by fhirpathParser#inequalityExpression.
    def enterInequalityExpression(self, ctx: fhirpathParser.InequalityExpressionContext):
        self._enter(ctx)

    # Exit a parse tree produced by fhirpathParser#inequalityExpression.
    def exitInequalityExpression(self, ctx: fhirpathParser.InequalityExpressionContext):
        node, parentNode, code = self._exit(ctx)
        new_code = None
        new_op = ctx.children[1].getText()
        if re.search("^\\[[0-9]+\\]$", code[1].code):
            if re.search("^\\[[A-Za-z_][A-Za-z0-9_]*\\]$", code[0].code):
                params_code = code[0].code[1:-1]
                strcomp = code[1].code[1:-1]
                var_type = self.var_types.get(params_code, None)
                if issubclass(var_type, int):
                    if self._is_value_type(var_type):
                        getstr = ".value"
                    else:
                        getstr = ""
                    if getstr == ".value":
                        proj = f"getattr({params_code}, 'value', None)"
                    else:
                        proj = f"{params_code}"
                    new_code = f"[{proj} {new_op} {strcomp}]"
            elif code[0].code.startswith("fhirpath_utils.get(") and len(code[0].code.split(",")) == 2:
                parts = code[0].code[19:-1].split(",")
                var_type = self.var_types.get(parts[0], None)
                elem_type, is_list = utils.get_type(var_type, parts[1][1:-1]) if var_type else (None, None)
                if issubclass(elem_type, int):
                    if self._is_value_type(elem_type):
                        getstr = ".value"
                    else:
                        getstr = ""
                    params_code = f"{parts[0]}.{parts[1][1:-1]}"
                    strcomp = code[1].code[1:-1]
                    if is_list:
                        v1 = self._get_new_varname()
                        new_code = f"[{v1}{getstr} {new_op} {strcomp} for {v1} in {params_code} or []]"
                    else:
                        if getstr == ".value":
                            proj = f"getattr({params_code}, 'value', None)"
                        else:
                            proj = f"{params_code}"
                        new_code = f"[{proj} {new_op} {strcomp}]"
            elif code[0].code.startswith("[len("):
                new_code = f"[{code[0].code[1:-1]} {new_op} {code[1].code[1:-1]}]"
        if not new_code:
            new_code = "fhirpath_utils.compare(%s, '%s', %s)" % (code[0].code, new_op, code[1].code)
        parentNode["py_code"][ctx] = PythonCode(new_code, bool)

    # Enter a parse tree produced by fhirpathParser#invocationExpression.
    def enterInvocationExpression(self, ctx: fhirpathParser.InvocationExpressionContext):
        self._enter(ctx)

    # Exit a parse tree produced by fhirpathParser#invocationExpression.
    def exitInvocationExpression(self, ctx: fhirpathParser.InvocationExpressionContext):
        node, parentNode, code = self._exit(ctx)

        if isinstance(ctx.children[-1], fhirpathParser.MemberInvocationContext):
            context = code[0]
            element = code[1]
            out_type, is_list = utils.get_type(context.out_type, element.code)
            choice_group_names = []
            if context.out_type:
                for base_var_type in inspect.getmro(context.out_type):
                    choice_group_names += getattr(base_var_type, "choice_group_names", [])
            if out_type is None and element.code in choice_group_names:
                out_type = context.out_type
                code = context.code
            else:
                add_args = ""
                if not out_type and element.code in ["dataString", "other", "dataBase64Binary", "xmlText"]:
                    element.code = "valueOf_"
                    add_args = ",strip=True"
                    out_type = str
                elif out_type and context.out_type.__name__ == "ResourceContainer":
                    raise BaseException("Cannot access contained without specifiying type (use 'as' or ofType)")
                if re.search("^\\[[A-Za-z_][A-Za-z0-9_]*\\]$", context.code):
                    code = f"fhirpath_utils.get({context.code[1:-1]},'{element.code}'{add_args})"
                elif context.code.startswith("fhirpath_utils.get(") and context.code.endswith("')"):
                    code = f"{context.code[:-1]},'{element.code}'{add_args})"
                elif context.code.endswith(" or [])[:1]"):
                    code = f"fhirpath_utils.get(next(iter({context.code[1:-5]}), None),'{element.code}')"
                elif re.search("fhirpath_utils\\.get\\(v[0-9]+(,'[A-Za-z_][A-Za-z0-9_]*')+\\)\\]$", context.code):
                    code = f"{context.code[:-2]},'{element.code}'{add_args})]"
                else:
                    v = self._get_new_varname(context.out_type) 
                    v2 = self._get_new_varname(element.out_type) 
                    code = f"[{v2} for {v} in {context.code} for {v2} in fhirpath_utils.get({v},'{element.code}'{add_args})]"
            py_code = PythonCode(code, out_type)
        elif isinstance(ctx.children[-1], fhirpathParser.FunctionInvocationContext):
            params = code[0]
            func = code[1]
            new_code = None
            if func.out_type == "🔥":
                func.out_type = params.out_type
            if func.list_func:
                if func.code == "fhirpath_utils.bool_not(🔥)" and params.code.startswith("[bool("):
                    new_code = "[not" + params.code[5:]
                elif func.code == "fhirpath_utils.bool_not(🔥)" and params.code.endswith(" is None)]"):
                    new_code = params.code[:-10] + " is not None)]"
                elif func.code == "fhirpath_utils.bool_not(🔥)" and params.code.endswith(" is not None)]"):
                    new_code = params.code[:-14] + " is None)]"
                elif (func.code == "[bool(🔥)]" or func.code == "[not(🔥)]") and params.code.startswith("fhirpath_utils.get(") and len(params.code.split(",")) == 2:
                    parts = params.code[19:-1].split(",")
                    var_type = self.var_types.get(parts[0], None)
                    elem_type, is_list = utils.get_type(var_type, parts[1][1:-1]) if var_type else (None, None)
                    if elem_type:
                        params_code = f"{parts[0]}.{parts[1][1:-1]}"
                        if is_list:
                            new_code = func.code.replace("🔥", params_code)
                        elif func.code == "[bool(🔥)]":
                            new_code = f"[({params_code} is not None)]"
                        else:
                            new_code = f"[({params_code} is None)]"
                elif re.search("^\\[v[0-9]+ for v[0-9]+ in 🔥 if fhirpath_utils.is_type\\(v[0-9]+, '.*'\\) == \\[True\\]\\]$", func.code) and re.search("^\\[[A-Za-z_][A-Za-z0-9_]*\\]$", params.code):
                    type_str = func.code[func.code[func.code.index("if "):].index("'") + func.code.index("if "):-12]
                    new_code = f"[fhirpath_utils.as_type({params.code[1:-1]}, {type_str})]"
                if new_code is None:
                    new_code = func.code.replace("🔥", params.code)
            else:
                if func.code.startswith("fhirpath_utils.startswith(🔥") and func.code.endswith("'])") and not func.code.endswith("''])") and params.code.startswith("fhirpath_utils.get(") and len(params.code.split(",")) == 2:
                    parts = params.code[19:-1].split(",")
                    var_type = self.var_types.get(parts[0], None)
                    elem_type, is_list = utils.get_type(var_type, parts[1][1:-1]) if var_type else (None, None)
                    if elem_type:
                        if self._is_value_type(elem_type):
                            getstr = ".value"
                        else:
                            getstr = ""
                        params_code = f"{parts[0]}.{parts[1][1:-1]}"
                        strcomp = func.code[30:-2]
                        if is_list:
                            v1 = self._get_new_varname()
                            new_code = f"[{v1}{getstr}.startswith({strcomp}) for {v1} in {params_code} or []]"
                        else:
                            if getstr == ".value":
                                proj = f"getattr({params_code}, 'value', '')"
                            else:
                                proj = f"({params_code} or '')"
                            new_code = f"[{proj}.startswith({strcomp})]"
                elif func.code.startswith("fhirpath_utils.startswith(🔥") and func.code.endswith("'])") and not func.code.endswith("''])") and re.search("^\\[[A-Za-z_][A-Za-z0-9_]*\\]$", params.code):
                    params_code = params.code[1:-1]
                    elem_type = self.var_types.get(params_code, None)
                    if elem_type:
                        if self._is_value_type(elem_type):
                            getstr = ".value"
                        else:
                            getstr = ""
                        if getstr == ".value":
                            proj = f"getattr({params_code}, 'value', '')"
                        else:
                            proj = f"({params_code} or '')"
                        new_code = f"[{proj}.startswith({func.code[30:-2]})]"
                elif func.code.startswith("fhirpath_utils.resolve(🔥, ["):
                    if params.code.startswith("['"):
                        new_code = func.code.replace("🔥", params.code[1:-1])
                elif params.code.startswith("["):
                    comp = ast.parse(params.code, mode="eval")
                    if isinstance(comp.body, ast.List) and len(comp.body.elts) == 1:
                        new_code = func.code.replace("🔥", params.code[1:-1])
                if new_code is None:
                    v1 = self._get_new_varname(params.out_type) 
                    v2 = self._get_new_varname(func.out_type) 
                    proj = func.code.replace("🔥", v1)
                    new_code = f"[{v2} for {v1} in {params.code} for {v2} in {proj}]"
            py_code = PythonCode(new_code, func.out_type)
        else:
            raise NotImplementedError("Not implemented: invocation other")
        parentNode["py_code"][ctx] = py_code

    # Enter a parse tree produced by fhirpathParser#equalityExpression.
    def enterEqualityExpression(self, ctx: fhirpathParser.EqualityExpressionContext):
        self._enter(ctx)

    # Exit a parse tree produced by fhirpathParser#equalityExpression.
    def exitEqualityExpression(self, ctx: fhirpathParser.EqualityExpressionContext):
        node, parentNode, code = self._exit(ctx)
        op = ctx.children[1].getText()
        if op in ["=", "!="]:
            new_op = "==" if op == "=" else "!="
            new_code = None
            if code[0].code.startswith("fhirpath_utils.get(") and len(code[0].code.split(",")) == 2 and (code[1].code.startswith("['") or re.search("^\\[[0-9]+\\]$", code[1].code)):
                parts = code[0].code[19:-1].split(",")
                var_type = self.var_types.get(parts[0], None)
                elem_type, is_list = utils.get_type(var_type, parts[1][1:-1]) if var_type else (None, None)
                if elem_type:
                    if self._is_value_type(elem_type):
                        getstr = ".value"
                    else:
                        getstr = ""
                    params_code = f"{parts[0]}.{parts[1][1:-1]}"
                    strcomp = code[1].code[1:-1]
                    if is_list:
                        v1 = self._get_new_varname()
                        new_code = f"[{v1}{getstr} {new_op} {strcomp} for {v1} in {params_code} or []]"
                    else:
                        if getstr == ".value":
                            proj = f"getattr({params_code}, 'value', None)"
                        else:
                            proj = f"{params_code}"
                        new_code = f"[{proj} {new_op} {strcomp}]"
            elif re.search("^\\[[0-9]+\\]$", code[1].code) and code[0].code.startswith("[len("):
                new_code = f"[{code[0].code[1:-1]} {new_op} {code[1].code[1:-1]}]"
            elif code[0].code.startswith("[") and (code[1].code.startswith("['") or re.search("^\\[[0-9]+\\]$", code[1].code)):
                simple = False
                inner = code[0].code[1:-1]
                strcomp = code[1].code[1:-1]
                getstr = None
                if re.search("^[A-Za-z_][A-Za-z0-9_]*$", inner):
                    simple = True
                    var_type = self.var_types.get(inner, None)
                    if self._is_value_type(var_type):
                        getstr = ".value"
                    else:
                        getstr = ""
                elif inner.startswith("'"):
                    simple = True
                elif inner in ["True", "False"]:
                    simple = True
                elif re.search("^[0-9]+$", inner):
                    simple = True
                elif re.search("^[0-9]+\\.[0-9]+$", inner):
                    simple = True
                elif inner.startswith("fhirpath_utils.System"):
                    simple = True
                if simple:
                    if getstr == ".value":
                        proj = f"getattr({inner}, 'value', None)"
                    else:
                        proj = f"{inner}"
                    new_code = f"[{proj} {new_op} {strcomp}]"
            elif code[0].code.startswith("[") and (code[1].code == "[False]" or code[1].code == "[True]"):
                inner = code[0].code[1:-1]
                bcomp = code[1].code[1:-1]
                if inner.startswith("bool("):
                    if bcomp == "True" and op == "=" or bcomp == "False" and op == "!=":
                        new_code = inner
                    else:
                        new_code = f"[not({inner[5:-1]})]"
                elif inner.startswith("not("):
                    if bcomp == "True" and op == "=" or bcomp == "False" and op == "!=":
                        new_code = inner
                    else:
                        new_code = f"[bool({inner[4:-1]})]"
                else:
                    comp = ast.parse(code[0].code, mode="eval")
                    if isinstance(comp.body, ast.List) and len(comp.body.elts) == 1:
                        if bcomp == "True" and op == "=" or bcomp == "False" and op == "!=":
                            new_code = inner
                        else:
                            if inner.endswith("is not None)"):
                                new_code = f"[{inner[:-10]} None)]"
                            elif inner.endswith("is None)"):
                                new_code = f"[{inner[:-6]} not None)]"
                            else:
                                new_code = f"[not({inner})]"
            if new_code is None:
                new_code = "fhirpath_utils.equals(%s, '%s', %s)" % (code[0].code, new_op, code[1].code)
            parentNode["py_code"][ctx] = PythonCode(new_code, bool)
        elif op in  ["~", "!~"]:
            parentNode["py_code"][ctx] = PythonCode("fhirpath_utils.equivalent(%s, '%s', %s)" % (code[0].code, op, code[1].code), bool)
        else:
            raise NotImplementedError("Not implemented: equality expr")

    def _is_value_type(self, elem_type):
        return elem_type == self.o_module.string or elem_type == self.o_module.uri or elem_type == self.o_module.code or inspect.get_annotations(elem_type.__init__).get("value", "").endswith("Enum")

    # Enter a parse tree produced by fhirpathParser#impliesExpression.
    def enterImpliesExpression(self, ctx: fhirpathParser.ImpliesExpressionContext):
        self._enter(ctx)

    # Exit a parse tree produced by fhirpathParser#impliesExpression.
    def exitImpliesExpression(self, ctx: fhirpathParser.ImpliesExpressionContext):
        node, parentNode, code = self._exit(ctx)
        parentNode["py_code"][ctx] = PythonCode("fhirpath_utils.bool_implies(%s, %s)" % (code[0].code, code[1].code), bool)

    # Enter a parse tree produced by fhirpathParser#termExpression.
    def enterTermExpression(self, ctx: fhirpathParser.TermExpressionContext):
        self._enter(ctx)

    # Exit a parse tree produced by fhirpathParser#termExpression.
    def exitTermExpression(self, ctx: fhirpathParser.TermExpressionContext):
        node, parentNode, code, = self._exit(ctx)
        parentNode["py_code"][ctx] = code[0]

    # Enter a parse tree produced by fhirpathParser#typeExpression.
    def enterTypeExpression(self, ctx: fhirpathParser.TypeExpressionContext):
        self._enter(ctx)

    # Exit a parse tree produced by fhirpathParser#typeExpression.
    def exitTypeExpression(self, ctx: fhirpathParser.TypeExpressionContext):
        node, parentNode, code, = self._exit(ctx)
        op = ctx.children[1].getText()
        if op == "is":
            out_type = bool
        else:
            out_type = self.utils.gettype_fromspec(code[1].code)
        parentNode["py_code"][ctx] = PythonCode("fhirpath_utils.%s_type(%s, '%s')" % (op, code[0].code, code[1].code), out_type)

    # Enter a parse tree produced by fhirpathParser#invocationTerm.
    def enterInvocationTerm(self, ctx: fhirpathParser.InvocationTermContext):
        self._enter(ctx)

    # Exit a parse tree produced by fhirpathParser#invocationTerm.
    def exitInvocationTerm(self, ctx: fhirpathParser.InvocationTermContext):
        node, parentNode, code = self._exit(ctx)
        parentNode["py_code"][ctx] = code[0]

    # Enter a parse tree produced by fhirpathParser#literalTerm.
    def enterLiteralTerm(self, ctx: fhirpathParser.LiteralTermContext):
        self._enter(ctx)

    # Exit a parse tree produced by fhirpathParser#literalTerm.
    def exitLiteralTerm(self, ctx: fhirpathParser.LiteralTermContext):
        node, parentNode, code = self._exit(ctx)
        parentNode["py_code"][ctx] = code[0]

    # Enter a parse tree produced by fhirpathParser#externalConstantTerm.
    def enterExternalConstantTerm(self, ctx: fhirpathParser.ExternalConstantTermContext):
        self._enter(ctx)

    # Exit a parse tree produced by fhirpathParser#externalConstantTerm.
    def exitExternalConstantTerm(self, ctx: fhirpathParser.ExternalConstantTermContext):
        node, parentNode, code = self._exit(ctx)
        parentNode["py_code"][ctx] = code[0]

    # Enter a parse tree produced by fhirpathParser#parenthesizedTerm.
    def enterParenthesizedTerm(self, ctx: fhirpathParser.ParenthesizedTermContext):
        self._enter(ctx)

    # Exit a parse tree produced by fhirpathParser#parenthesizedTerm.
    def exitParenthesizedTerm(self, ctx: fhirpathParser.ParenthesizedTermContext):
        node, parentNode, code = self._exit(ctx)
        parentNode["py_code"][ctx] = code[0]

    # Enter a parse tree produced by fhirpathParser#nullLiteral.
    def enterNullLiteral(self, ctx: fhirpathParser.NullLiteralContext):
        self._enter(ctx)

    # Exit a parse tree produced by fhirpathParser#nullLiteral.
    def exitNullLiteral(self, ctx: fhirpathParser.NullLiteralContext):
        node, parentNode, code = self._exit(ctx)
        parentNode["py_code"][ctx] = PythonCode("[]", None)

    # Enter a parse tree produced by fhirpathParser#booleanLiteral.
    def enterBooleanLiteral(self, ctx: fhirpathParser.BooleanLiteralContext):
        self._enter(ctx)

    # Exit a parse tree produced by fhirpathParser#booleanLiteral.
    def exitBooleanLiteral(self, ctx: fhirpathParser.BooleanLiteralContext):
        node, parentNode, code = self._exit(ctx)
        parentNode["py_code"][ctx] = PythonCode("[%s]" % ctx.getText().title(), None)

    # Enter a parse tree produced by fhirpathParser#stringLiteral.
    def enterStringLiteral(self, ctx: fhirpathParser.StringLiteralContext):
        self._enter(ctx)

    # Exit a parse tree produced by fhirpathParser#stringLiteral.
    def exitStringLiteral(self, ctx: fhirpathParser.StringLiteralContext):
        node, parentNode, code = self._exit(ctx)
        parentNode["py_code"][ctx] = PythonCode("[%s]" % ctx.getText().replace("\\`", "`"), str)

    # Enter a parse tree produced by fhirpathParser#numberLiteral.
    def enterNumberLiteral(self, ctx: fhirpathParser.NumberLiteralContext):
        self._enter(ctx)

    # Exit a parse tree produced by fhirpathParser#numberLiteral.
    def exitNumberLiteral(self, ctx: fhirpathParser.NumberLiteralContext):
        node, parentNode, code = self._exit(ctx)
        number = ctx.getText()
        if "." in number:
            parentNode["py_code"][ctx] = PythonCode("[decimal.Decimal('%s')]" % number, decimal.Decimal)
        else:
            parentNode["py_code"][ctx] = PythonCode("[%s]" % number, int)

    # Enter a parse tree produced by fhirpathParser#dateLiteral.
    def enterDateLiteral(self, ctx: fhirpathParser.DateLiteralContext):
        self._enter(ctx)

    # Exit a parse tree produced by fhirpathParser#dateLiteral.
    def exitDateLiteral(self, ctx: fhirpathParser.DateLiteralContext):
        node, parentNode, code = self._exit(ctx)
        parentNode["py_code"][ctx] = PythonCode("[fhirpath_utils.SystemDate(value='%s')]" % (ctx.getText()[1:]), getattr(self.o_module, "date"))

    # Enter a parse tree produced by fhirpathParser#dateTimeLiteral.
    def enterDateTimeLiteral(self, ctx: fhirpathParser.DateTimeLiteralContext):
        self._enter(ctx)

    # Exit a parse tree produced by fhirpathParser#dateTimeLiteral.
    def exitDateTimeLiteral(self, ctx: fhirpathParser.DateTimeLiteralContext):
        node, parentNode, code = self._exit(ctx)
        parentNode["py_code"][ctx] = PythonCode("[fhirpath_utils.SystemDateTime(value='%s')]" % (ctx.getText()[1:]), getattr(self.o_module, "dateTime"))

    # Enter a parse tree produced by fhirpathParser#timeLiteral.
    def enterTimeLiteral(self, ctx: fhirpathParser.TimeLiteralContext):
        self._enter(ctx)

    # Exit a parse tree produced by fhirpathParser#timeLiteral.
    def exitTimeLiteral(self, ctx: fhirpathParser.TimeLiteralContext):
        node, parentNode, code = self._exit(ctx)
        parentNode["py_code"][ctx] = PythonCode("[fhirpath_utils.SystemTime(value='%s')]" % (ctx.getText()[2:]), getattr(self.o_module, "time"))

    # Enter a parse tree produced by fhirpathParser#quantityLiteral.
    def enterQuantityLiteral(self, ctx: fhirpathParser.QuantityLiteralContext):
        self._enter(ctx)

    # Exit a parse tree produced by fhirpathParser#quantityLiteral.
    def exitQuantityLiteral(self, ctx: fhirpathParser.QuantityLiteralContext):
        node, parentNode, code = self._exit(ctx)
        parentNode["py_code"][ctx] = code[0]

    # Enter a parse tree produced by fhirpathParser#externalConstant.
    def enterExternalConstant(self, ctx: fhirpathParser.ExternalConstantContext):
        self._enter(ctx)

    # Exit a parse tree produced by fhirpathParser#externalConstant.
    def exitExternalConstant(self, ctx: fhirpathParser.ExternalConstantContext):
        node, parentNode, code = self._exit(ctx)
        constant = ctx.getText()[1:].replace('"', "").replace("`", "")
        if constant == "resource" or constant == "context":
            py_code = self.this
            out_type = self.var_types["$this"]
        elif constant == "ucum":
            py_code = "['http://unitsofmeasure.org']"
            out_type = str
        elif constant == "sct":
            py_code = "['http://snomed.info/sct']"
            out_type = str
        elif constant == "loinc":
            py_code = "['http://loinc.org']"
            out_type = str
        elif constant.startswith("vs-"):
            py_code = "['http://hl7.org/fhir/ValueSet/%s']" % constant[3:]
            out_type = str
        elif constant.startswith("ext-"):
            py_code = "['http://hl7.org/fhir/StructureDefinition/%s']" % constant[4:]
            out_type = str
        elif constant in self.var_types:
            py_code = self._handle_var(constant, get=False)
            out_type = self.var_types[constant]
        else:
            raise BaseException("Unkonwn external constant %s" % constant)
        parentNode["py_code"][ctx] = PythonCode(py_code, out_type)

    # Enter a parse tree produced by fhirpathParser#memberInvocation.
    def enterMemberInvocation(self, ctx: fhirpathParser.MemberInvocationContext):
        self._enter(ctx)

    # Exit a parse tree produced by fhirpathParser#memberInvocation.
    def exitMemberInvocation(self, ctx: fhirpathParser.MemberInvocationContext):
        node, parentNode, code = self._exit(ctx)
        parentNode["py_code"][ctx] = code[0]

    # Enter a parse tree produced by fhirpathParser#functionInvocation.
    def enterFunctionInvocation(self, ctx: fhirpathParser.FunctionInvocationContext):
        self._enter(ctx)

    # Exit a parse tree produced by fhirpathParser#functionInvocation.
    def exitFunctionInvocation(self, ctx: fhirpathParser.FunctionInvocationContext):
        node, parentNode, code = self._exit(ctx)
        parentNode["py_code"][ctx] = code[0]

    # Enter a parse tree produced by fhirpathParser#thisInvocation.
    def enterThisInvocation(self, ctx: fhirpathParser.ThisInvocationContext):
        self._enter(ctx)

    # Exit a parse tree produced by fhirpathParser#thisInvocation.
    def exitThisInvocation(self, ctx: fhirpathParser.ThisInvocationContext):
        node, parentNode, code = self._exit(ctx)
        if self.where_vars:
            where_var = self.where_vars[-1]
            code = where_var.code
            out_type = where_var.out_type
            single_val = where_var.single_val
        else:
            code = self.this
            out_type = self.var_types["$this"]
            single_val = True
        if single_val:
            parentNode["py_code"][ctx] = PythonCode("[%s]" % code, out_type)
        else:
            parentNode["py_code"][ctx] = PythonCode("%s" % code, out_type)

    # Enter a parse tree produced by fhirpathParser#indexInvocation.
    def enterIndexInvocation(self, ctx: fhirpathParser.IndexInvocationContext):
        self._enter(ctx)

    # Exit a parse tree produced by fhirpathParser#indexInvocation.
    def exitIndexInvocation(self, ctx: fhirpathParser.IndexInvocationContext):
        node, parentNode, code = self._exit(ctx)
        where_var = self.where_vars[-3]
        code = where_var.code
        out_type = where_var.out_type
        parentNode["py_code"][ctx] = PythonCode("%s" % code, out_type)

    # Enter a parse tree produced by fhirpathParser#totalInvocation.
    def enterTotalInvocation(self, ctx: fhirpathParser.TotalInvocationContext):
        self._enter(ctx)

    # Exit a parse tree produced by fhirpathParser#totalInvocation.
    def exitTotalInvocation(self, ctx: fhirpathParser.TotalInvocationContext):
        node, parentNode, code = self._exit(ctx)
        where_var = self.where_vars[-2]
        code = where_var.code
        out_type = where_var.out_type
        parentNode["py_code"][ctx] = PythonCode("%s" % code, out_type)

    # Enter a parse tree produced by fhirpathParser#function.
    def enterFunction(self, ctx: fhirpathParser.FunctionContext):
        self._enter(ctx)
        name = ctx.children[0].getText()
        if name in ["where", "select", "trace", "all", "repeat", "aggregate", "exists"]:
            context = next(iter(self.parentStack[-3]["py_code"].items()))[1]
            varname = self._get_new_varname(context.out_type)
            single_val = True
            if name == "aggregate":
                single_val = False
                varname_total = self._get_new_varname()
                varname_index = self._get_new_varname()
                self.where_vars.append(PythonCode(varname_total, context.out_type))
                self.where_vars.append(PythonCode(varname_index, context.out_type))
            self.where_vars.append(PythonCode(varname, context.out_type, single_val=single_val))

    # Exit a parse tree produced by fhirpathParser#function.
    # # are placeholders for code that is generated at a later point in time and will be replaced afterwards
    def exitFunction(self, ctx: fhirpathParser.FunctionContext):
        node, parentNode, code = self._exit(ctx)
        function_name = code[0].code
        params = code[1] if len(code) > 1 else []
        if function_name == "lower":
            py_code = PythonCode("fhirpath_utils.lower(🔥)", str)
        elif function_name == "upper":
            py_code = PythonCode("fhirpath_utils.upper(🔥)", str)
        elif function_name == "substring":
            py_code = PythonCode("fhirpath_utils.substring(🔥,%s,%s)" % (params[0].code, params[1].code if len(params) > 1 else "[]"), str)
        elif function_name == "now":
            py_code = PythonCode("[one_timestamp]", datetime.datetime)
        elif function_name == "today":
            py_code = PythonCode("[one_timestamp.date()]", datetime.date)
        elif function_name == "timeOfDay":
            py_code = PythonCode("[one_timestamp.time()]", datetime.time)
        elif function_name == "exists":
            var = self.where_vars.pop()
            if len(params) > 0:
                where_code = params[0].code.replace("🔥", var.code)
                where_part = "%s == [True]" % where_code
                if where_code.startswith("["):
                    comp = ast.parse(where_code, mode="eval")
                    if isinstance(comp.body, ast.List) and len(comp.body.elts) == 1:
                        where_part = where_code[1:-1]
                invocation = "[bool([%s for %s in 🔥 if %s])]" % (var.code, var.code, where_part)
                py_code = PythonCode(invocation, var.out_type, list_func=True)
            else:
                py_code = PythonCode("[bool(🔥)]", bool, list_func=True)

        elif function_name == "length":
            py_code = PythonCode("fhirpath_utils.strlength(🔥)", int)
        elif function_name == "toChars":
            py_code = PythonCode("fhirpath_utils.toChars(🔥)", str)
        elif function_name == "empty":
            py_code = PythonCode("[not(🔥)]", bool, list_func=True)
        elif function_name == "round":
            if len(params) > 0:
                py_code = PythonCode("fhirpath_utils.decimal_round(🔥, %s)" % params[0].code, decimal.Decimal, list_func=True)
            else:
                py_code = PythonCode("fhirpath_utils.decimal_round(🔥, [0])", decimal.Decimal, list_func=True)
        elif function_name == "truncate":
            py_code = PythonCode("fhirpath_utils.decimal_truncate(🔥)", int, list_func=True)
        elif function_name == "sqrt":
            py_code = PythonCode("fhirpath_utils.decimal_sqrt(🔥)", decimal.Decimal, list_func=True)
        elif function_name == "abs":
            py_code = PythonCode("fhirpath_utils.decimal_abs(🔥)", decimal.Decimal, list_func=True)
        elif function_name == "ceiling":
            py_code = PythonCode("fhirpath_utils.decimal_ceiling(🔥)", int, list_func=True)
        elif function_name == "floor":
            py_code = PythonCode("fhirpath_utils.decimal_floor(🔥)", int, list_func=True)
        elif function_name == "exp":
            py_code = PythonCode("fhirpath_utils.decimal_exp(🔥)", decimal.Decimal, list_func=True)
        elif function_name == "ln":
            py_code = PythonCode("fhirpath_utils.decimal_ln(🔥)", decimal.Decimal, list_func=True)
        elif function_name == "log":
            py_code = PythonCode("fhirpath_utils.decimal_log(🔥, %s)" % params[0].code, decimal.Decimal, list_func=True)
        elif function_name == "power":
            py_code = PythonCode("fhirpath_utils.decimal_power(🔥, %s)" % params[0].code, decimal.Decimal, list_func=True)
        elif function_name == "select":
            var = self.where_vars.pop()
            v1 = self._get_new_varname()
            where_code = params[0].code.replace("🔥", var.code)
            invocation = f"[{v1} for {var.code} in 🔥 for {v1} in {where_code}]"
            py_code = PythonCode(invocation, params[0].out_type, list_func=True)
        elif function_name == "where":
            var = self.where_vars.pop()
            where_code = params[0].code.replace("🔥", var.code)
            where_part = "%s == [True]" % where_code
            if where_code.startswith("["):
                comp = ast.parse(where_code, mode="eval")
                if isinstance(comp.body, ast.List) and len(comp.body.elts) == 1:
                    where_part = where_code[1:-1]
            invocation = "[%s for %s in 🔥 if %s]" % (var.code, var.code, where_part)
            py_code = PythonCode(invocation, var.out_type, list_func=True)
        elif function_name == "all":
            var = self.where_vars.pop()
            where_code = params[0].code.replace("🔥", var.code)
            where_part = "%s == [True]" % where_code
            if where_code.startswith("["):
                comp = ast.parse(where_code, mode="eval")
                if isinstance(comp.body, ast.List) and len(comp.body.elts) == 1:
                    where_part = where_code[1:-1]
            invocation = "[all(%s for %s in 🔥)]" % (where_part, var.code)
            py_code = PythonCode(invocation, bool, list_func=True)
        elif function_name == "repeat":
            var = self.where_vars.pop()
            where_code = params[0].code
            py_code = PythonCode("fhirpath_utils.repeat(🔥, lambda %s: %s)" % (var.code, where_code), params[0].out_type, list_func=True)
        elif function_name == "aggregate":
            var = self.where_vars.pop()
            var_total = self.where_vars.pop()
            var_index = self.where_vars.pop()
            where_code = params[0].code
            init_code = params[1].code if len(params) > 1 else "{}"
            py_code = PythonCode("fhirpath_utils.aggregate(🔥, lambda %s, %s, %s: %s, %s)" % (var.code, var_index.code, var_total.code, where_code, init_code), params[0].out_type, list_func=True)
        elif function_name == "matches":
            py_code = PythonCode("fhirpath_utils.matches(🔥, %s)" % params[0].code, bool)
        elif function_name == "contains":
            py_code = PythonCode("fhirpath_utils.contains(🔥, %s)" % params[0].code, bool)
        elif function_name == "startsWith":
            py_code = PythonCode("fhirpath_utils.startswith(🔥, %s)" % params[0].code, bool)
        elif function_name == "endsWith":
            py_code = PythonCode("fhirpath_utils.endswith(🔥, %s)" % params[0].code, bool)
        elif function_name == "not":
            py_code = PythonCode("fhirpath_utils.bool_not(🔥)", bool, list_func=True)
        elif function_name == "skip":
            py_code = PythonCode("fhirpath_utils.skip(🔥, %s)" % params[0].code, "🔥", list_func=True)
        elif function_name == "take":
            py_code = PythonCode("fhirpath_utils.take(🔥, %s)" % params[0].code, "🔥", list_func=True)
        elif function_name == "first":
            py_code = PythonCode("fhirpath_utils.first(🔥)", "🔥", list_func=True)
        elif function_name == "last":
            py_code = PythonCode("fhirpath_utils.last(🔥)", "🔥", list_func=True)
        elif function_name == "tail":
            py_code = PythonCode("fhirpath_utils.tail(🔥)", "🔥", list_func=True)
        elif function_name == "children":
            py_code = PythonCode("fhirpath_utils.children(🔥)", None, list_func=True)
        elif function_name == "descendants":
            py_code = PythonCode("fhirpath_utils.descendants(🔥)", None, list_func=True)
        elif function_name == "count":
            py_code = PythonCode("[len(🔥)]", int, list_func=True)
        elif function_name == "allTrue":
            py_code = PythonCode("fhirpath_utils.allTrue(🔥)", bool, list_func=True)
        elif function_name == "allFalse":
            py_code = PythonCode("fhirpath_utils.allFalse(🔥)", bool, list_func=True)
        elif function_name == "anyTrue":
            py_code = PythonCode("fhirpath_utils.anyTrue(🔥)", bool, list_func=True)
        elif function_name == "anyFalse":
            py_code = PythonCode("fhirpath_utils.anyFalse(🔥)", bool, list_func=True)
        elif function_name == "iif":
            where_code = params[0].code
            where_part = "%s == [True]" % where_code
            if where_code.startswith("["):
                comp = ast.parse(where_code, mode="eval")
                if isinstance(comp.body, ast.List) and len(comp.body.elts) == 1:
                    where_part = where_code[1:-1]
            py_code = PythonCode("(%s if %s else %s)" % (params[1].code, where_part, params[2].code), "🔥", list_func=True)
        elif function_name == "union":
            py_code = PythonCode("fhirpath_utils.union(🔥, %s)" % params[0].code, params[0].out_type, list_func=True)
        elif function_name == "combine":
            py_code = PythonCode("(🔥 + %s)" % params[0].code, params[0].out_type, list_func=True)
        elif function_name == "exclude":
            py_code = PythonCode("fhirpath_utils.exclude(🔥, %s)" % params[0].code, params[0].out_type, list_func=True)
        elif function_name == "single":
            py_code = PythonCode("fhirpath_utils.single(🔥)", "🔥", list_func=True)
        elif function_name == "trace":
            var = self.where_vars.pop()
            if len(params) > 0:
                v1 = self._get_new_varname()
                invocation = f"[{v1} for {var.code} in 🔥 for {v1} in {params[0].code}]"
                py_code = PythonCode("fhirpath_utils.trace(🔥, %s, %s)" % (params[0].code, invocation), "🔥", list_func=True)
            else:
                py_code = PythonCode("fhirpath_utils.trace(🔥, %s)" % (params[0].code), "🔥", list_func=True)
        elif function_name == "subsetOf":
            py_code = PythonCode("fhirpath_utils.subset_of(🔥, %s)" % params[0].code, bool, list_func=True)
        elif function_name == "supersetOf":
            py_code = PythonCode("fhirpath_utils.superset_of(🔥, %s)" % params[0].code, bool, list_func=True)
        elif function_name == "intersect":
            py_code = PythonCode("fhirpath_utils.intersect(🔥, %s)" % params[0].code, params[0].out_type, list_func=True)
        elif function_name == "distinct":
            py_code = PythonCode("fhirpath_utils.distinct(🔥)", "🔥", list_func=True)
        elif function_name == "isDistinct":
            py_code = PythonCode("fhirpath_utils.is_distinct(🔥)", bool, list_func=True)
        elif function_name == "toString":
            py_code = PythonCode("fhirpath_utils.toString(🔥)", str, list_func=True)
        elif function_name == "convertsToString":
            py_code = PythonCode("fhirpath_utils.convertsToString(🔥)", bool, list_func=True)
        elif function_name == "toBoolean":
            py_code = PythonCode("fhirpath_utils.toBoolean(🔥)", bool, list_func=True)
        elif function_name == "convertsToBoolean":
            py_code = PythonCode("fhirpath_utils.convertsToBoolean(🔥)", bool, list_func=True)
        elif function_name == "toInteger":
            py_code = PythonCode("fhirpath_utils.toInteger(🔥)", int, list_func=True)
        elif function_name == "convertsToInteger":
            py_code = PythonCode("fhirpath_utils.convertsToInteger(🔥)", bool, list_func=True)
        elif function_name == "toDecimal":
            py_code = PythonCode("fhirpath_utils.toDecimal(🔥)", decimal.Decimal, list_func=True)
        elif function_name == "convertsToDecimal":
            py_code = PythonCode("fhirpath_utils.convertsToDecimal(🔥)", bool, list_func=True)
        elif function_name == "toQuantity":
            py_code = PythonCode("fhirpath_utils.toQuantity(🔥, %s)" % (params[0].code if params else "[]"), getattr(self.o_module, "Quantity"), list_func=True)
        elif function_name == "convertsToQuantity":
            py_code = PythonCode("fhirpath_utils.convertsToQuantity(🔥, %s)" % (params[0].code if params else "[]"), bool, list_func=True)
        elif function_name == "toDate":
            py_code = PythonCode("fhirpath_utils.toDate(🔥)", getattr(self.o_module, "date"), list_func=True)
        elif function_name == "convertsToDate":
            py_code = PythonCode("fhirpath_utils.convertsToDate(🔥)", bool, list_func=True)
        elif function_name == "toDateTime":
            py_code = PythonCode("fhirpath_utils.toDateTime(🔥)", getattr(self.o_module, "dateTime"), list_func=True)
        elif function_name == "convertsToDateTime":
            py_code = PythonCode("fhirpath_utils.convertsToDateTime(🔥)", bool, list_func=True)
        elif function_name == "toTime":
            py_code = PythonCode("fhirpath_utils.toTime(🔥)", getattr(self.o_module, "time"), list_func=True)
        elif function_name == "convertsToTime":
            py_code = PythonCode("fhirpath_utils.convertsToTime(🔥)", bool, list_func=True)
        elif function_name == "type":
            py_code = PythonCode("fhirpath_utils.gettype(🔥)", None)
        elif function_name == "is":
            type_ = ctx.children[-2].getText().replace("`", "")
            py_code = PythonCode("fhirpath_utils.is_type(🔥, '%s')" % type_, bool, list_func=True)
        elif function_name == "as":
            type_ = ctx.children[-2].getText().replace("`", "")
            out_type = self.utils.gettype_fromspec(type_)
            py_code = PythonCode("fhirpath_utils.as_type(🔥, '%s')" % type_, out_type, list_func=True)
        elif function_name == "ofType":
            type_ = ctx.children[-2].getText().replace("`", "")
            out_type = self.utils.gettype_fromspec(type_)
            v1 = self._get_new_varname()
            py_code = PythonCode("[%s for %s in 🔥 if fhirpath_utils.is_type(%s, '%s') == [True]]" % (v1, v1, v1, type_), out_type, list_func=True)
        elif function_name == "conformsTo":
            py_code = PythonCode("fhirpath_utils.conformsTo(🔥, %s)" % params[0].code, bool, list_func=True)
        elif function_name == "extension":
            py_code = PythonCode("fhirpath_utils.extension(🔥, %s)" % params[0].code, getattr(self.o_module, "Extension"))
        elif function_name == "resolve":
            py_code = PythonCode("fhirpath_utils.resolve(🔥, [%s])" % ", ".join(self.resolve_ctx), None)
        elif function_name == "indexOf":
            py_code = PythonCode("fhirpath_utils.indexof(🔥, %s)" % params[0].code, int)
        else:
            raise NotImplementedError("Not implemented function %s" % function_name)
        parentNode["py_code"][ctx] = py_code

    # Enter a parse tree produced by fhirpathParser#paramList.
    def enterParamList(self, ctx: fhirpathParser.ParamListContext):
        self._enter(ctx)

    # Exit a parse tree produced by fhirpathParser#paramList.
    def exitParamList(self, ctx: fhirpathParser.ParamListContext):
        node, parentNode, code = self._exit(ctx)
        parentNode["py_code"][ctx] = code

    # Enter a parse tree produced by fhirpathParser#quantity.
    def enterQuantity(self, ctx: fhirpathParser.QuantityContext):
        self._enter(ctx)

    # Exit a parse tree produced by fhirpathParser#quantity.
    def exitQuantity(self, ctx: fhirpathParser.QuantityContext):
        node, parentNode, code = self._exit(ctx)
        number = ctx.children[0].getText()
        unit = code[0].code
        parentNode["py_code"][ctx] = PythonCode("[fhirpath_utils.SystemQuantity(value=%s.decimal(value=decimal.Decimal('%s')), %s)]" % (self.o_module.__name__, number, unit), self.utils.SystemQuantity)

    # Enter a parse tree produced by fhirpathParser#unit.
    def enterUnit(self, ctx: fhirpathParser.UnitContext):
        self._enter(ctx)

    # Exit a parse tree produced by fhirpathParser#unit.
    def exitUnit(self, ctx: fhirpathParser.UnitContext):
        node, parentNode, code = self._exit(ctx)
        if code:
            parentNode["py_code"][ctx] = code[0]
        else:
            parentNode["py_code"][ctx] = PythonCode("code=%s.string(value=%s), system=%s.string('http://unitsofmeasure.org')" % (self.o_module.__name__, ctx.getText(), self.o_module.__name__), str)

    # Enter a parse tree produced by fhirpathParser#dateTimePrecision.
    def enterDateTimePrecision(self, ctx: fhirpathParser.DateTimePrecisionContext):
        self._enter(ctx)

    # Exit a parse tree produced by fhirpathParser#dateTimePrecision.
    def exitDateTimePrecision(self, ctx: fhirpathParser.DateTimePrecisionContext):
        node, parentNode, code = self._exit(ctx)
        parentNode["py_code"][ctx] = PythonCode("unit=%s.string(value='%s')" % (self.o_module.__name__, ctx.getText()), str)

    # Enter a parse tree produced by fhirpathParser#pluralDateTimePrecision.
    def enterPluralDateTimePrecision(self, ctx: fhirpathParser.PluralDateTimePrecisionContext):
        self._enter(ctx)

    # Exit a parse tree produced by fhirpathParser#pluralDateTimePrecision.
    def exitPluralDateTimePrecision(self, ctx: fhirpathParser.PluralDateTimePrecisionContext):
        node, parentNode, code = self._exit(ctx)
        parentNode["py_code"][ctx] = PythonCode("unit=%s.string(value='%s')" % (self.o_module.__name__, ctx.getText()), str)

    # Enter a parse tree produced by fhirpathParser#typeSpecifier.
    def enterTypeSpecifier(self, ctx: fhirpathParser.TypeSpecifierContext):
        self._enter(ctx)

    # Exit a parse tree produced by fhirpathParser#typeSpecifier.
    def exitTypeSpecifier(self, ctx: fhirpathParser.TypeSpecifierContext):
        node, parentNode, code = self._exit(ctx)
        parentNode["py_code"][ctx] = code[0]

    # Enter a parse tree produced by fhirpathParser#qualifiedIdentifier.
    def enterQualifiedIdentifier(self, ctx: fhirpathParser.QualifiedIdentifierContext):
        self._enter(ctx)

    # Exit a parse tree produced by fhirpathParser#qualifiedIdentifier.
    def exitQualifiedIdentifier(self, ctx: fhirpathParser.QualifiedIdentifierContext):
        node, parentNode, code = self._exit(ctx)
        parentNode["py_code"][ctx] = PythonCode(".".join([c.code for c in code]), None)

    # Enter a parse tree produced by fhirpathParser#identifier.
    def enterIdentifier(self, ctx: fhirpathParser.IdentifierContext):
        self._enter(ctx)

    # Exit a parse tree produced by fhirpathParser#identifier.
    def exitIdentifier(self, ctx: fhirpathParser.IdentifierContext):
        node, parentNode, code = self._exit(ctx)
        var = ctx.getText()
        var_type = self.var_types.get(var)
        if isinstance(ctx.parentCtx, fhirpathParser.MemberInvocationContext) and \
                len(ctx.parentCtx.parentCtx.children) > 1 and \
                ctx.parentCtx.parentCtx.children[-1] == ctx.parentCtx:
            var = var.replace("`", "")
            if var == "type":
                var = "type_"
        elif isinstance(ctx.parentCtx, fhirpathParser.FunctionContext) and \
                ctx.parentCtx.children[0] == ctx:
            pass
        elif isinstance(ctx.parentCtx, fhirpathParser.QualifiedIdentifierContext):
            var_type = None
        elif isinstance(ctx.parentCtx, fhirpathParser.ExternalConstantContext):
            var = "[%s]" % var.replace("`", "")
            var_type = self.var_types.get(var, None)
        else:
            if self.where_vars:
                where_var = self.where_vars[-1]
                out_type = where_var.out_type
                var_type, __ = utils.get_type(out_type, var)
                var = "fhirpath_utils.get(%s,'%s')" % (where_var.code, var.replace("`", ""))
            elif var in self.this_elem:
                var_type, __ = self.this_elem[var]
                var = "fhirpath_utils.get(%s,'%s')" % (self.this, var.replace("`", ""))
            else:
                var = self._handle_var(var.replace("`", ""))
        parentNode["py_code"][ctx] = PythonCode(var, var_type)

    def _handle_var(self, var, get=True):
        var_type = self.var_types.get(var)
        if var_type:
            self.resolve_ctx.add(var)
            if var_type.__name__ == "dateTime":
                var = "dateutil.parse(str(%s.value))" % var
            elif var_type.__name__ == "dateStringV3":
                var = "str(dateutil.parse(%s).isoformat())" % var
            if var_type != list:
                if var not in self.list_var:
                    var = "[%s]" % var
        elif get:
            var = "fhirpath_utils.get(%s,'%s')" % (self.this, var.replace("`", ""))
        else:
            var = "[%s]" % var
        return var

    def _enter(self, ctx):
        parentNode = self.parentStack[-1]
        node = {"py_code": OrderedDict()}
        for child in ctx.children:
            if not isinstance(child, TerminalNodeImpl):
                node["py_code"][child] = PythonCode("", None)
        self.parentStack.append(node)

    def _exit(self, ctx):
        node = self.parentStack.pop()
        parentNode = self.parentStack[-1]
        code = []
        for child in ctx.children:
            if not isinstance(child, TerminalNodeImpl):
                code.append(node["py_code"][child])
        return node, parentNode, code

    def _get_new_varname(self, var_type=None):
        self.counter += 1
        name = "v" + str(self.counter)
        self.var_types[name] = var_type
        return name

class PythonCode(object): # TODO:sbe add base class which is returned for every convert method

    def __init__(self, code, out_type, list_func=False, single_val=False):
        self.code = code
        self.out_type = out_type
        self.list_func = list_func
        self.single_val = single_val
        self.input_class = None
        self.module = None
        self.base_context = None

    def __str__(self) -> str:
        return self.code
    
    def execute(self, resource, context={}):
        if self.base_context is None:
            self.base_context = {
                "malac": malac,
                "dateutil": dateutil, 
                "datetime": datetime, 
                "decimal": decimal,
                "fhirpath_utils": fhirpath_utils.FHIRPathUtils(self.module),
            }
        base_context = self.base_context.copy()
        base_context["one_timestamp"] = datetime.datetime.now()
        base_context.update(context)
        if self.input_class:
            base_context[self.input_class.__name__] = resource
        else:
            base_context.update(resource)
        exec("__myresult__=" + self.code, base_context) # TODO: pass locals
        base_result = base_context["__myresult__"]
        if base_result is None:
            base_result = []
        elif not isinstance(base_result, list):
            base_result = [base_result]
        return base_result


class FHIRPathContext(object):
    
    def __init__(self, var_types, list_var, o_module, this, this_elem):
        self.var_types = var_types
        self.list_var = list_var
        self.this = this
        self.this_elem = this_elem
        self.o_module = o_module


def compile_factory(parseString, supermod):

    def compile(expression, input_class, model=None) -> PythonCode:
        model = model or supermod
        generator = parseString(expression) # TODO:sbe do simple syntax check of expression via fhirpathListener?

        var_types = {input_class.__name__: input_class, "$this": input_class}
        this_elem = {}
        for elem, __ in inspect.get_annotations(input_class.__init__).items():
            this_elem[elem] = utils.get_type(input_class, elem)

        context = FHIRPathContext(var_types, set(), model, input_class.__name__, this_elem)

        py_code = generator.convert(context=context)
        py_code.input_class = input_class
        py_code.module = model
        return py_code

    return compile

def evaluate_json_factory(supermod):

    simple_cache = dict()
    model_initialized = set()

    # example usage:
    # from malac.hd.core.fhir.r5.generator.fhirpath import evaluate_json
    # evaluate_json("birthDate", {"resourceType": "Patient", "birthDate": "1974-12-25"})
    def evaluate_json(expression, resource_json, model): # TODO:sbe add support for lists, add evaluate_xml, add tests
        model = model or supermod
        mod_res = fhir_utils.parse_json(model, resource_json) # TODO:sbe cache or add option to directly pass parsed json

        tpl = (expression, resource_json["resourceType"])
        if tpl in simple_cache:
            code = simple_cache[tpl]
        else:
            code = compile(expression, type(mod_res), model=model)
            simple_cache[tpl] = code
        base_result = code.execute(mod_res)

        result = []
        for r in base_result:
            result.append(r.exportJson())
        return result

    return evaluate_json