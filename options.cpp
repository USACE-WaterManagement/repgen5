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


#include "options.h"
#include <unistd.h>
#include <getopt.h>
#include <time.h>
#include "repgenutil.h"

Options::Options(int argc, char** argv)
{
  // parse the options
  report = "report";
  input = "";
  time_t rawtime;
  time( &rawtime );
  tm *_time = localtime( &rawtime );
  
  // default to the current time  
  
  startdate = rg_strftime( "%d%b%Y", _time); 
  starttime = rg_strftime( "%H%M", _time );
  
  static struct option long_options[] = {
        {"in",      required_argument,   0,  'i' },
	{"input",   required_argument,   0,  'i' },
        {"report",  required_argument,   0,  'r' },
        {"date",    required_argument,   0,  'd' },
        {"time",    required_argument,   0,  't' },
        {0,         0,                   0,  0   }
    };
  
  int opt;
  int long_index;
  
  while( ( opt = getopt_long_only(argc, argv,"", long_options, &long_index ) ) != -1 )  {
    
    
    
    switch( opt ){
      case 'i':
	  input = optarg;
	  break;
      case 'r':
	  report = optarg;
	  break;
      case 'd':
	  startdate = optarg;
	  break;
      case 't':
	  starttime = optarg;
	  break;
	
      default:
	  cout << "Uknown options" << endl;
    }
    
  }
  
  cout << "Using repot definition " << input << endl;
  cout << "To create report " << report << endl;
  cout << "Using date/time " << startdate << " " << starttime << endl;
  
  
}


Options::Options()
{

}
