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


#ifndef REPORT_H
#define REPORT_H

#include <iostream>
#include <fstream>
#include <cstdlib>
#include <vector>
#include <list>
#include <map>
#include <functional>
#include "options.h"
#include "value.h"
#include "repgenutil.h"
using namespace std;


extern const char *standard_options[];

class Report
{
	private:
		list<string> report; // vector of report lines
		data_map     data;   // map of variable -> data, sorted backwards so that when we search for the variable we get the logest name first
									/*
									 * e.g. if you have %TMP %TMP2
									 * and map sorted in the default order then TMP2 gets found as TMP.
									 */
		Options options;
	
		void read_report_body( ifstream &file );
		//void read_variable_definitions( ifstream &file );
		
	public:

		Report( Options &opts );
	
		

		
		void print();

  
};

#endif // REPORT_H
