/*
Basios Georgios
AM: 5050
cs05050@uoi.gr
*/

import java.util.*;

public class SplayTree<Key extends Comparable<Key>, Item> {

    TreeNode root;        // root of tree

    class TreeNode {

        Key key;
        Item item;
        TreeNode parent, left, right;     // node's right child
        int height;         // node's height

        // create new node
        TreeNode(Key key, Item item) {
            this.key = key;
            this.item = item;
            this.parent = null;
            this.height = 1;
        }

        @Override
        public String toString(){
            return "["+key+"]";
        }
    }

    //******************** HELPER METHODS */
    private void rotateLeft(TreeNode x) {
        TreeNode y = x.right;

        if (y == null) {
            return;
        }

        x.right = y.left;
        if (x.right != null) {
            x.right.parent = x;
        }

        y.left = x;
        y.parent = x.parent;
        if (x.parent != null) {
            if (x.parent.left == x) {
                x.parent.left = y;
            } else {
                x.parent.right = y;
            }
        } else {
            root = y;
        }
        x.parent = y;
    }

    private void rotateRight(TreeNode y) {
        TreeNode x = y.left;

        if (x == null) {

            return;
        }

        y.left = x.right;
        if (y.left != null) {
            y.left.parent = y;
        }

        x.right = y;
        x.parent = y.parent;
        if (y.parent != null) {
            if (y.parent.left == y) {
                y.parent.left = x;
            } else {
                y.parent.right = x;
            }
        } else {
            root = x;
        }
        y.parent = x;
    }

    private void splay(TreeNode x){
        if (x == root || x == null) return;

        while (x != root){
            TreeNode parent = x.parent;
            TreeNode grandpa = parent.parent;

            // 1st case - parent is root
            if (parent == root){
                if (x == parent.left) rotateRight(parent);
                else rotateLeft(parent);
            }
            else if ((parent != null) && (grandpa != null)){
                // 2nd case - straight zig-zag
                // all left
                if ((x == parent.left) && (parent == grandpa.left)){
                    rotateRight(grandpa);
                    rotateRight(parent);
                }
                // all right
                else if ((x == parent.right) && (parent == grandpa.right)){
                    rotateLeft(grandpa);
                    rotateLeft(parent);
                }

                // 3rd case - classic zig-zag
                else if ((x == parent.right) && (parent == grandpa.left)){
                    rotateLeft(parent);
                    rotateRight(grandpa);
                }
                else if ((x == parent.left) && (parent == grandpa.right)){
                    rotateRight(parent);
                    rotateLeft(grandpa);
                }
            }
        }
    }

    private TreeNode searchNode(Key key) {
        TreeNode v = root;
        TreeNode pv = null; // parent of v
        while (v != null) {
            int c = key.compareTo(v.key);
            pv = v;
            if (c < 0) {
                v = v.left;
            } else if (c > 0) {
                v = v.right;
            } else {
                return v; // item found; return node that contains it
            }
        }
        return pv; // item not found; return last node on the search path
    }

    public int getTreeHeight() {
        return calculateHeight(root);
    }

    private int calculateHeight(TreeNode x) {
        if (x == null) return 0;
        int leftCh = calculateHeight(x.left);
        int rightChild = calculateHeight(x.right);
        return 1 + Math.max(leftCh, rightChild);
    }

    //******************** CORE FUNCTIONS */
    public Item search(Key key) {
        if (root == null) return null;

        TreeNode node = searchNode(key);
        splay(node);

        if (node.key.compareTo(key) == 0) {
            return node.item;
        }
        return null;
    }

    public void insert(Key key, Item item){
        if (root == null) {
            root = new TreeNode(key, item);
            return;
        }

        TreeNode node = searchNode(key);
        int comp = node.key.compareTo(key);
        if (comp == 0) {
            node.item = item;
            splay(node);
            return;
        }

        TreeNode newNode = new TreeNode(key, item);
        if (comp < 0){
            node.right = newNode;
            newNode.parent = node;
        }
        else {
            node.left = newNode;
            newNode.parent = node;
        }

        splay(newNode);
        return;
    }

    public int delete(Key key){
        if (root == null) return 1;

        TreeNode node = searchNode(key);
        int comp = node.key.compareTo(key);

        splay(node);
        if (comp != 0) return 1;
        else{
            if (root.right == null && root.left == null) root = null;
            else if (root.right == null && root.left != null){
                root = root.left;
                root.parent = null;
            }
            else if (root.right != null && root.left == null){
                root = root.right;
                root.parent = null;
            }
            else{
                TreeNode leftTreeNode = root.left;
                TreeNode rightTreeNode = root.right;
                
                root = leftTreeNode;
                root.parent = null;

                TreeNode current = root;
                while (current.right != null){
                    current = current.right;
                }
                splay(current);
                current.right = rightTreeNode;

                if (rightTreeNode != null) rightTreeNode.parent = current;
            }
        }
        return 0;
    }

