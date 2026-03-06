import java.util.Scanner;

public class CliMain{

    static Scanner scanner = new Scanner(System.in);

    private static int getIntInput(){
        while (true) {
            while (!scanner.hasNextInt()) {
                String bad = scanner.next();
                System.out.println("Invalid input. Select a positive Integer!");
                System.out.print("> ");
            }
            int input = scanner.nextInt();
            if (input >= 0) return input;
            System.out.println("Invalid input. Select a positive Integer!");
            System.out.print("> ");
        }
    }

    private static void printMenu(){
        System.out.println("Choose an action:");
        System.out.println("-----------------------------------");
        System.out.println("1. Insert");
        System.out.println("2. Delete");
        System.out.println("3. Search");
        System.out.println("4. Print Tree");
        System.out.println("-----------------------------------");
        System.out.println("0. Exit                  9. Go Back");
        System.out.print("> ");
    }

    private static void interactiveTwoFour(){
        System.out.println("\nTwo-Four Tree interactive playground");
        System.out.println("====================================");

        TwoFourTree<Integer, String> T = new TwoFourTree<Integer, String>();

        while (true) {
            printMenu();
            int action = getIntInput();
            if (action == 0) System.exit(0);
            if (action == 9) return;
            switch (action) {
                case 1:
                    System.out.print("Enter key to insert: ");
                    int key = getIntInput();
                    String item = "item" + key;
                    T.insert(key, item);
                    System.out.println("Inserted key ["+key+"]");
                    System.out.println();
                    break;
                case 2:
                    System.out.print("Enter key to delete: ");
                    int key2 = getIntInput();
                    T.delete(key2);
                    if (T.search(key2) != null) System.out.println("Deleted key ["+key2+"]\n");
                    else System.out.println("Key ["+key2+"] doesn't belong in Tree\n");
                    break;
                case 3:
                    System.out.print("Enter key to search: ");
                    int key3 = getIntInput();
                    String itm3 = T.search(key3);
                    if (itm3 != null) System.out.println("Found key ["+key3+"] with item: " + itm3+"\n");
                    else System.out.println("Key ["+key3+"] doesn't belong in Tree\n");
                    break;
                case 4 : 
                    T.printTree();
                    System.out.println();
                    break;
                default : System.out.println("Invalid action!");
            }
        }
    }

    private static void interactiveSplay(){
        System.out.println("\nSplay Tree interactive playground");
        System.out.println("=================================");

        SplayTree<Integer, String> T = new SplayTree<Integer, String>();

        while (true) {
            printMenu();
            int action = getIntInput();
            if (action == 0) System.exit(0);
            if (action == 9) return;
            switch (action) {
                case 1:
                    System.out.print("Enter key to insert: ");
                    int key = getIntInput();
                    String item = "item" + key;
                    T.insert(key, item);
                    System.out.println("Inserted key ["+key+"]");
                    System.out.println();
                    break;
                case 2:
                    System.out.print("Enter key to delete: ");
                    int key2 = getIntInput();
                    int flag = T.delete(key2);
                    if (flag == 0) {
                        System.out.println("Deleted key ["+key2+"]\n");
                    }
                    else System.out.println("Key ["+key2+"] doesn't belong in Tree\n");
                    break;
                case 3:
                    System.out.print("Enter key to search: ");
                    int key3 = getIntInput();
                    String itm3 = T.search(key3);
                    if (itm3 != null) System.out.println("Found key ["+key3+"] with item: " + itm3+"\n");
                    else System.out.println("Key ["+key3+"] doesn't belong in Tree\n");
                    break;
                case 4 : 
                    T.printTree();
                    System.out.println(); 
                    break;
                default : System.out.println("Invalid action!");
            }
        }
    }

