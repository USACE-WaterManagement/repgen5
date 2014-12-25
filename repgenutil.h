#ifndef _REPGENUTIL_H_
#define _REPGENUTIL_H_
#include <string>
#include <time.h>
#include <map>
#include "value.h"
using namespace std;


typedef enum {
    // basic operations
    OP_PUSHV , // push a named var until the var stack
    OP_POPV  ,  // pop a stack var into the named var
    OP_POPR  ,  // pop result onto the stack
    OP_CLRV  ,  // clear the var stack
    OP_PUSHD , // push a double onto the var stack
    OP_PUSHDI, // push value at index
    OP_PUSHS , // push a string onto the var stack
    OP_SIZE  ,  // go over all the var on the var stack and set the size, 
              // if there are two non scalars they should match in size, and the times should line up, but we only really need to check the first two   
    OP_LOOP  ,  // 
    OP_NOOP  ,
    
    // basic math operations
    
    OP_LOADV, // load a variable from parameters on the stack (must have a type)
    OP_ADD,   // add the top two values from the stack, looping over all values if needed
    OP_ADDI,  // add the two values at the index counter
    OP_SUB,
    OP_SUBI,
    OP_MUL,
    OP_MULI,
    OP_DIV,
    OP_DIVI,
    
    // conditionals
    OP_JMP,
    OP_JMPEQ,
    OP_JMPLS,
    OP_JMPGT,
    OP_JMPGTEQ,
    OP_JMPLTEQ,
    
  
} eOpcodes;





typedef map< string, Value, std::greater<string> >     data_map;
typedef map< string, eOpcodes, std::greater<string> >     opcode_map;

string rg_strftime( char *format, const tm *time );


extern opcode_map opcodes;
void init_opcodes();



#endif