        private void printSpaces(int spaces){
        for (int i =0; i<spaces; i++){
            System.out.print(" ");
        }
    }

    public void printTree() {
        int height = getTreeHeight();
        if (height == 0) {
            System.out.println("Tree is empty");
            return;
        }

        List<TreeNode> currentLevel = new ArrayList<>();
        currentLevel.add(root);

        int totalNodes = (int)(Math.pow(2, height/2));
        int nodeLength = 4;
        int betweenBros = 4; //for last level
        int betweenTrees = 10; //for last level
        int maxLength = (totalNodes*nodeLength) + (totalNodes*(betweenBros/2)) + (betweenTrees*(totalNodes-1));

        for (int i = 0; i < height; i++) {
            int fromSides = (maxLength/(int)(Math.pow(2, i+1))) - nodeLength/2;
            betweenBros = 2*fromSides;
            printSpaces(fromSides);

            List<TreeNode> nextLevel = new ArrayList<>();

            for (TreeNode node : currentLevel) {
                if (node != null) {
                    System.out.print(node);
                    
                    nextLevel.add(node.left);
                    nextLevel.add(node.right);
                } 
                else{
                    printSpaces(nodeLength);

                    nextLevel.add(null); 
                    nextLevel.add(null);
                }
                printSpaces(betweenBros);
            }
            System.out.println("\n");

            currentLevel = nextLevel;
        }
        for (int i =0; i<maxLength; i++){
            System.out.print("=");
        }
        System.out.println();
    }

    public static void main(String[] args) {
        System.out.println("\n[*]      Test Splay Tree      [*]");
        System.out.println("=================================");
        if (args.length == 0) {
            System.out.println("Usage: java SplayTree <n>");
            return;
        }

        int n = Integer.parseInt(args[0]);
        System.out.println("- Number of keys n = " + n);

        SplayTree<Integer, String> T = new SplayTree<Integer, String>();

        Random rand = new Random(0);
        int[] keys = new int[n];
        for (int i = 0; i < n; i++) { // store n random numbers in [0,2n)
            keys[i] = rand.nextInt(2 * n);
        }

        long startTime = System.currentTimeMillis();
        for (int i = 0; i < n; i++) {
            String item = "item" + i;
            T.insert(keys[i], item);
            //T.printTree(n); //DEBUG: UNCOMMENT TO SEE THE TREE DURING CREATION
        }

        long endTime = System.currentTimeMillis();
        long totalTime = endTime - startTime;

        if ( n<= 12){
            System.out.println("\nConstructed Splay Tree:");
            T.printTree(); 
        }

        System.out.println("- Construction time = " + totalTime);
        System.out.println("- Tree height = " + T.getTreeHeight());

        // test search queries
        startTime = System.currentTimeMillis();
        for (int i = 0; i < n; i++) {
            if (T.search(keys[i]) == null) {
                System.out.println("- Key " + keys[i] + " not found!");
            }
        }

        endTime = System.currentTimeMillis();
        totalTime = endTime - startTime;
        System.out.println("- Search time = " + totalTime);


        // test deletions
        System.out.println("\n[*]     Testing deletions     [*]");
        System.out.println("=================================");
        startTime = System.currentTimeMillis();
        for (int i = 0; i < n/2; i++) {
            T.delete(keys[i]);
            //T.printTree(); //DEBUG: UNCOMMENT TO SEE THE TREE DURING DELETION
        }

        for (int i = n/2; i < n; i++) {
            T.delete(keys[i]);
            //T.printTree(); //DEBUG: UNCOMMENT TO SEE THE TREE DURING DELETION
        }
        
        endTime = System.currentTimeMillis();
        totalTime = endTime - startTime;

        System.out.println("Remains of Splay Tree:");
        T.printTree(); 
        System.out.println();

        System.out.println("- Deletion time = " + totalTime);
        System.out.println("- Tree height after deletions = " + T.getTreeHeight());

        // verify that all keys have been deleted
        boolean allDeleted = true;
        for (int i = 0; i < n; i++) {
            if (T.search(keys[i]) != null) {
                System.out.println("- Key " + keys[i] + " still found after deletion!");
                allDeleted = false;
            }
        }
        if (allDeleted) System.out.println("- All keys deleted successfully");
        
        System.out.println();
    }
    
}
