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


#include "value.h"
#include "mildatetime.h"
#include <sstream>
#include <iostream>
#include <limits>
using namespace std;



string Value::get_value_formatted(const string& picture, uint8 type)
{
	switch(type){
		case DOUBLE_VAL:{
		      stringstream stream;
		      stream.width( picture.size() );
		      // we should scan the picture to figure out how many decimal places to present
		      stream.precision(3);
		      stream.fill( '0' );      
		      stream << this->value;
		      /*
		       * Check for missing
		       */
		      cout << "Line is '" << stream.str() << "'" << endl;
		      string raw = stream.str();
		      string result;
		      string::iterator strm = raw.begin();
		      string::iterator pic  = picture.begin();

		      bool at_first_sig_fig = false;
		      for( pic; pic != picture.end(); pic++, strm++ ){
			  if( *strm > '0' ){ at_first_sig_fig = true; }
			  if( *strm == '0' && *pic == 'N' && !at_first_sig_fig ){
			      result += ' ';
			  }else{
			      result += *strm;
			  }
			  
			  
		      }
		      /*
		      if( strm != raw.end() )
		      {
			  string over;
			  over.insert(0, picture.size(), '*' );
			  return over;
		      }
		      */
		      
		      return result;
		}
		case STRING_VAL:{
				return "string";
		}
		case TIME_VAL:{			
		      /*
		       * Picture                    Display
		       * DDbAAAbYYYY                4 JUL 1987
			  ZDbAAAbYYYY               04 JUL 1987
			  MM/DD                     7/4
			  MM/DD/YYbbHH              7/4/87 8
			  ZM/ZD/YYbbHH              07/04/87 08
			  DDbAAAbYY                 4 JUL 87
			  ZDbAAAbYY                 04 JUL 87
			  AAAbDD,bYYYY              JUL 4, 1987
			  AAAAAAAAAbDD,bYYYY        JULY 4, 1987
			  ZZZT                      0830
			  ZZ:ZT                     08:30
			  ZT                        30
			  TZ:ZT                     8:30
			  HH                        8
			  ZH                        08
			  AAAAAAAAAbDD,bYYYYb@bZZZT JULY 4, 1987 @ 0830

			  loop through the picture
			  if we find a z increase a counter for a number to zero fill
			  So those are the pictures, and the results that should happen from it
			  if we find a format character, process and output it.
			  if the next character is the same as the previous, ignore unless it's A, then we count and cut of
		       */
		      // build a date 
		      time_t time = this->time;
		      tm *mytime = gmtime( &time );
		      string result;
		      stringstream stream;
		      int zeropad = 0;
		      string::iterator token = picture.begin();
		      char previous = 0;
		      while( token != picture.end() ){
			stream.str("");
			stream.clear();
			//cout << "STREAM: " <<  stream.str() << endl;;
			//cout << *token << endl;
			previous = *token; // make it easier to copy paste code
			
			switch( *token ){
			  case 'Z':
			      while( *token == previous ){
				zeropad++;
				token++;
			      }
			      break;
			  case 'D':	      	      
			      while( *token == previous ){
				 token++;
			      }
			      if( zeropad > 0 ){
				stream.fill('0');
				stream.width(zeropad+1); // the Zs plus the D character
				zeropad = 0;
			      }	      
			      stream << mytime->tm_mday;	      
			      result += stream.str();
			      // process day	      
			      break;
			  case 'M':
			      while( *token == previous ){
				 token++;
			      }
			      if( zeropad > 0 ){
				stream.fill('0');
				stream.width(zeropad+1); // the Zs plus the D character
				zeropad = 0;
			      }	      
			      stream << mytime->tm_mon+1;	      
			      result += stream.str();
			      // process month (as digit)
			      break;
			  case 'Y':
			      while( *token == previous ){
				 token++;
			      }
			      if( zeropad > 0 ){
				stream.fill('0');
				stream.width(zeropad+1); // the Zs plus the D character
				zeropad = 0;
			      }
			      stream << mytime->tm_year + 1900; 
			      result += stream.str();
			      // process year
			      break;
			  case 'H':
			      while( *token == previous ){
				 token++;
			      }
			      if( zeropad > 0 ){
				stream.fill('0');
				stream.width(zeropad+1); // the Zs plus the D character
				zeropad = 0;
			      }
			      stream << mytime->tm_hour; 
			      result += stream.str();
			      // process hour
			      break;	      	  
			  case 'A':
			  {
			      string month( month_long[mytime->tm_mon] );
			      string::iterator m = month.begin();
			      while( *token == previous ){
				if( m != month.end() ){
				  result += *m;
				  m++;
				}
				
				token++;
			      }
			      
			      
			      // process month (as string )	     
			      break;
			  }
			  case 'T':
			      while( *token == previous ){
				 token++;
			      }
			      if( zeropad > 0 ){
				stream.fill('0');
				stream.width(zeropad+1); // the Zs plus the D character
				zeropad = 0;
			      }	 
			      {
				int t = mytime->tm_hour*100 + mytime->tm_min;
				stream << t; 
				result += stream.str();
			      }
			      // process time ( as full hours,minute )
			      break;
			  case 'b':
			  case 'B':	// these all get repeated as present     
			      token++;
			      // add a space
			      result += ' ';
			      break;
			  default:	      
			      result += *token; // if we don't know what it is just add it
			      token++;
			      break;
			}
	
		      }
		      cout << endl;
		      
		      cout << "--" << result << "--" << endl;
		      return result;
		    }
}


time_t Value::get_time(  ){
 	return this->time; 
}

		
double Value::get_value(  ){
	return this->value;
}



