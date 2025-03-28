#ifndef __READER__
#define __READER__

#include <string>
#include <vector>
using namespace std;

class Reader {
    
    public:
        Reader() = default;
        Reader(string fname, int n, int N=5000);
        ~Reader() = default;

////////////////////////////////////////////////////////////////////////////////    

        vector<vector<double>>& GetData();

    private:
        int n;
        int N;
        string fname;
        vector<vector<double>> data;
};

#endif