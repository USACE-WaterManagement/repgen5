#include <iostream>
#include <fstream>
#include <string>
#include "options.h"
#include "report.h"
#include "queue.h"
#include "value.h"
#include "mildatetime.h"

using namespace std;


int main( int argc, char **argv )
{
	// Process all times as is
	setenv("TZ", "", 1);
	tzset();
  
	time_t _time = MilDateTime::parse("21Jun2014 1500");
	cout << "Repgen 5" << endl;
	// parse the options
	Options options( argc, argv );
	cout << "  " <<  options.input << endl;
	// read the report
	Report report( options );
	// present the report
	report.print();

	
	cout << "Done" << endl;
	return 0;
}	
