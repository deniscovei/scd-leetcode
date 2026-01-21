public class Driver {
    public static void main(String[] args) {
        Scanner scanner = new Scanner(System.in);
        if(scanner.hasNextLine()) {
            String line1 = scanner.nextLine().trim();
            String line2 = scanner.hasNextLine() ? scanner.nextLine().trim() : "";
            if(line1.length() > 2) line1 = line1.substring(1, line1.length()-1);
            String[] parts = line1.split(",");
            int[] nums = new int[parts.length];
            for(int i=0; i<parts.length; i++) {
                if(!parts[i].trim().isEmpty()) nums[i] = Integer.parseInt(parts[i].trim());
            }
            int target = Integer.parseInt(line2);
            Solution sol = new Solution();
            int[] res = sol.twoSum(nums, target);
            System.out.print("[");
            for(int i=0; i<res.length; i++) {
                System.out.print(res[i]);
                if(i < res.length - 1) System.out.print(",");
            }
            System.out.print("]");
        }
    }
}