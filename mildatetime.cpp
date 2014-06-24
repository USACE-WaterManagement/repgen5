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


#include "mildatetime.h"
#include <ctime>
#include <algorithm>
#include <cctype>
#include <cstdlib>
#include <cstring>
#include <string>
#include <sstream>
#include <iostream>
#include <cstdlib>
using namespace std;

// 01MAR2014 0800
// 01234567890123
// 01MAR14 0800

const char *month_long[] = {
  "January",
  "Februray",
  "March",
  "April",
  "May",
  "June",
  "July",
  "August",
  "September",
  "October",
  "November",
  "December"
};

const char *month_short[] = {
  "JAN",
  "FEB",
  "MAR",
  "APR",
  "MAY",
  "JUN",
  "JUL",
  "AUG",
  "SEP",
  "OCT",
  "NOV",
  "DEC"
};


time_t MilDateTime::parse( char *date ){
    string str( date );
    return MilDateTime::parse(str);
}

time_t MilDateTime::parse(string& date)
{
  time_t _time;
  int day;
  string month_str;
  int month;
  int year;
  int hour;
  int minute;
  
  stringstream stream;
  stream.str( date.substr(0, 2 ) );
  stream >> day;
  
  stream.clear();
  stream.str( date.substr(2,3) );
  stream >> month_str;
  
  // here we diverge
  stream.clear();
  if( date.size() == 14 ){
    stream.str( date.substr(5,4) );
    stream >> year;
    
    stream.clear();
    stream.str( date.substr( 10, 2) );
    stream >> hour;
    
    stream.clear();
    stream.str( date.substr( 12, 2) );
    stream >> minute;
    
  } else if( date.size() == 12 ){
    stream.str( date.substr( 5,2 ) );
    stream >> year;
    
    stream.clear();
    stream.str( date.substr( 5, 2 ) );
    stream >> year;
    cout << "Two digit year provided, assuming 1900" << endl;
    year = year + 1900;
    
    stream.clear();
    stream.str( date.substr( 8, 2 ) );
    stream >> hour;
    
    stream.clear();
    stream.str( date.substr( 10, 2 ) );
    stream >> minute;       
    
  } else{
    cout << "Can't parse date " << date << endl;
    exit(1);
  }
  
  std::transform(month_str.begin(), month_str.end(), month_str.begin(), ::toupper );
  
  cout << "Date values are " << endl;
  cout << "year  = " << year << endl;;
  cout << "month = " << month_str << endl;
  cout << "day   = " << day << endl;
  cout << "hour  = " << hour << endl;
  cout << "minute= " << minute << endl;
  
  month = -1;
  for( int i=0; i < 12; i ++)
  {
    if( month_str == month_short[i] ){
      month = i;
    }
  }
  if( month == -1 ){
      cout << "Unknown month in date" << endl;
      exit(1);
  }
  
  tm mytime;
  memset( &mytime, 0, sizeof( tm ) );
  mytime.tm_year = year-1900;
  mytime.tm_mon  = month;
  mytime.tm_mday = day;  
  mytime.tm_hour = hour;
  mytime.tm_min  = minute;
  
  _time = mktime( &mytime );
  cout << _time << endl;
  cout << mytime.tm_mday << endl;
  cout << "Time is " << ctime( &_time ) << endl;
  
  return _time;
  
}
