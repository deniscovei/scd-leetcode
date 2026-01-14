int main() {
    string line1, line2;
    if(getline(cin, line1) && getline(cin, line2)) {
        // Parse nums
        if(line1.size() > 2) {
            line1 = line1.substr(1, line1.size() - 2);
        }
        stringstream ss(line1);
        string item;
        vector<int> nums;
        while (getline(ss, item, ',')) {
            if(!item.empty()) nums.push_back(stoi(item));
        }
        int target = stoi(line2);
        Solution sol;
        vector<int> res = sol.twoSum(nums, target);
        cout << "[";
        for(int i=0; i<res.size(); ++i) {
            cout << res[i];
            if(i < res.size()-1) cout << ",";
        }
        cout << "]";
    }
    return 0;
}