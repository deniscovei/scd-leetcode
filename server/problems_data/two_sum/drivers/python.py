
if __name__ == '__main__':
    lines = sys.stdin.read().split('\n')
    lines = [l.strip() for l in lines if l.strip()]
    if len(lines) >= 2:
        nums = json.loads(lines[0])
        target = int(lines[1])
        sol = Solution()
        result = sol.twoSum(nums, target)
        print(json.dumps(result))