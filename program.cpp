/*
    Copyright (c) 2014, <copyright holder> <email>
    All rights reserved.

    Redistribution and use in source and binary forms, with or without
    modification, are permitted provided that the following conditions are met:
        * Redistributions of source code must retain the above copyright
        notice, this list of conditions and the following disclaimer.
        * Redistributions in binary form must reproduce the above copyright
        notice, this list of conditions and the following disclaimer in the
        documentation and/or other materials provided with the distribution.
        * Neither the name of the <organization> nor the
        names of its contributors may be used to endorse or promote products
        derived from this software without specific prior written permission.

    THIS SOFTWARE IS PROVIDED BY <copyright holder> <email> ''AS IS'' AND ANY
    EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
    WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
    DISCLAIMED. IN NO EVENT SHALL <copyright holder> <email> BE LIABLE FOR ANY
    DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES
    (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
    LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND
    ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
    (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
    SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
*/

#include "program.h"
#include "repgenutil.h"
#include "value.h"
#include <cstring>
#include <cmath>
#include <cstdio>
#include <cstdlib>
#include <string>
#include <fstream>
#include <sstream>
#include <utility>
#include <iostream>
#include <bits/algorithmfwd.h>


#include "instruction.h"


using namespace std;

Program::Program( stringstream &stream ){
  string line;
  while( getline( stream, line ) ){
      Instruction inst;
      if( line[0] != '#' ){
	
	size_t first_space  = line.find_first_of( ' ' );
	string code = line.substr( 0, first_space );
	transform(code.begin(), code.end(), code.begin(), ::tolower );
	cout << "Finding opCode for '" << code << '\'' << endl;
	inst.opcode = opcodes.at(code);
	
	inst.value = line.substr( first_space+1, line.size() );
	
	cout << "Adding (" << inst.opcode << " " << inst.value << ")" << endl;
	program.push_back( inst );
	
      }else{
	  cout << "Found a NOOP" << endl;
	  inst.opcode = OP_NOOP;
	  program.push_back( inst );
      }
  }
  
}
  
