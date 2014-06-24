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


#include "queue.h"

void Queue::push(Value& v)
{
  values.push_back(v); // put the item in the back of the queue
}

Value Queue::pop()
{
  if( is_scalar ){
    return *values.begin(); // if we're a scalar value we always just return the first one in the list
  } else {
    Value v = values.front();
    values.pop_front();
    return v;
  }
}

Value Queue::get(int i)
{
  if( is_scalar ) {
      return *values.begin(); // there's only the one, this makes the calculator math easier
  }
  size_t index = 0;
  list<Value>::iterator ind = values.begin();
  while( index != i ){
    ind++;
    i++;
  }
  return *ind;
}

void Queue::set_picture(char* picture)
{
  this->picture = picture;
  
}

void Queue::set_picture(string& picture)
{
  this->picture = picture;
}

string Queue::get_picture(){
    return this->picture;
}


