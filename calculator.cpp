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


#include "calculator.h"
#include <sstream>
#include <cstring>
#include <cstdlib>
#include <string>
#include <map>
#include <cmath>




Calculator::Calculator(string& equation, map< string, Queue, std::greater<string> > *data)
{
  
  operators['+'] = operator_def( true,2 );
  operators['-'] = operator_def( true,2 );
  operators['/'] = operator_def( true, 3 );
  operators['*'] = operator_def( true, 3 );
  operators['^'] = operator_def( false, 4 );
  /*{'+', true,  2},
  {'-', true,  2},
  {'/', true,  3},
  {'*', true,  3},
  {'^', false, 4}  */

  
  
  this->data = data;  
  stack<Token> operator_stack; // The temporary stack of operators
  this->scalar_result = true;
  string::iterator it = equation.begin();
  while( it != equation.end() ){
    Token tok; // our new token    
    //memset(&tok,0, sizeof( tok ) );
    stringstream tmp(""); // for processing string, functions and 
    tmp.clear();
    if( *it == '%' ){
	// process variable token
	/* lookup variable, if not scalar, scalar_result = false
	 */	
    }
    else if( *it == '"' ){
	// process string token
    }
    else if( ::isdigit(*it) ){
       // process scalar token
       tok.type = TYPE_SCALAR;
       while( ::isdigit(*it) || *it == '.' ){
	  tmp << *it;
	  it++;
       }
       tmp >> tok.value;
       eq.push_back( tok );
    }else if( isalpha(*it) ){
      
      // we have a function which must have a ( open it
      tok.type = TYPE_FUNCTION;
      while( *it != '('){
	tmp << *it;
	it++;
      }
      tok .str = tmp.str();
      operator_stack.push( tok );
    }
    else{
	// process as other type of token
	
	tok.op = *it;
	tok.type = TYPE_OP;
	if( *it == '(' ){
	  operator_stack.push( tok );
	  
	} else if( *it == ')'){
	  Token tmp = operator_stack.top();
	  operator_stack.pop();
	  while( tmp.op != '(' ){	    
	    
	    eq.push_back( tmp );
	    tmp = operator_stack.top();
	    operator_stack.pop();
	  }
	}else{
	  
	  
	  
	  if( !operator_stack.empty() ){
	    char prev_op = operator_stack.top().op;
	    if( prev_op != '(' ){
	      while( !operator_stack.empty() && 
		    ( ( (operators[*it].left==true) && operators[*it].precedence <= operators[prev_op].precedence ) ) ||
		    ( operators[*it].precedence < operators[prev_op].precedence )     
	      ){
		  eq.push_back( operator_stack.top() );
		  operator_stack.pop();
	      }
	      operator_stack.push( tok );
	    }else{
	      operator_stack.push( tok );
	    }
	  } else{
	    operator_stack.push( tok );
	  }
	  
	}
	
	it++;
    }
    
    
  }
  
  while( !operator_stack.empty() ){
    Token tmp = operator_stack.top();
    operator_stack.pop();
    eq.push_back(tmp);
  }

}


void Calculator::process(Queue& newqueue)
{
  // for now just do the simple scalar version
  // later we need to add a for loop for the non-scalar values
  newqueue.set_scalar( this->scalar_result );
  list<Token>::iterator token = eq.begin(); // we don't want to destroy the stack
  stack<double> value_stack;
  double op1;
  double op2;
  double result;
  while( token != eq.end() ){
    switch( token->type ){
	  case TYPE_SCALAR:{
	    value_stack.push( token->value );
	    
	    break;
	  }
	  case TYPE_VAR:{
	    // TODO: get variable value and push unto stack
	    break;
	  }
	  case TYPE_FUNCTION:{
	    // process function
	    if( token->str == "cos"){
	      op1 = value_stack.top();
	      value_stack.pop();
	      value_stack.push( cos( op1 ) );
	    } else if( token->str == "sin" ){
	      op1 = value_stack.top();
	      value_stack.pop();
	      value_stack.push( sin( op1 ) );
	    } else if( token->str == "tan" ){
	      op1 = value_stack.top();
	      value_stack.pop();
	      value_stack.push( tan( op1 ) );
	    }
	    break;
	  }
	  case TYPE_OP:{
	      switch( token->op ){
		case '+':		
		    op2 = value_stack.top();
		    value_stack.pop();
		    op1 = value_stack.top();
		    value_stack.pop();
		    value_stack.push( op1 + op2 );
		  break;
		case '-':
		    op2 = value_stack.top();
		    value_stack.pop();
		    op1 = value_stack.top();
		    value_stack.pop();
		    value_stack.push( op1 - op2 );
		  break;
		case '*':
		    op2 = value_stack.top();
		    value_stack.pop();
		    op1 = value_stack.top();
		    value_stack.pop();
		    value_stack.push( op1 * op2 );
		  break;
		case '/':
		    op2 = value_stack.top();
		    value_stack.pop();
		    op1 = value_stack.top();
		    value_stack.pop();
		    value_stack.push( op1 / op2 );
		  break;
		case '^':
		    op2 = value_stack.top();
		    value_stack.pop();
		    op1 = value_stack.top();
		    value_stack.pop();
		    value_stack.push( pow( op1, op2 ) );
		  break;
	      }
	      
	  }
	  
      }
      token++; // move on to the next token
    }
    
  
  Value val( value_stack.top() );
  newqueue.push( val );
  
}
