#include "Reader.h"
#include <iostream>
#include <fstream>
#include <sstream>
using namespace std;

Reader::Reader(string dfname, int dn, int dN){
	fname = dfname;
	n = dn;
	N = dN;
	data.resize(N);
}

vector<vector<double>>& Reader::GetData(){

	//open file
		ifstream F;
		int i;
		F.open(fname);

	/*
	//read 2 first lines
		string header;
		for(i=0; i<5; i++){
			getline(F, header);
		}
	*/

	//read lines
		string raw;
		int k = 0;
		double x;
		while(getline(F, raw)){
			stringstream sst(raw);
			
			for(int i=0; i<n; i++) {
				sst >> x;
				data[k].push_back(x);
			}
			
			k++;
		}

	//close file
		F.close();

		return data;
}