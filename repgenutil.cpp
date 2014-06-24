#include "repgenutil.h"
#include <cstring>



string rg_strftime(char* format, const tm* time)
{
  char *result;
  int size = strlen(format)*3; // probably overkill
  result = new char[size];
  int result_size = strftime(result, size, format, time  );
  string str( result );
  return str;
  
}
