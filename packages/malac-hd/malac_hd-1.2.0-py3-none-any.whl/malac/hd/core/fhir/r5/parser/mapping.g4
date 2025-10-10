/**
 * Define a grammar called FhirMapper
 */
 grammar mapping;
 import fhirpath;

// starting point for parsing a mapping file
// in case we need nested ConceptMaps, we need to have this rule:
// structureMap : mapId conceptMap* structure* imports* group+

structureMap
    : mapId conceptMap* structure* imports* const* group+ EOF
    ;

mapId
	: 'map' url '=' quoteidentifier
	;

url
    : DELIMITEDIDENTIFIER
    | QUOTEIDENTIFIER
    ;

quoteidentifier
    : IDENTIFIER
    | DELIMITEDIDENTIFIER
    | QUOTEIDENTIFIER
    ;

mapidentifier
    : IDENTIFIER
    | DELIMITEDIDENTIFIER
    | 'div'
    ;

structure
	: 'uses' url structureAlias? 'as'  modelMode
	;

structureAlias
    : 'alias' mapidentifier
    ;

imports
	: 'imports' url
	;

const 
    : 'let' IDENTIFIER '=' fhirPath ';' // which might just be a literal
    ;

group
	: 'group' IDENTIFIER parameters extends? typeMode? rules
	;

rules
    : '{' rule* '}'
    ;

typeMode
    : '<<' groupTypeMode '>>'
    ;

extends
    : 'extends' IDENTIFIER
    ;

parameters
    : '(' parameter (',' parameter)+ ')'
    ;

parameter
    : inputMode IDENTIFIER type?
	;

type
    : ':' mapidentifier
    ;

rule
 	: ruleSources ('->' ruleTargets)? dependent? ruleName? ';'
 	;

ruleName
    : QUOTEIDENTIFIER
    ;

ruleSources
    : ruleSource (',' ruleSource)*
    ;

ruleSource
    :  ruleContext sourceType? sourceCardinality? sourceDefault? sourceListMode? alias? whereClause? checkClause? log?
    ;

ruleTargets
    : ruleTarget (',' ruleTarget)*
    ;

sourceType
    : ':' mapidentifier
    ;

sourceCardinality
    : INTEGER '..' upperBound
    ;

upperBound
    : INTEGER
    | '*'
    ;

ruleContext
	: mapidentifier ('.' mapidentifier)*
	;

sourceDefault
    : 'default' '(' fhirPath ')'
    ;

alias
	: 'as' mapidentifier
	;

whereClause
    : 'where' '(' fhirPath ')'
    ;

checkClause
    : 'check' '(' fhirPath ')'
    ;

log
    : 'log' '(' fhirPath ')'
    ;

dependent
    : 'then' (mapinvocation (',' mapinvocation)* rules? | rules)
    ;

ruleTarget
    : ruleContext ('=' transform)? alias? targetListMode?
    | mapinvocation alias?     // alias is not required when simply invoking a group
    ;

transform
    : mapliteral           // trivial constant transform
    | ruleContext       // 'copy' transform
    | mapinvocation        // other named transforms
    | evaluate     // evaluate
    ;

evaluate
    : '(' fhirPath ')'
    ;

mapinvocation
    : mapidentifier '(' mapparamList? ')'
    ;

mapparamList
    : param (',' param)*
    ;

param
    : mapliteral
    | IDENTIFIER
    ;

fhirPath
    : mapliteral       // insert reference to FhirPath grammar here
    | expression
    ;

mapliteral
    : INTEGER
    | NUMBER
    | STRING
    | DATETIME
    | DATE
    | TIME
    | BOOL
    ;

groupTypeMode
    : 'types' | 'type+'
    ;

sourceListMode
    : 'first' | 'not_first' | 'last' | 'not_last' | 'only_one'
    ;

targetListMode
   : 'first' | 'share' | 'last' | 'single'
   ;

inputMode
   : 'source' | 'target'
   ;

modelMode           // StructureMapModelMode binding
    : 'source' | 'queried' | 'target' | 'produced'
    ;




conceptMap
    : ('conceptMap'|'conceptmap') quoteidentifier '{' (prefix)+ conceptMapping+ '}'
    ;

prefix
    : 'prefix' conceptMappingVar '=' url
    ;

conceptMappingVar
    :  IDENTIFIER
    ;

conceptMapping
    :  conceptMappingVar ':' field
        (('-' | '<=' | '=' | '==' | '!=' '>=' '>-' | '<-' | '~') conceptMappingVar ':' field) | '--'
    ;

field
    :  IDENTIFIER
    |  QUOTEIDENTIFIER
    ;



/****************************************************************
    Lexical rules from FhirPath
*****************************************************************/

BOOL
        : 'true'
        | 'false'
        ;

DATE
        : '@' DATEFORMAT
        ;

DATETIME
        : '@' DATEFORMAT 'T' (TIMEFORMAT TIMEZONEOFFSETFORMAT?)?
        ;

TIME
        : '@' 'T' TIMEFORMAT
        ;

fragment DATEFORMAT
        : [0-9][0-9][0-9][0-9] ('-'[0-9][0-9] ('-'[0-9][0-9])?)?
        ;

fragment TIMEFORMAT
        : [0-9][0-9] (':'[0-9][0-9] (':'[0-9][0-9] ('.'[0-9]+)?)?)?
        ;

fragment TIMEZONEOFFSETFORMAT
        : ('Z' | ('+' | '-') [0-9][0-9]':'[0-9][0-9])
        ;

IDENTIFIER
        : ([A-Za-z] | '_')([A-Za-z0-9] | '_')*            // Added _ to support CQL (FHIR could constrain it out)
        ;

QUOTEIDENTIFIER
        : '"' (ESC | .)*? '"'
        ;

DELIMITEDIDENTIFIER
        : '`' (ESC | .)*? '`'
        ;

STRING
        : '\'' (ESC | .)*? '\''
        ;

INTEGER
    : [0-9]+
    ;

// Also allows leading zeroes now (just like CQL and XSD)
NUMBER
    : INTEGER ('.' [0-9]+)?
    ;

// Pipe whitespace to the HIDDEN channel to support retrieving source text through the parser.
WS
    : [ \r\n\t]+ -> channel(HIDDEN)
    ;

COMMENT
        : '/*' .*? '*/' -> channel(HIDDEN)
        ;

LINE_COMMENT
        : '//' ~[\r\n]* -> channel(HIDDEN)
        ;

fragment ESC
        : '\\' (["'\\/fnrt] | UNICODE)    // allow \", \', \\, \/, \f, etc. and \uXXX
        ;

fragment UNICODE
        : 'u' HEX HEX HEX HEX
        ;

fragment HEX
        : [0-9a-fA-F]
        ;
