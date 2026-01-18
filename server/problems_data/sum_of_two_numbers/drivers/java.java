class Driver {
    public static void main(String[] args) {
        Scanner scanner = new Scanner(System.in);
        if (scanner.hasNextLine()) {
            String line = scanner.nextLine();
            line = line.trim();
            if (line.startsWith("[") && line.endsWith("]")) {
                line = line.substring(1, line.length() - 1);
            }
            String[] parts = line.split(",");
            if (parts.length >= 2) {
                try {
                    int a = Integer.parseInt(parts[0].trim());
                    int b = Integer.parseInt(parts[1].trim());
                    
                    Solution sol = new Solution();
                    System.out.println(sol.sumTwoNumbers(a, b));
                } catch (NumberFormatException e) {
                    // Handle potential parsing errors
                }
            }
        }
        scanner.close();
    }
}