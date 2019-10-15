YACC=bison -b y
LEX=flex
VER=`cat VERSION`
CC= gcc

asparser : lex.yy.c y.tab.c asparser.c
	$(CC) -o asparser lex.yy.c y.tab.c asparser.c

y.tab.c : parser.y
	$(YACC) -d -v parser.y
	
lex.yy.c : scanner.l
	$(LEX) scanner.l	