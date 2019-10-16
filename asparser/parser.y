%{
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include "asparser.h"

extern int yylex(void);

extern int yyrestart(FILE *);
int yyerror (char *s)  /* Called by yyparse on error */
{
  fprintf (stderr,"%d: %s after `%s'\n", yyline, s, yytext);
  return 1;
}

char **atoms;
char **values;
int counter = -1;

char *current;
char *last;

/* Used to print (in a json-like way) the atoms stored up to that moment */
char* printAtoms(){
  char *string = "";
  int i;
  for (i=0; i <= counter; i++){
    if (i < counter)
      string=strCat(string, "\"", atoms[i], "\" : [", values[i], "],", NULL);
    else
      string=strCat(string, "\"", atoms[i], "\" : [", values[i], "]", NULL);
  };
  return string;
}

%}

%union {
  char  	*strval; /* For returning a string */
}

%token HEADER
%token ANSWER     /* 'answer:' header token */

%token OPTIMUMFOUND
%token SATISFIABLE
%token UNSATISFIABLE

%token  NUMBER     /* integer   */
%token  ID         /* identifier */
%token  STRING     /* string literal */
%token  SECONDS
%token  FILENAME

/* STATS TOKENS */
%token STATNAME
%token STAT_TIME_SOLVING
%token STAT_TIME_FIRST_MODEL
%token STAT_TIME_UNSAT


%type <strval> output
%type <strval> answerset_list

%type <strval> answerset
%type <strval> answer_header
%type <strval> atoms

%type <strval> fterm
%type <strval> termlist
%type <strval> term
%type <strval> statname

%type <strval> id
%type <strval> num
%type <strval> string
%type <strval> seconds


/* Grammar follows */
%%


output:
    output_header answerset_list stat_list              {exit(0);}
  | output_header answerset_list SATISFIABLE stat_list  {exit(0);}
  | output_header UNSATISFIABLE stat_list               {exit(0);}
  ;

answerset_list:
    answerset                 {printf("%s\n",$1);}
  | answerset_list answerset  {printf("%s\n",$2);}
  ;

output_header:
    HEADER
  ;


answerset :
    answer_header atoms OPTIMUMFOUND  {$$=strCat("{ \"solnum\":", $1, ",\"optimum\" : \"yes\", \"atoms\" :{", printAtoms(), "}}", NULL);}
  | answer_header atoms               {$$=strCat("{ \"solnum\":", $1, ",\"atoms\" :{", printAtoms(), "}}", NULL);}
  ;

answer_header:
    ANSWER num  {$$=$2; counter=-1; last=strCat("X",NULL); current=strCat("",NULL);}
  ;


/*
 * 'atoms' and 'values' store all the atoms and its values for the solution.
 * Example; for the following solution:
      rectinliercount(1,54) rectinliercount(2,9) outliercount(68) overlapcount(5)
 * The content would be:
      atoms[0]="rectinliercount" atoms[1]="outliercount" atoms[2]="overlapcount"
      values[0]="[[1,54],[2,9]]" values[1]="[[68]]"      values[2]="[[5]]" 
 *
 * asparser takes advantage of the fact that clingo (and asprin) print the atoms of each
 * solution in an ordered way. So it uses two variables ('current' and 'last') and a 'counter'
 * to manage 'atoms' and 'values' arrays correctly.
*/
atoms:
    fterm       { if (strcmp(last, current) != 0){ // Change atom
                    counter++;
                    
                    atoms = realloc(atoms, (counter+1) * sizeof(char*));
                    atoms[counter]=strCat(current,NULL);

                    values = realloc(values, (counter+1) * sizeof(char*));
                    values[counter]=strCat($1,NULL);
                  } else {                         // Same atom
                    
                    values = realloc(values, (counter+1) * sizeof(char*));
                    values[counter]=strCat(values[counter],",",$1,NULL);
                  }

                  last=strCat(current,NULL);
                }
  | atoms fterm { if (strcmp(last, current) != 0){ // Change atom
                    counter++;
                    
                    atoms = realloc(atoms, (counter+1) * sizeof(char*));
                    atoms[counter]=strCat(current,NULL);

                    values = realloc(values, (counter+1) * sizeof(char*));
                    values[counter]=strCat($2,NULL);
                  } else {                         // Same atom
                    
                    values = realloc(values, (counter+1) * sizeof(char*));
                    values[counter]=strCat(values[counter],",",$2,NULL);
                  }

                  last=strCat(current,NULL);
                }
  ;



fterm :
    id                  { current=$1; $$="[]"; }
  | id '(' termlist ')'	{ current=$1; $$=strCat("[", $3, "]", NULL); }
  ;
  
termlist :
    term              {$$=strCat($1,NULL);}
  | termlist ',' term {$$=strCat($1,",",$3,NULL);}
  ;

term :
    id      {$$=$1;}
  | num     {$$=$1;}
  | string  {$$=strCat("'",$1,"'",NULL);}
  ;



stat_list:
    stat    
  | stat_list stat
  ;

stat:
    statname ':' seconds '(' stat_list ')'
  | statname ':' num '+' /* Model counter */
  | statname ':' seconds 
  | statname ':' num
  | statname ':' id     /* (asprin) Optimum : yes/no */
  | STAT_TIME_FIRST_MODEL ':' seconds  /* For now: is an exception */
  ;




statname:
    STATNAME          { $$=yylval.strval; }
  | statname STATNAME { $$=strCat($1, " ", yylval.strval, NULL);}
  ;

seconds:
    SECONDS { $$=yylval.strval;}
  ;

id : 
    ID 		{ $$=yylval.strval; }
  ;

num : 
    NUMBER 		{ $$=yylval.strval; }
  ;

string:
    STRING {$$=yylval.strval;}
  ;


/* End of grammar */
%%
