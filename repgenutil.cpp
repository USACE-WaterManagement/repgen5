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

opcode_map opcodes;


void init_opcodes()
{
    opcodes.insert( std::pair< string, eOpcodes>( "pushv", OP_PUSHV ) );
    opcodes.insert( std::pair< string, eOpcodes>( "pushs", OP_PUSHS ) );
    opcodes.insert( std::pair< string, eOpcodes>( "pushd", OP_PUSHD ) );
    opcodes.insert( std::pair< string, eOpcodes>( "pushdi", OP_PUSHDI ) );
    opcodes.insert( std::pair< string, eOpcodes>( "clrv", OP_CLRV ) );
    opcodes.insert( std::pair< string, eOpcodes>( "size", OP_SIZE ) );
    opcodes.insert( std::pair< string, eOpcodes>( "loop", OP_SIZE ) );
    opcodes.insert( std::pair< string, eOpcodes>( "popv", OP_POPV ) );
    opcodes.insert( std::pair< string, eOpcodes>( "popr", OP_POPR ) );
    opcodes.insert( std::pair< string, eOpcodes>( "noop", OP_NOOP ) );
    
    opcodes.insert( std::pair< string, eOpcodes>( "add", OP_ADD ) );
    opcodes.insert( std::pair< string, eOpcodes>( "sub", OP_SUB ) );
    opcodes.insert( std::pair< string, eOpcodes>( "addi", OP_ADDI ) );
    opcodes.insert( std::pair< string, eOpcodes>( "subi", OP_SUBI ) );
    
    
    opcodes.insert( std::pair< string, eOpcodes>( "jmp", OP_JMP ) );
    opcodes.insert( std::pair< string, eOpcodes>( "jmpeq", OP_JMPEQ ) );
    opcodes.insert( std::pair< string, eOpcodes>( "jmpgteq", OP_JMPGTEQ ) );
    opcodes.insert( std::pair< string, eOpcodes>( "jmpgt", OP_JMPGT ) );
    opcodes.insert( std::pair< string, eOpcodes>( "jmpls", OP_JMPLS ) );
    opcodes.insert( std::pair< string, eOpcodes>( "jmplseq", OP_JMPLTEQ ) );
    
        
    
}