void Program::run( data_map &data ){
  
  // start everything at zero
  program_counter = 0;
  register_index = 0; // loop index
  int compare = 0; // 0 eq, -1 less, 1 greater
  
  Instruction instr;
  Value result;		     //tmp value for all of the indexed results
  result.picture = "NNNNNZ";
  result.type = DOUBLE_VAL;
  
  while( program_counter < program.size() ){
    instr = program[program_counter];
      
    stack<Value> tmp = stack_values; // this should be a copyright
    cout << "\tValues on the stack:" << tmp.size() << endl;
    cout << "\tregister index     :" << register_index << endl;
    cout << "\tprogram  counter   :" << program_counter << endl;
    cout << "\tcompare register   :" << compare << endl;
    cout << "\tcurrent instruction:" << instr.opcode << "/" << endl;
    /* set missing picture etc from setting */
      
    switch( instr.opcode ){                 
      case OP_PUSHD:{
	   cout << "pushing a scalar double value " << instr.value << endl;
	   Value val( "NNNNNZ", "", "", DOUBLE_VAL );
	   val.scalar = true;
	   val.double_value.push_back( atof( instr.value.c_str() ) );
	   stack_values.push( val );
	   program_counter++;
	  break;	
      }
      case OP_PUSHDI:{
	  cout << "pushing value to index " << register_index << endl;
	  double v = atof( instr.value.c_str() );
	  cout << "\t pushing value" << v << endl;
	  result.double_value[register_index] = v;
	  program_counter++;
	  break;
      }
      case OP_PUSHV:{
	  cerr << "pushing named var " << instr.value << " onto var stack"<<endl;
	  Value val = data.at(instr.value );	  
	  stack_values.push( val );
	  program_counter++;
	  break;
      }
      case OP_POPV:{
	  cout << "popping value into named variable " << instr.value << endl;	  
	  Value val = stack_values.top();
	  stack_values.pop();
	  data[ instr.value ] = val;	  
	  program_counter++;
	  break;
      }
      case OP_POPR:{
	  cout << "popping result value into named variable " << instr.value << endl;	  
	  data[ instr.value ] = result;
	  result.double_value.clear();
	  program_counter++;
	  break;
      }      
      case OP_SIZE:{
	  cout << "figuring out loop counter" << endl;
	  bool all_scalar = true;	  
	  while( !tmp.empty() ){
	      Value v = tmp.top();	      
	      if( !v.scalar ){
		  all_scalar = false;
		  if( register_index != 0 ){
		      register_index = v.double_value.size();
		  } else{
		      if( register_index != v.double_value.size() ){
			  cerr << "\tCannot run math on series of two different lengths" << endl;
			  exit(1);
		      }
		  }	
	      } 	      
	      cout << "\ttmp size: " << tmp.size() << endl;
	      tmp.pop();	      	  	      
	  }
	  if( all_scalar ){
	      result.scalar = true;
	      register_index = 0; //only loop once
	  }
	  result.double_value.reserve(register_index); // we'll need this many elements
	  cout << "\tlooping " << register_index << " time(s)" << endl;
	  program_counter++;
	  break;
      }
      case OP_ADD:{	  
	  result.double_value.clear();
	  cout << "adding values" << endl;
	  Value op1 = stack_values.top();
	  stack_values.pop();
	  Value op2 = stack_values.top();
	  stack_values.pop();
	  
	  /*
	   *  check for scalar and size
	   */
	  if( op1.scalar && op2.scalar ){	      	      
	      result.double_value.push_back( op1.get_double_val(0) + op2.get_double_val(0) );	      
	      result.scalar = true;
	  } else {
	      cerr << "\tCannot run calculation on these disimilar types" << endl;
	      exit(1);
	  }
	  
	  stack_values.push( result );	  	  
	
	  cout << "\tCalculated value: " << result.double_value[0] << endl;
	  program_counter++;
	  break;
      }
      case OP_SUB:{	
	  result.double_value.clear();
	  cout << "substracting values" << endl;
	  Value op1 = stack_values.top();
	  stack_values.pop();
	  Value op2 = stack_values.top();
	  stack_values.pop();
	  
	  if( op1.scalar && op2.scalar ){
	      result.double_value.push_back( op1.get_double_val(0) - op2.get_double_val(0) );
	      result.scalar = true;
	  } else{
	      cerr << "\tCannot run calculations these disimilar types yet" << endl;
	  }
	  
	  stack_values.push( result );
	  program_counter++;
	  
	  break;
      }                
      case OP_SUBI:{
	  cout << "subtracting values at index " << register_index << endl;
	  Value op1 = stack_values.top();
	  stack_values.pop();
	  Value op2 = stack_values.top();
	  stack_values.pop();
	  
	  // size will have been run before this, so we shouldn't have to worry about figuring out if we need to bail here
	  double v = op1.get_double_val(register_index) - op2.get_double_val(register_index);
	  //set the compare bit
	  
	  cout << "\tset compare bit" << endl;
	  
	  if( v == 0 ){
	      compare = 0;
	  } else if( v > 0 ){
	      compare = 1;
	  } else {
	      compare = -1;
	  }
	  result.double_value[register_index] = v;
	  
	  
	  program_counter++;
	  break;
      }
      
      case OP_JMP:{
	  cout << "Jumping with no conditions" << endl;
	  program_counter += atoi( instr.value.c_str() );
	  break;
      }
      case OP_JMPGT:{
	  cout << "Jumping if greater" << endl;
	  if( compare > 0 ){
	      program_counter += atoi( instr.value.c_str() );
	  }
	  break;
      }
      
      case OP_NOOP:{
	  cout << "No OP" << endl;
	  program_counter++;
	  break;
      }
      
      default:{
	  cout << "Unknown opcode " << instr.opcode << endl;;
	  program_counter++;
	  break;
      }
      
      
    }
    
  }
  
}

