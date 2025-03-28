#include <iostream>
#include <fstream>
#include <sstream>
using namespace std;

void ReadFile(string fname, double (&t)[1023], double (&A)[1023]){

//open fil
	ifstream F;
	int i;
	F.open(fname);

//read 2 first lines
	string header;
	for(i=0; i<5; i++){
		getline(F, header);
	}

//read lines
	string raw;
	for(i=0; i<1023; i++){
		getline(F, raw);
		stringstream sst(raw);
		sst >> t[i] >> A[i];
	}

//close file
	F.close();
}
