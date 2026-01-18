import sys
import json

if __name__ == '__main__':
    try:
        input_data = sys.stdin.read().strip()
        if not input_data:
            sys.exit(0)
            
        # Expecting JSON list like [1, 2]
        params = json.loads(input_data)
        a = params[0]
        b = params[1]
        
        sol = Solution()
        result = sol.sumTwoNumbers(a, b)
        print(result)
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
