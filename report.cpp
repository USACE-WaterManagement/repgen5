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


#include "report.h"
#include "mildatetime.h"
#include <cstring>
#include <fstream>
#include <sstream>

using namespace std;


const char *standard_options[] = {
    "PICTURE",
    "MISSTR",
    "UNDEF",
    "TIME",
    "STIME",
    "ETIME",
    "DURATION",
    0  
};




Report::Report(Options& opts)
{
  options = opts;
  cout << "Loading report: " << options.input << endl;
  // go through the options and get the report and the data
  ifstream rep;
  rep.open( options.input.c_str(), ifstream::in );
  cout << rep.is_open() << endl;
  string line;
  
  // setup the initial variables
  cout << "Setting up curdate variable" << endl;
  Value cur_date( "MM/DD/YYYY ZZZT", "               ", "9999999999", TIME_VAL );
  cur_date.scalar = true;  
  time_t _time = time(NULL);
  cur_date.time_value.push_back( _time );
  
  
  this->data["%CURDATE"] =  cur_date;
  
  cout << "Setting up basdate variable" << endl;
  Value bas_date( "AAAbDD,bYYYYb@bZZZT", "                   ",  "9999999999", TIME_VAL );
  
  
  
  string fulldate = options.startdate + " " + options.starttime;
  _time = MilDateTime::parse( fulldate  );
  bas_date.time_value.push_back( _time );
  
  this->data["%BASDATE"] = bas_date;    
  
  cout << "Reading Actual report now" << endl;
  
  while( getline( rep, line ) )
  {    
    //cout << "Read: " << line << endl;
    if( line.find( "#FORM") != string::npos ){
      this->read_report_body( rep );
    }
    else if( line.find( "#DEF") != string::npos ){
      bool compiled= false;
      if( line.find( "complied") != string::npos ){
	complied = true;
      }
	  // already compiled
      stringstream _prog;
      
      string line;
      while( getline( rep, line ) ){
	  if( line.find("#ENDFORM") != string::npos ){
	      break; //done reading
	  }
	  
	  _prog >> line;
      }
      
      if( !compiled ){
	  // Compiler compiler( _prog );
	  // _prog = compiler.compile();
      }
      
      Program prog( _prog );
      prog.run( this->data );
      
      //this->read_variable_definitions( rep );      
    } // anything else gets ignored    
  }  
  
  
}


void Report::read_report_body(ifstream& file)
{
  // read the report body and store the reporft
  string line;
  //cout << "Reading body" << endl;;  
  while(getline( file, line )){
    if(  line.find( "#ENDFORM" ) != string::npos ){
      ///cout << "End of Form found" << endl;
      break;
    }    
    cout << "READ: " << line << endl;
    //cout << line << endl;
    this->report.push_back(line);  
  }
  
}




void Report::print()
{
  //go through each line of the report
  //scan through the line and replace data as needed
  cout << "Printing Report: " << options.report << endl;
  ofstream rep_out( options.report.c_str(), ofstream::out );
  cout << report.size();
  while( !report.empty() )
  {
    string line = report.front();
    report.pop_front();
   
    for( map<string,Value, std::greater<string> >::iterator iter = data.begin(); iter != data.end(); iter++ ){
      string key = iter->first;
      Value  values = iter->second;
      size_t pos = string::npos;
      if( (pos = line.find( key ) ) != string::npos ){
	  cout << "Found variable in report: " << key << endl;	  
	  line.replace( pos,  values.picture.size() , values.get_formatted( values.index )  );	  
	  values.index++;
      }
      
      
      
      
    }
    
    
    
    rep_out << line << endl;
  }
  
}
