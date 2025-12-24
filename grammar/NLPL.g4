grammar NLPL;

// Parser Rules
program: statement* EOF;

statement
    : variableDeclaration
    | functionDefinition
    | ifStatement
    | whileStatement
    | forStatement
    | returnStatement
    | expressionStatement
    | memoryStatement
    ;

variableDeclaration
    : SET IDENTIFIER type? '=' expression
    ;

functionDefinition
    : FUNCTION IDENTIFIER '(' parameterList? ')' ('->' type)? block
    ;

parameterList
    : parameter (',' parameter)*
    ;

parameter
    : IDENTIFIER type?
    ;

type
    : IDENTIFIER
    ;

block
    : '{' statement* '}'
    ;

ifStatement
    : IF expression block (ELSE block)?
    ;

whileStatement
    : WHILE expression block
    ;

forStatement
    : FOR IDENTIFIER IN expression block
    ;

returnStatement
    : RETURN expression?
    ;

expressionStatement
    : expression
    ;

memoryStatement
    : ALLOCATE IDENTIFIER type?
    | DEALLOCATE IDENTIFIER
    ;

expression
    : primary
    | expression '.' IDENTIFIER                      // Member access
    | expression '(' argumentList? ')'               // Function call
    | expression '[' expression ']'                  // Index access
    | expression operator=('+' | '-' | '*' | '/') expression
    | expression operator=('==' | '!=' | '<' | '>' | '<=' | '>=') expression
    | expression operator=('and' | 'or') expression
    | 'not' expression
    ;

primary
    : IDENTIFIER
    | INTEGER
    | FLOAT
    | STRING
    | BOOLEAN
    | NULL
    | '(' expression ')'
    ;

argumentList
    : expression (',' expression)*
    ;

// Lexer Rules
SET: 'set';
FUNCTION: 'function';
IF: 'if';
ELSE: 'else';
WHILE: 'while';
FOR: 'for';
IN: 'in';
RETURN: 'return';
ALLOCATE: 'allocate';
DEALLOCATE: 'deallocate';
NULL: 'null';
BOOLEAN: 'true' | 'false';

IDENTIFIER: [a-zA-Z_][a-zA-Z0-9_]*;
INTEGER: [0-9]+;
FLOAT: [0-9]+ '.' [0-9]+;
STRING: '"' (~["\r\n] | '\\"')* '"';

WS: [ \t\r\n]+ -> skip;
COMMENT: '#' ~[\r\n]* -> skip; 