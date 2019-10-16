#include <stdio.h>
#include <stdlib.h>
#include <stdarg.h>
#include <string.h>
#include "asparser.h"
int yyparse();

unsigned int yyline=1;
char *defAttrType;
char *defRuleType;
char goalEnabled=0;

char *strCat(const char *first, ... ) {
  va_list ap;
  char *s, *new;
  int size=0;
  va_start(ap, first);
  for (s=(char *)first; s!=NULL; s=va_arg(ap, char *) ) 
    size += strlen(s);
  va_end(ap);
  
  new=(char *)malloc(size+1);  new[0]='\0';
  va_start(ap, first);
  for (s=(char *)first; s!=NULL; s=va_arg(ap, char *) ) 
    strcat(new,s);
  va_end(ap);
  
  return new;
}

char *strCopy(char *s)
{
  int size;
  char *t;
  
  size=strlen(s)+1;
  if( (t=(char *)malloc(sizeof(char)*size)) == NULL)
  {
    printf("NULL malloc: cloning string %s\n",s);
    exit(0);
  }
  memcpy(t,s,size);
  return t;
}

char *strAppend(char *s,char *t)
{
  char *r=(char *)malloc(strlen(s)+strlen(t)+1);
  sprintf(r,"%s%s",s,t);
  free(s);
  return r;
}


int main() {
  yyparse();
}