    private static void interactiveInterval(){
        System.out.println("\nInterval Tree interactive playground");
        System.out.println("====================================");

        IntervalTree T = new IntervalTree();

        while (true) {
            printMenu();
            int action = getIntInput();
            if (action == 0) System.exit(0);
            if (action == 9) return;
            switch (action) {
                case 1:
                    int low;
                    int high;
                    System.out.println("Node to insert");
                    while (true){
                        System.out.print("Enter low interval: ");
                        low = getIntInput();
                        System.out.print("Enter high interval: ");
                        high = getIntInput();
                        if (low < high) break;
                        else System.out.println("Low interval must be smaller than the high!");
                    }
                    IntervalTree.IntervalNode node = T.new IntervalNode(new IntervalTree.Interval(low, high)); 
                    T.intervalInsert(node);
                    System.out.println("Inserted ["+low+","+high+"]");
                    System.out.println();
                    break;
                case 2:
                    System.out.println("Node to delete");
                    System.out.print("Enter low interval: ");
                    int low2 = getIntInput();
                    System.out.print("Enter high interval: ");
                    int high2 = getIntInput();
                    IntervalTree.IntervalNode node2 = T.new IntervalNode(new IntervalTree.Interval(low2, high2));
                    int flag = T.intervalDelete(node2);
                    if (flag == 0) System.out.println("Deleted ["+low2+","+high2+"]\n");
                    else System.out.println("Interval ["+low2+","+high2+"] doesn't belong in Tree\n");
                    break;
                case 3:
                    System.out.print("Enter value to search: ");
                    int value = getIntInput();
                    IntervalTree.IntervalNode node3 = T.intervalSearch(value);
                    if (node3 != T.getNIL()) System.out.println("Found " + node3.interval+"\n");
                    else System.out.println("Couldn't find any interval with value: " + value+"\n");
                    break;
                case 4 : 
                    T.printTree(); 
                    System.out.println();
                    break;
                default : System.out.println("Invalid action!");
            }
        }
    }

    private static void InteractivePlay(int tree){
        switch (tree) {
            case 1: interactiveTwoFour(); break;
            case 2: interactiveSplay(); break;
            case 3: interactiveInterval(); break;
            default: System.out.println("Invalid Tree type!");
        }
    }

    private static void automaticPlay(int tree){
        String limit = "";
        if (tree == 1) limit = "keys (Less than 50 to print the Tree):";
        if (tree == 2) limit = "keys (Less than 12 to print the Tree):";
        if (tree == 3) limit = "intervals (Less than 10 to print the Tree):";
        System.out.println("Give the number of " + limit);
        System.out.print("> ");
        int n = getIntInput();

        String[] args = {String.valueOf(n)};

        try{
            switch (tree) {
                case 1: TwoFourTree.main(args); break;
                case 2: SplayTree.main(args); break;
                case 3: IntervalTree.main(args); break;
                default: System.out.println("Invalid Tree type!");
            }
        }          
        catch (Exception e) {
            System.out.println("An error occured:" + e.getMessage());
        }
    }

    private static int modeMenu(){
        int mode;
        while (true){
            System.out.println("\nSelect a mode:");
            System.out.println("-----------------------------------");
            System.out.println("1. Interactive Mode");
            System.out.println("2. Automatic Mode");
            System.out.println("-----------------------------------");
            System.out.println("0. Exit                     8. Help");
            System.out.print("> ");
            mode = getIntInput();

            if (mode >=0 && mode <= 3 || mode == 8) break;
        }
        return mode;
    }

    private static int treeMenu(){
        int tree;
        while (true){
            System.out.println("\nSelect a Tree type:");
            System.out.println("-----------------------------------");
            System.out.println("1. Two-Four Tree");
            System.out.println("2. Splay Tree");
            System.out.println("3. Interval Tree");
            System.out.println("-----------------------------------");
            System.out.println("0. Exit                  9. Go Back");
            System.out.print("> ");
            tree = getIntInput();

            if (tree >= 0 && tree <=3 || tree == 9) break;
        }
        return tree;
    }

    private static void helpMenu(){
        System.out.println("1. Interactive mode:");
        System.out.println("   You can select from a menu of Data Structure trees and manually:");
        System.out.println("           - Insert keys or intervals");
        System.out.println("           - Delete a key or an interval");
        System.out.println("           - Search for a key or a value");
        System.out.println("           - Also, you can print the tree you made at any time\n");
        System.out.println("2. Automatic mode:");
        System.out.println("   You can select from a menu of Data Structure trees. The system");
        System.out.println("   will calculate for you insertion, deletion, and search times.");
        System.out.println("   For a specific range of keys or intervals, you can also watch");
        System.out.println("   the constructed tree.");

        return;
    }
    public static void main(String[] args) {
        System.out.println("\nDATA STRUCTURES TREE IMPLEMENTATION");
        System.out.println("----- Made by BASIOS GEORGIOS -----");
        System.out.println("===================================");
        
        while (true) {
            int mode = modeMenu();

            if (mode == 0) System.exit(0);
            if (mode == 8) {
                helpMenu();
                mode = modeMenu();
            }

            while (true) {
                int tree = treeMenu();

                if (tree == 0) System.exit(0);
                if (tree == 9) break;

                if (mode == 1) InteractivePlay(tree);
                else if (mode == 2) automaticPlay(tree);
            }
        }
    }
}

