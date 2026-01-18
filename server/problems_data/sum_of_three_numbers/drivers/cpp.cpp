using namespace std;

int main() {
    string line;
    if (getline(cin, line)) {
        if (line.size() >= 2 && line.front() == '[' && line.back() == ']') {
            line = line.substr(1, line.size() - 2);
        }
        stringstream ss(line);
        string segment;
        vector<int> args;
        while(getline(ss, segment, ',')) {
            args.push_back(stoi(segment));
        }

        if (args.size() >= 3) {
            Solution sol;
            int result = sol.sumThreeNumbers(args[0], args[1], args[2]);
            cout << result << endl;
        }
    }
    return 0;
}
