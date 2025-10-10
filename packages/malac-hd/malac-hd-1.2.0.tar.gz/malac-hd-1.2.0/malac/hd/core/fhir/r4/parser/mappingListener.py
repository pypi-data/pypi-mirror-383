# Generated from mapping.g4 by ANTLR 4.13.2
from antlr4 import *
if "." in __name__:
    from .mappingParser import mappingParser
else:
    from mappingParser import mappingParser

# This class defines a complete listener for a parse tree produced by mappingParser.
class mappingListener(ParseTreeListener):

    # Enter a parse tree produced by mappingParser#structureMap.
    def enterStructureMap(self, ctx:mappingParser.StructureMapContext):
        pass

    # Exit a parse tree produced by mappingParser#structureMap.
    def exitStructureMap(self, ctx:mappingParser.StructureMapContext):
        pass


    # Enter a parse tree produced by mappingParser#mapId.
    def enterMapId(self, ctx:mappingParser.MapIdContext):
        pass

    # Exit a parse tree produced by mappingParser#mapId.
    def exitMapId(self, ctx:mappingParser.MapIdContext):
        pass


    # Enter a parse tree produced by mappingParser#url.
    def enterUrl(self, ctx:mappingParser.UrlContext):
        pass

    # Exit a parse tree produced by mappingParser#url.
    def exitUrl(self, ctx:mappingParser.UrlContext):
        pass


    # Enter a parse tree produced by mappingParser#quoteidentifier.
    def enterQuoteidentifier(self, ctx:mappingParser.QuoteidentifierContext):
        pass

    # Exit a parse tree produced by mappingParser#quoteidentifier.
    def exitQuoteidentifier(self, ctx:mappingParser.QuoteidentifierContext):
        pass


    # Enter a parse tree produced by mappingParser#mapidentifier.
    def enterMapidentifier(self, ctx:mappingParser.MapidentifierContext):
        pass

    # Exit a parse tree produced by mappingParser#mapidentifier.
    def exitMapidentifier(self, ctx:mappingParser.MapidentifierContext):
        pass


    # Enter a parse tree produced by mappingParser#structure.
    def enterStructure(self, ctx:mappingParser.StructureContext):
        pass

    # Exit a parse tree produced by mappingParser#structure.
    def exitStructure(self, ctx:mappingParser.StructureContext):
        pass


    # Enter a parse tree produced by mappingParser#structureAlias.
    def enterStructureAlias(self, ctx:mappingParser.StructureAliasContext):
        pass

    # Exit a parse tree produced by mappingParser#structureAlias.
    def exitStructureAlias(self, ctx:mappingParser.StructureAliasContext):
        pass


    # Enter a parse tree produced by mappingParser#imports.
    def enterImports(self, ctx:mappingParser.ImportsContext):
        pass

    # Exit a parse tree produced by mappingParser#imports.
    def exitImports(self, ctx:mappingParser.ImportsContext):
        pass


    # Enter a parse tree produced by mappingParser#group.
    def enterGroup(self, ctx:mappingParser.GroupContext):
        pass

    # Exit a parse tree produced by mappingParser#group.
    def exitGroup(self, ctx:mappingParser.GroupContext):
        pass


    # Enter a parse tree produced by mappingParser#rules.
    def enterRules(self, ctx:mappingParser.RulesContext):
        pass

    # Exit a parse tree produced by mappingParser#rules.
    def exitRules(self, ctx:mappingParser.RulesContext):
        pass


    # Enter a parse tree produced by mappingParser#typeMode.
    def enterTypeMode(self, ctx:mappingParser.TypeModeContext):
        pass

    # Exit a parse tree produced by mappingParser#typeMode.
    def exitTypeMode(self, ctx:mappingParser.TypeModeContext):
        pass


    # Enter a parse tree produced by mappingParser#extends.
    def enterExtends(self, ctx:mappingParser.ExtendsContext):
        pass

    # Exit a parse tree produced by mappingParser#extends.
    def exitExtends(self, ctx:mappingParser.ExtendsContext):
        pass


    # Enter a parse tree produced by mappingParser#parameters.
    def enterParameters(self, ctx:mappingParser.ParametersContext):
        pass

    # Exit a parse tree produced by mappingParser#parameters.
    def exitParameters(self, ctx:mappingParser.ParametersContext):
        pass


    # Enter a parse tree produced by mappingParser#parameter.
    def enterParameter(self, ctx:mappingParser.ParameterContext):
        pass

    # Exit a parse tree produced by mappingParser#parameter.
    def exitParameter(self, ctx:mappingParser.ParameterContext):
        pass


    # Enter a parse tree produced by mappingParser#type.
    def enterType(self, ctx:mappingParser.TypeContext):
        pass

    # Exit a parse tree produced by mappingParser#type.
    def exitType(self, ctx:mappingParser.TypeContext):
        pass


    # Enter a parse tree produced by mappingParser#rule.
    def enterRule(self, ctx:mappingParser.RuleContext):
        pass

    # Exit a parse tree produced by mappingParser#rule.
    def exitRule(self, ctx:mappingParser.RuleContext):
        pass


    # Enter a parse tree produced by mappingParser#ruleName.
    def enterRuleName(self, ctx:mappingParser.RuleNameContext):
        pass

    # Exit a parse tree produced by mappingParser#ruleName.
    def exitRuleName(self, ctx:mappingParser.RuleNameContext):
        pass


    # Enter a parse tree produced by mappingParser#ruleSources.
    def enterRuleSources(self, ctx:mappingParser.RuleSourcesContext):
        pass

    # Exit a parse tree produced by mappingParser#ruleSources.
    def exitRuleSources(self, ctx:mappingParser.RuleSourcesContext):
        pass


    # Enter a parse tree produced by mappingParser#ruleSource.
    def enterRuleSource(self, ctx:mappingParser.RuleSourceContext):
        pass

    # Exit a parse tree produced by mappingParser#ruleSource.
    def exitRuleSource(self, ctx:mappingParser.RuleSourceContext):
        pass


    # Enter a parse tree produced by mappingParser#ruleTargets.
    def enterRuleTargets(self, ctx:mappingParser.RuleTargetsContext):
        pass

    # Exit a parse tree produced by mappingParser#ruleTargets.
    def exitRuleTargets(self, ctx:mappingParser.RuleTargetsContext):
        pass


    # Enter a parse tree produced by mappingParser#sourceType.
    def enterSourceType(self, ctx:mappingParser.SourceTypeContext):
        pass

    # Exit a parse tree produced by mappingParser#sourceType.
    def exitSourceType(self, ctx:mappingParser.SourceTypeContext):
        pass


    # Enter a parse tree produced by mappingParser#sourceCardinality.
    def enterSourceCardinality(self, ctx:mappingParser.SourceCardinalityContext):
        pass

    # Exit a parse tree produced by mappingParser#sourceCardinality.
    def exitSourceCardinality(self, ctx:mappingParser.SourceCardinalityContext):
        pass


    # Enter a parse tree produced by mappingParser#upperBound.
    def enterUpperBound(self, ctx:mappingParser.UpperBoundContext):
        pass

    # Exit a parse tree produced by mappingParser#upperBound.
    def exitUpperBound(self, ctx:mappingParser.UpperBoundContext):
        pass


    # Enter a parse tree produced by mappingParser#ruleContext.
    def enterRuleContext(self, ctx:mappingParser.RuleContextContext):
        pass

    # Exit a parse tree produced by mappingParser#ruleContext.
    def exitRuleContext(self, ctx:mappingParser.RuleContextContext):
        pass


    # Enter a parse tree produced by mappingParser#sourceDefault.
    def enterSourceDefault(self, ctx:mappingParser.SourceDefaultContext):
        pass

    # Exit a parse tree produced by mappingParser#sourceDefault.
    def exitSourceDefault(self, ctx:mappingParser.SourceDefaultContext):
        pass


    # Enter a parse tree produced by mappingParser#alias.
    def enterAlias(self, ctx:mappingParser.AliasContext):
        pass

    # Exit a parse tree produced by mappingParser#alias.
    def exitAlias(self, ctx:mappingParser.AliasContext):
        pass


    # Enter a parse tree produced by mappingParser#whereClause.
    def enterWhereClause(self, ctx:mappingParser.WhereClauseContext):
        pass

    # Exit a parse tree produced by mappingParser#whereClause.
    def exitWhereClause(self, ctx:mappingParser.WhereClauseContext):
        pass


    # Enter a parse tree produced by mappingParser#checkClause.
    def enterCheckClause(self, ctx:mappingParser.CheckClauseContext):
        pass

    # Exit a parse tree produced by mappingParser#checkClause.
    def exitCheckClause(self, ctx:mappingParser.CheckClauseContext):
        pass


    # Enter a parse tree produced by mappingParser#log.
    def enterLog(self, ctx:mappingParser.LogContext):
        pass

    # Exit a parse tree produced by mappingParser#log.
    def exitLog(self, ctx:mappingParser.LogContext):
        pass


    # Enter a parse tree produced by mappingParser#dependent.
    def enterDependent(self, ctx:mappingParser.DependentContext):
        pass

    # Exit a parse tree produced by mappingParser#dependent.
    def exitDependent(self, ctx:mappingParser.DependentContext):
        pass


    # Enter a parse tree produced by mappingParser#ruleTarget.
    def enterRuleTarget(self, ctx:mappingParser.RuleTargetContext):
        pass

    # Exit a parse tree produced by mappingParser#ruleTarget.
    def exitRuleTarget(self, ctx:mappingParser.RuleTargetContext):
        pass


    # Enter a parse tree produced by mappingParser#transform.
    def enterTransform(self, ctx:mappingParser.TransformContext):
        pass

    # Exit a parse tree produced by mappingParser#transform.
    def exitTransform(self, ctx:mappingParser.TransformContext):
        pass


    # Enter a parse tree produced by mappingParser#evaluate.
    def enterEvaluate(self, ctx:mappingParser.EvaluateContext):
        pass

    # Exit a parse tree produced by mappingParser#evaluate.
    def exitEvaluate(self, ctx:mappingParser.EvaluateContext):
        pass


    # Enter a parse tree produced by mappingParser#mapinvocation.
    def enterMapinvocation(self, ctx:mappingParser.MapinvocationContext):
        pass

    # Exit a parse tree produced by mappingParser#mapinvocation.
    def exitMapinvocation(self, ctx:mappingParser.MapinvocationContext):
        pass


    # Enter a parse tree produced by mappingParser#mapparamList.
    def enterMapparamList(self, ctx:mappingParser.MapparamListContext):
        pass

    # Exit a parse tree produced by mappingParser#mapparamList.
    def exitMapparamList(self, ctx:mappingParser.MapparamListContext):
        pass


    # Enter a parse tree produced by mappingParser#param.
    def enterParam(self, ctx:mappingParser.ParamContext):
        pass

    # Exit a parse tree produced by mappingParser#param.
    def exitParam(self, ctx:mappingParser.ParamContext):
        pass


    # Enter a parse tree produced by mappingParser#fhirPath.
    def enterFhirPath(self, ctx:mappingParser.FhirPathContext):
        pass

    # Exit a parse tree produced by mappingParser#fhirPath.
    def exitFhirPath(self, ctx:mappingParser.FhirPathContext):
        pass


    # Enter a parse tree produced by mappingParser#mapliteral.
    def enterMapliteral(self, ctx:mappingParser.MapliteralContext):
        pass

    # Exit a parse tree produced by mappingParser#mapliteral.
    def exitMapliteral(self, ctx:mappingParser.MapliteralContext):
        pass


    # Enter a parse tree produced by mappingParser#groupTypeMode.
    def enterGroupTypeMode(self, ctx:mappingParser.GroupTypeModeContext):
        pass

    # Exit a parse tree produced by mappingParser#groupTypeMode.
    def exitGroupTypeMode(self, ctx:mappingParser.GroupTypeModeContext):
        pass


    # Enter a parse tree produced by mappingParser#sourceListMode.
    def enterSourceListMode(self, ctx:mappingParser.SourceListModeContext):
        pass

    # Exit a parse tree produced by mappingParser#sourceListMode.
    def exitSourceListMode(self, ctx:mappingParser.SourceListModeContext):
        pass


    # Enter a parse tree produced by mappingParser#targetListMode.
    def enterTargetListMode(self, ctx:mappingParser.TargetListModeContext):
        pass

    # Exit a parse tree produced by mappingParser#targetListMode.
    def exitTargetListMode(self, ctx:mappingParser.TargetListModeContext):
        pass


    # Enter a parse tree produced by mappingParser#inputMode.
    def enterInputMode(self, ctx:mappingParser.InputModeContext):
        pass

    # Exit a parse tree produced by mappingParser#inputMode.
    def exitInputMode(self, ctx:mappingParser.InputModeContext):
        pass


    # Enter a parse tree produced by mappingParser#modelMode.
    def enterModelMode(self, ctx:mappingParser.ModelModeContext):
        pass

    # Exit a parse tree produced by mappingParser#modelMode.
    def exitModelMode(self, ctx:mappingParser.ModelModeContext):
        pass


    # Enter a parse tree produced by mappingParser#conceptMap.
    def enterConceptMap(self, ctx:mappingParser.ConceptMapContext):
        pass

    # Exit a parse tree produced by mappingParser#conceptMap.
    def exitConceptMap(self, ctx:mappingParser.ConceptMapContext):
        pass


    # Enter a parse tree produced by mappingParser#prefix.
    def enterPrefix(self, ctx:mappingParser.PrefixContext):
        pass

    # Exit a parse tree produced by mappingParser#prefix.
    def exitPrefix(self, ctx:mappingParser.PrefixContext):
        pass


    # Enter a parse tree produced by mappingParser#conceptMappingVar.
    def enterConceptMappingVar(self, ctx:mappingParser.ConceptMappingVarContext):
        pass

    # Exit a parse tree produced by mappingParser#conceptMappingVar.
    def exitConceptMappingVar(self, ctx:mappingParser.ConceptMappingVarContext):
        pass


    # Enter a parse tree produced by mappingParser#conceptMapping.
    def enterConceptMapping(self, ctx:mappingParser.ConceptMappingContext):
        pass

    # Exit a parse tree produced by mappingParser#conceptMapping.
    def exitConceptMapping(self, ctx:mappingParser.ConceptMappingContext):
        pass


    # Enter a parse tree produced by mappingParser#field.
    def enterField(self, ctx:mappingParser.FieldContext):
        pass

    # Exit a parse tree produced by mappingParser#field.
    def exitField(self, ctx:mappingParser.FieldContext):
        pass


    # Enter a parse tree produced by mappingParser#indexerExpression.
    def enterIndexerExpression(self, ctx:mappingParser.IndexerExpressionContext):
        pass

    # Exit a parse tree produced by mappingParser#indexerExpression.
    def exitIndexerExpression(self, ctx:mappingParser.IndexerExpressionContext):
        pass


    # Enter a parse tree produced by mappingParser#polarityExpression.
    def enterPolarityExpression(self, ctx:mappingParser.PolarityExpressionContext):
        pass

    # Exit a parse tree produced by mappingParser#polarityExpression.
    def exitPolarityExpression(self, ctx:mappingParser.PolarityExpressionContext):
        pass


    # Enter a parse tree produced by mappingParser#additiveExpression.
    def enterAdditiveExpression(self, ctx:mappingParser.AdditiveExpressionContext):
        pass

    # Exit a parse tree produced by mappingParser#additiveExpression.
    def exitAdditiveExpression(self, ctx:mappingParser.AdditiveExpressionContext):
        pass


    # Enter a parse tree produced by mappingParser#multiplicativeExpression.
    def enterMultiplicativeExpression(self, ctx:mappingParser.MultiplicativeExpressionContext):
        pass

    # Exit a parse tree produced by mappingParser#multiplicativeExpression.
    def exitMultiplicativeExpression(self, ctx:mappingParser.MultiplicativeExpressionContext):
        pass


    # Enter a parse tree produced by mappingParser#unionExpression.
    def enterUnionExpression(self, ctx:mappingParser.UnionExpressionContext):
        pass

    # Exit a parse tree produced by mappingParser#unionExpression.
    def exitUnionExpression(self, ctx:mappingParser.UnionExpressionContext):
        pass


    # Enter a parse tree produced by mappingParser#orExpression.
    def enterOrExpression(self, ctx:mappingParser.OrExpressionContext):
        pass

    # Exit a parse tree produced by mappingParser#orExpression.
    def exitOrExpression(self, ctx:mappingParser.OrExpressionContext):
        pass


    # Enter a parse tree produced by mappingParser#andExpression.
    def enterAndExpression(self, ctx:mappingParser.AndExpressionContext):
        pass

    # Exit a parse tree produced by mappingParser#andExpression.
    def exitAndExpression(self, ctx:mappingParser.AndExpressionContext):
        pass


    # Enter a parse tree produced by mappingParser#membershipExpression.
    def enterMembershipExpression(self, ctx:mappingParser.MembershipExpressionContext):
        pass

    # Exit a parse tree produced by mappingParser#membershipExpression.
    def exitMembershipExpression(self, ctx:mappingParser.MembershipExpressionContext):
        pass


    # Enter a parse tree produced by mappingParser#inequalityExpression.
    def enterInequalityExpression(self, ctx:mappingParser.InequalityExpressionContext):
        pass

    # Exit a parse tree produced by mappingParser#inequalityExpression.
    def exitInequalityExpression(self, ctx:mappingParser.InequalityExpressionContext):
        pass


    # Enter a parse tree produced by mappingParser#invocationExpression.
    def enterInvocationExpression(self, ctx:mappingParser.InvocationExpressionContext):
        pass

    # Exit a parse tree produced by mappingParser#invocationExpression.
    def exitInvocationExpression(self, ctx:mappingParser.InvocationExpressionContext):
        pass


    # Enter a parse tree produced by mappingParser#equalityExpression.
    def enterEqualityExpression(self, ctx:mappingParser.EqualityExpressionContext):
        pass

    # Exit a parse tree produced by mappingParser#equalityExpression.
    def exitEqualityExpression(self, ctx:mappingParser.EqualityExpressionContext):
        pass


    # Enter a parse tree produced by mappingParser#impliesExpression.
    def enterImpliesExpression(self, ctx:mappingParser.ImpliesExpressionContext):
        pass

    # Exit a parse tree produced by mappingParser#impliesExpression.
    def exitImpliesExpression(self, ctx:mappingParser.ImpliesExpressionContext):
        pass


    # Enter a parse tree produced by mappingParser#termExpression.
    def enterTermExpression(self, ctx:mappingParser.TermExpressionContext):
        pass

    # Exit a parse tree produced by mappingParser#termExpression.
    def exitTermExpression(self, ctx:mappingParser.TermExpressionContext):
        pass


    # Enter a parse tree produced by mappingParser#typeExpression.
    def enterTypeExpression(self, ctx:mappingParser.TypeExpressionContext):
        pass

    # Exit a parse tree produced by mappingParser#typeExpression.
    def exitTypeExpression(self, ctx:mappingParser.TypeExpressionContext):
        pass


    # Enter a parse tree produced by mappingParser#invocationTerm.
    def enterInvocationTerm(self, ctx:mappingParser.InvocationTermContext):
        pass

    # Exit a parse tree produced by mappingParser#invocationTerm.
    def exitInvocationTerm(self, ctx:mappingParser.InvocationTermContext):
        pass


    # Enter a parse tree produced by mappingParser#literalTerm.
    def enterLiteralTerm(self, ctx:mappingParser.LiteralTermContext):
        pass

    # Exit a parse tree produced by mappingParser#literalTerm.
    def exitLiteralTerm(self, ctx:mappingParser.LiteralTermContext):
        pass


    # Enter a parse tree produced by mappingParser#externalConstantTerm.
    def enterExternalConstantTerm(self, ctx:mappingParser.ExternalConstantTermContext):
        pass

    # Exit a parse tree produced by mappingParser#externalConstantTerm.
    def exitExternalConstantTerm(self, ctx:mappingParser.ExternalConstantTermContext):
        pass


    # Enter a parse tree produced by mappingParser#parenthesizedTerm.
    def enterParenthesizedTerm(self, ctx:mappingParser.ParenthesizedTermContext):
        pass

    # Exit a parse tree produced by mappingParser#parenthesizedTerm.
    def exitParenthesizedTerm(self, ctx:mappingParser.ParenthesizedTermContext):
        pass


    # Enter a parse tree produced by mappingParser#nullLiteral.
    def enterNullLiteral(self, ctx:mappingParser.NullLiteralContext):
        pass

    # Exit a parse tree produced by mappingParser#nullLiteral.
    def exitNullLiteral(self, ctx:mappingParser.NullLiteralContext):
        pass


    # Enter a parse tree produced by mappingParser#booleanLiteral.
    def enterBooleanLiteral(self, ctx:mappingParser.BooleanLiteralContext):
        pass

    # Exit a parse tree produced by mappingParser#booleanLiteral.
    def exitBooleanLiteral(self, ctx:mappingParser.BooleanLiteralContext):
        pass


    # Enter a parse tree produced by mappingParser#stringLiteral.
    def enterStringLiteral(self, ctx:mappingParser.StringLiteralContext):
        pass

    # Exit a parse tree produced by mappingParser#stringLiteral.
    def exitStringLiteral(self, ctx:mappingParser.StringLiteralContext):
        pass


    # Enter a parse tree produced by mappingParser#numberLiteral.
    def enterNumberLiteral(self, ctx:mappingParser.NumberLiteralContext):
        pass

    # Exit a parse tree produced by mappingParser#numberLiteral.
    def exitNumberLiteral(self, ctx:mappingParser.NumberLiteralContext):
        pass


    # Enter a parse tree produced by mappingParser#integerLiteral.
    def enterIntegerLiteral(self, ctx:mappingParser.IntegerLiteralContext):
        pass

    # Exit a parse tree produced by mappingParser#integerLiteral.
    def exitIntegerLiteral(self, ctx:mappingParser.IntegerLiteralContext):
        pass


    # Enter a parse tree produced by mappingParser#dateLiteral.
    def enterDateLiteral(self, ctx:mappingParser.DateLiteralContext):
        pass

    # Exit a parse tree produced by mappingParser#dateLiteral.
    def exitDateLiteral(self, ctx:mappingParser.DateLiteralContext):
        pass


    # Enter a parse tree produced by mappingParser#dateTimeLiteral.
    def enterDateTimeLiteral(self, ctx:mappingParser.DateTimeLiteralContext):
        pass

    # Exit a parse tree produced by mappingParser#dateTimeLiteral.
    def exitDateTimeLiteral(self, ctx:mappingParser.DateTimeLiteralContext):
        pass


    # Enter a parse tree produced by mappingParser#timeLiteral.
    def enterTimeLiteral(self, ctx:mappingParser.TimeLiteralContext):
        pass

    # Exit a parse tree produced by mappingParser#timeLiteral.
    def exitTimeLiteral(self, ctx:mappingParser.TimeLiteralContext):
        pass


    # Enter a parse tree produced by mappingParser#quantityLiteral.
    def enterQuantityLiteral(self, ctx:mappingParser.QuantityLiteralContext):
        pass

    # Exit a parse tree produced by mappingParser#quantityLiteral.
    def exitQuantityLiteral(self, ctx:mappingParser.QuantityLiteralContext):
        pass


    # Enter a parse tree produced by mappingParser#externalConstant.
    def enterExternalConstant(self, ctx:mappingParser.ExternalConstantContext):
        pass

    # Exit a parse tree produced by mappingParser#externalConstant.
    def exitExternalConstant(self, ctx:mappingParser.ExternalConstantContext):
        pass


    # Enter a parse tree produced by mappingParser#memberInvocation.
    def enterMemberInvocation(self, ctx:mappingParser.MemberInvocationContext):
        pass

    # Exit a parse tree produced by mappingParser#memberInvocation.
    def exitMemberInvocation(self, ctx:mappingParser.MemberInvocationContext):
        pass


    # Enter a parse tree produced by mappingParser#functionInvocation.
    def enterFunctionInvocation(self, ctx:mappingParser.FunctionInvocationContext):
        pass

    # Exit a parse tree produced by mappingParser#functionInvocation.
    def exitFunctionInvocation(self, ctx:mappingParser.FunctionInvocationContext):
        pass


    # Enter a parse tree produced by mappingParser#thisInvocation.
    def enterThisInvocation(self, ctx:mappingParser.ThisInvocationContext):
        pass

    # Exit a parse tree produced by mappingParser#thisInvocation.
    def exitThisInvocation(self, ctx:mappingParser.ThisInvocationContext):
        pass


    # Enter a parse tree produced by mappingParser#indexInvocation.
    def enterIndexInvocation(self, ctx:mappingParser.IndexInvocationContext):
        pass

    # Exit a parse tree produced by mappingParser#indexInvocation.
    def exitIndexInvocation(self, ctx:mappingParser.IndexInvocationContext):
        pass


    # Enter a parse tree produced by mappingParser#totalInvocation.
    def enterTotalInvocation(self, ctx:mappingParser.TotalInvocationContext):
        pass

    # Exit a parse tree produced by mappingParser#totalInvocation.
    def exitTotalInvocation(self, ctx:mappingParser.TotalInvocationContext):
        pass


    # Enter a parse tree produced by mappingParser#function.
    def enterFunction(self, ctx:mappingParser.FunctionContext):
        pass

    # Exit a parse tree produced by mappingParser#function.
    def exitFunction(self, ctx:mappingParser.FunctionContext):
        pass


    # Enter a parse tree produced by mappingParser#paramList.
    def enterParamList(self, ctx:mappingParser.ParamListContext):
        pass

    # Exit a parse tree produced by mappingParser#paramList.
    def exitParamList(self, ctx:mappingParser.ParamListContext):
        pass


    # Enter a parse tree produced by mappingParser#quantity.
    def enterQuantity(self, ctx:mappingParser.QuantityContext):
        pass

    # Exit a parse tree produced by mappingParser#quantity.
    def exitQuantity(self, ctx:mappingParser.QuantityContext):
        pass


    # Enter a parse tree produced by mappingParser#unit.
    def enterUnit(self, ctx:mappingParser.UnitContext):
        pass

    # Exit a parse tree produced by mappingParser#unit.
    def exitUnit(self, ctx:mappingParser.UnitContext):
        pass


    # Enter a parse tree produced by mappingParser#dateTimePrecision.
    def enterDateTimePrecision(self, ctx:mappingParser.DateTimePrecisionContext):
        pass

    # Exit a parse tree produced by mappingParser#dateTimePrecision.
    def exitDateTimePrecision(self, ctx:mappingParser.DateTimePrecisionContext):
        pass


    # Enter a parse tree produced by mappingParser#pluralDateTimePrecision.
    def enterPluralDateTimePrecision(self, ctx:mappingParser.PluralDateTimePrecisionContext):
        pass

    # Exit a parse tree produced by mappingParser#pluralDateTimePrecision.
    def exitPluralDateTimePrecision(self, ctx:mappingParser.PluralDateTimePrecisionContext):
        pass


    # Enter a parse tree produced by mappingParser#typeSpecifier.
    def enterTypeSpecifier(self, ctx:mappingParser.TypeSpecifierContext):
        pass

    # Exit a parse tree produced by mappingParser#typeSpecifier.
    def exitTypeSpecifier(self, ctx:mappingParser.TypeSpecifierContext):
        pass


    # Enter a parse tree produced by mappingParser#qualifiedIdentifier.
    def enterQualifiedIdentifier(self, ctx:mappingParser.QualifiedIdentifierContext):
        pass

    # Exit a parse tree produced by mappingParser#qualifiedIdentifier.
    def exitQualifiedIdentifier(self, ctx:mappingParser.QualifiedIdentifierContext):
        pass


    # Enter a parse tree produced by mappingParser#identifier.
    def enterIdentifier(self, ctx:mappingParser.IdentifierContext):
        pass

    # Exit a parse tree produced by mappingParser#identifier.
    def exitIdentifier(self, ctx:mappingParser.IdentifierContext):
        pass



del mappingParser