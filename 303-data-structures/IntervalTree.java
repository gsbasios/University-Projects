/*
Basios Georgios
AM: 5050
cs05050@uoi.gr
*/

import java.util.*;

public class IntervalTree {

    private IntervalNode root;
    private final IntervalNode NIL;

    public static class Interval {
        int low, high;

        public Interval(int low, int high){
            this.low = low;
            this.high = high;
        }

        @Override
        public String toString(){
            int low = this.low;
            int high = this.high;
            return "["+low+","+high+"]";
        }
    }

    public class IntervalNode {
        Interval interval;
        int max;
        IntervalNode parent, left, right;
        boolean isRed;

        public IntervalNode(Interval interval) {
            this.interval = interval;
            this.max = interval.high;
            this.isRed = true;
            this.left = NIL;
            this.right = NIL;
            this.parent = NIL;
        }
    }

    //create the NIL node during the ini
    public IntervalTree() {
        Interval interval = new Interval(Integer.MIN_VALUE, Integer.MIN_VALUE);
        NIL = new IntervalNode(interval);
        NIL.max = Integer.MIN_VALUE;
        NIL.isRed = false;
        NIL.left = NIL.right = NIL.parent = NIL;
        root = NIL;
    }

    public IntervalNode getNIL(){
        return this.NIL;
    }

    //******************** HELPER METHODS */
    private boolean isRed(IntervalNode x) {return x != NIL && x.isRed;}

    private void colorRed(IntervalNode x) {if (x != NIL) x.isRed = true;}

    private void colorBlack(IntervalNode x) {if (x != NIL) x.isRed = false;}

    public boolean overlaps(int intSearch, Interval intNode){
        return (intNode.low <= intSearch && intSearch <= intNode.high);
    }

    private void updateMax(IntervalNode node){
        if (root == NIL) return;

        //in each step, check which node has the bigger max, like BST search
        while (node != NIL){
            int maximum = node.interval.high;
            if (node.left != NIL) maximum = Math.max(maximum, node.left.max);
            if (node.right != NIL) maximum = Math.max(maximum, node.right.max);
            node.max = maximum;

            if (node.parent != NIL){
                if (node.parent.max >= node.max) return;
            }
            node = node.parent;
        }
    }

    private void rotateLeft(IntervalNode x) {
        IntervalNode y = x.right;

        if (y == NIL) {
            return;
        }

        x.right = y.left;
        if (x.right != NIL) {
            x.right.parent = x;
        }

        y.left = x;
        y.parent = x.parent;
        if (x.parent != NIL) {
            if (x.parent.left == x) {
                x.parent.left = y;
            } else {
                x.parent.right = y;
            }
        } else {
            root = y;
        }
        x.parent = y;

        updateMax(x);
    }

    private void rotateRight(IntervalNode y) {
        IntervalNode x = y.left;

        if (x == NIL) {
            return;
        }

        y.left = x.right;
        if (y.left != NIL) {
            y.left.parent = y;
        }

        x.right = y;
        x.parent = y.parent;
        if (y.parent != NIL) {
            if (y.parent.left == y) {
                y.parent.left = x;
            } else {
                y.parent.right = x;
            }
        } else {
            root = x;
        }
        y.parent = x;

        updateMax(y);
    }

    private void fixInsert(IntervalNode x) {
        while (x!=root && isRed(x.parent)){    
            IntervalNode parent = x.parent;
            IntervalNode grandpa = parent.parent;
 
            // parent of x is left child
            if (parent == grandpa.left){
                IntervalNode uncle = grandpa.right;
                // if uncle is red
                if (isRed(uncle)){
                    colorRed(grandpa);
                    colorBlack(uncle);
                    colorBlack(parent);
                    x=grandpa;
                }
                // if uncle is black
                else{
                    // if both x and parent are left
                    if (x == parent.left){
                        rotateRight(grandpa);
                        colorRed(grandpa);
                        colorBlack(parent);
                    }
                    // if x right and parent left
                    else{
                        rotateLeft(parent);
                        x=parent;
                        parent=x.parent;
                        rotateRight(grandpa);
                        colorRed(grandpa);
                        colorBlack(parent);
                    }
                }
            }
            // parent of x is right child
            else{
                IntervalNode uncle = grandpa.left;
                // if uncle is red
                if (isRed(uncle)){
                    colorRed(grandpa);
                    colorBlack(uncle);
                    colorBlack(parent);
                    x = grandpa;
                }
                // if uncle is black
                else{
                    // if both x and parent are right
                    if (x == parent.right){
                        rotateLeft(grandpa);
                        colorRed(grandpa);
                        colorBlack(parent);
                    }
                    // if x left and parent right
                    else{
                        rotateRight(parent);
                        x=parent;
                        parent=x.parent;
                        rotateLeft(grandpa);
                        colorRed(grandpa);
                        colorBlack(parent);
                    }
                }
            }
        }
        colorBlack(root);
    }

    //used in the main to test deletions
    public IntervalNode searchExactNode(IntervalNode x){
        IntervalNode current = root;
        //works like BST search to move to nodes
        while (current != NIL) {
            if (x.interval.low == current.interval.low && x.interval.high == current.interval.high) return current;
            else if (x.interval.low < current.interval.low || (x.interval.low == current.interval.low && x.interval.high < current.interval.high)) current = current.left;
            else current = current.right;
        }
        return NIL;
    }

    private IntervalNode searchNode(int low) {
        IntervalNode v = root;
        IntervalNode pv = NIL; // parent of v
        while (v != NIL) {
            int c = low - v.interval.low;
            pv = v;
            if (c < 0) v = v.left;
            else if (c > 0) v = v.right;
            else return v;
        }
        return pv; // item not found; return last node on the search path
    }

    public int getTreeHeight() {
        return calculateHeight(root);
    }

    private int calculateHeight(IntervalNode x) {
        if (x == NIL) return 0;
        int leftCh = calculateHeight(x.left);
        int rightChild = calculateHeight(x.right);
        return 1 + Math.max(leftCh, rightChild);
    }

    //******************** CORE FUNCTIONS */
    public IntervalNode intervalSearch(int value){
        IntervalNode x = root;

        while (x !=NIL && !overlaps(value, x.interval)){
            if (x.left != NIL && x.left.max >= value) x = x.left;
            else x = x.right;
        }
        return x;  
    }

    public void intervalInsert(IntervalNode newNode){
        int nodeLow = newNode.interval.low;
        int nodeHigh = newNode.interval.high;

        newNode.left = newNode.right = NIL;

        if (root == NIL) {
            root = newNode;
            colorBlack(root);
            return;
        }

        IntervalNode node = searchNode(nodeLow); // go to the last node with same key or parent to insert
        while (true){
            if (node == NIL) return;
            else if (nodeLow == node.interval.low){ // same low values
                if (nodeHigh == node.interval.high) return;
                if (nodeHigh < node.interval.high){ //new node has lower high key than current node
                    if (node.left == NIL) { //if left child is empty, put the node, else check in this left child
                        node.left = newNode;
                        newNode.parent = node;
                        colorRed(newNode);
                        break;
                    }
                    else node = node.left;
                }
                else {
                    if (node.right == NIL) { //if right child is empty, put the node, else check in this right child
                        node.right = newNode;
                        newNode.parent = node;
                        colorRed(newNode);
                        break;
                    }
                    else node = node.right;
                }
            }
            else {
                if (nodeLow < node.interval.low){ //if new low is smaller than current, check left
                    if (node.left == NIL) {
                        node.left = newNode;
                        newNode.parent = node;
                        colorRed(newNode);
                        break;
                    }
                    node = node.left;
                }
                else { //if new low is bigger than current, check right
                    if (node.right == NIL) { 
                        node.right = newNode;
                        newNode.parent = node;
                        colorRed(newNode);
                        break;
                    }
                    node = node.right;
                }
            }
        }
        // updateMax will run in O(1)
        updateMax(newNode);
        fixInsert(newNode);
    }

    public int intervalDelete(IntervalNode x){
        if (root == NIL) return 1;
        if (root.left == NIL && root.right == NIL) root = NIL;

        // search for node with the wanted low interval
        IntervalNode node = searchNode(x.interval.low); 
        IntervalNode toDelete = NIL;

        while (node != NIL){
            int low = node.interval.low;
            int high = node.interval.high;

            if (low == x.interval.low && high == x.interval.high){
                toDelete = node; // the node we want
                break;
            }
            if (x.interval.low > low) node = node.right;
            else if (x.interval.low < low) node = node.left;
            else {
                // second check with the high intervals
                if (x.interval.high < node.interval.high) node = node.left;
                else node = node.right;
            }
        }

        // not found
        if (toDelete == NIL) return 1;

        IntervalNode z;
        IntervalNode parent;
        IntervalNode child;

        if (toDelete.left == NIL){
            z = toDelete;
            parent = toDelete.parent;
            child = toDelete.right;
        }
        else if (toDelete.right == NIL){
            z = toDelete;
            parent = toDelete.parent;
            child = toDelete.left;
        }
        else {
            IntervalNode successor = toDelete.right;
            while (successor.left != NIL){
                successor = successor.left;
            }
            z = successor;
            parent = z.parent;
            child = z.right;
            toDelete.interval = z.interval;
        }
        
        boolean zOriginalRed = isRed(z);
        boolean zWasLeftChild = false;

        if (parent != NIL && parent.left == z) zWasLeftChild = true;

        if (parent == NIL) {
            root = child;
            if (root != NIL) root.parent = NIL;
        }
        else {
            if (parent.left == z) parent.left = child;
            else parent.right = child;
        }
        if (child != NIL) child.parent = parent;

        if (parent != NIL) updateMax(parent);
        
        if (zOriginalRed == false ) {
            if (child != NIL && child.isRed) colorBlack(child);
            else fixDelete(child, parent, zWasLeftChild);
        }
        return 0;
    }

    private void fixDelete(IntervalNode x, IntervalNode parent, boolean xIsLeftChild) {
        while (x!=root && parent!=NIL && (x==NIL || !isRed(x))){
            if (parent.left != NIL) xIsLeftChild = x==parent.left;
            IntervalNode w = xIsLeftChild ? parent.right : parent.left;

            // if w is left child
            if (w==parent.left){
                // if w is black
                if (!isRed(w)){
                    // if left child of w is red
                    if (isRed(w.left)){
                        // if parent is red
                        if (isRed(parent)){colorRed(w);}
                        else{colorBlack(w);}
                        colorBlack(parent);
                        colorBlack(w.left);
                        rotateRight(parent);
                        break;
                    }
                    // if right child of w is red
                    else if (isRed(w.right)){
                        rotateLeft(w);
                        if (isRed(parent)){colorRed(w.parent);}
                        else {colorBlack(w.parent);}
                        colorBlack(parent);
                        rotateRight(parent);
                        break;
                    }
                    // if w has 2 black childs
                    else if (!isRed(w.left) && !isRed(w.right)){
                        colorRed(w);
                        if (isRed(parent)){
                            colorBlack(parent);
                            break;
                        }
                        else{
                            x=parent;
                            parent=x.parent;
                        }
                    }
                }
                // if w is red
                else{
                    colorBlack(w);
                    colorRed(parent);
                    rotateRight(parent);
                    w=parent.left;
                }
            }
            // if w is right child
            else{
                // if w is black
                 if (!isRed(w)){
                    // if right child of w is red
                    if (isRed(w.right)){
                        // if parent is red
                        if (isRed(parent)){colorRed(w);}
                        else{colorBlack(w);}
                        colorBlack(parent);
                        colorBlack(w.right);
                        rotateLeft(parent);
                        break;
                    }
                    // if left child of w is red
                    else if (isRed(w.left)){
                        rotateRight(w);
                        if (isRed(parent)){colorRed(w.parent);}
                        else {colorBlack(w.parent);}
                        colorBlack(parent);
                        rotateLeft(parent);
                        break;
                    }
                    // if w has 2 black childs
                    else if (!isRed(w.left) && !isRed(w.right)){
                        colorRed(w);
                        if (isRed(parent)){
                            colorBlack(parent);
                            break;
                        }
                        else{
                            x=parent;
                            parent=x.parent;
                        }
                    }
                }
                // if w is red
                else{
                    colorBlack(w);
                    colorRed(parent);
                    rotateLeft(parent);
                    w=parent.right;
                }
            }
        }
        if (x!=NIL) colorBlack(x);
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

        List<IntervalNode> currentLevel = new ArrayList<>();
        currentLevel.add(root);

        int totalNodes = (int)(Math.pow(2, height));
        int nodeLength = 10;
        int betweenBros = 2; //for last level
        int betweenTrees = 1; //for last level
        int maxLength = (totalNodes*nodeLength) + (totalNodes*(betweenBros/2)) + (betweenTrees*(totalNodes-1));

        for (int i = 0; i < height; i++) {
            int fromSides = (maxLength/(int)(Math.pow(2, i+1))) - nodeLength/2;
            betweenBros = 2*fromSides;
            printSpaces(fromSides);

            List<IntervalNode> nextLevel = new ArrayList<>();

            for (IntervalNode node : currentLevel) {
                if (node != NIL) {
                    String color = node.isRed ? "R" : "B";
                    System.out.print(node.interval + "" + color);
                    
                    nextLevel.add(node.left);
                    nextLevel.add(node.right);
                } 
                else{
                    printSpaces(nodeLength);

                    nextLevel.add(NIL); 
                    nextLevel.add(NIL);
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
        System.out.println("\n[*]     Test Interval Tree    [*]");
        System.out.println("=================================");
        if (args.length == 0) {
            System.out.println("Usage: java IntervalTree <n>");
            return;
        }

        int n = Integer.parseInt(args[0]);
        System.out.println("- Number of intervals n = " + n);

        IntervalTree T = new IntervalTree();

        Random rand = new Random(0);
        int cap = 1000;
        int diff = 200;
        
        List<Interval> intervals = new ArrayList<>();
        List<IntervalNode> nodes = new ArrayList<>();

        //generate the intervals
        for (int i = 0; i < n; i++) {
            int a,b;
            do {
                a = rand.nextInt(cap - diff);
                b = a + rand.nextInt(diff) + 1;
            }   while (a >= b); //if a >= b, regenerate
            intervals.add(new Interval(a, b));
            nodes.add(T.new IntervalNode(intervals.get(i)));
        }

        // ****************** TEST INSERTION
        long startTime = System.currentTimeMillis();
        //put the intervals in the tree, as nodes
        for (int i=0; i<intervals.size(); i++){
            //System.out.println("Will insert: " + nodes.get(i).interval); //DEBUG
            T.intervalInsert(nodes.get(i));
            //T.printTree(); //DEBUG: UNCOMMENT TO SEE THE TREE DURING CREATION
        }
        long endTime = System.currentTimeMillis();
        long totalTime = endTime - startTime;

        if (n <= 10){
            System.out.println("\nConstructed Interval Tree:");
            T.printTree(); 
        }

        System.out.println("- Construction time = " + totalTime);

        // ****************** TEST SEARCH
        startTime = System.currentTimeMillis();
        for (int i = 0; i < n; i++) {
            int c = rand.nextInt(cap);
            IntervalNode search = T.intervalSearch(c);
            
            //DEBUG
            //if (search != T.NIL) System.out.println("Searched with Integer: " + c + " and returned: "+ search.interval);
                
            boolean result = false;
            for (Interval in : intervals){
                if (T.overlaps(c, in)){
                    result = true;
                    break;
                }
            }
            if (search == T.NIL && result){
                System.out.println("ERROR:");
                System.out.println("- Missed search for value " + c);
            }
            else if (result && !T.overlaps(c, search.interval)){
                System.out.println("ERROR:");
                System.out.println("- Returned non-overlapping interval " + search.interval + " for " + c);
            }
            else if (search != T.NIL && !result){
                System.out.println("ERROR:");
                System.out.println("- Found non-existent interval");
            }
        }
        endTime = System.currentTimeMillis();
        totalTime = endTime - startTime;
        System.out.println("- Search time = " + totalTime);

        // ****************** TEST DELETION
        System.out.println("\n[*]     Testing deletions     [*]");
        System.out.println("=================================");
        startTime = System.currentTimeMillis();
        for (int i = 0; i < n; i++) {
            //System.out.println("Will delete: "+ nodes.get(i).interval); //DEBUG
            T.intervalDelete(nodes.get(i));
            //T.printTree(); //DEBUG: UNCOMMENT TO SEE THE TREE DURING DELETION
        }     
        endTime = System.currentTimeMillis();
        totalTime = endTime - startTime;

        System.out.println("Remains of Interval Tree:");
        T.printTree();
        System.out.println();

        System.out.println("- Deletion time = " + totalTime);

        // ****************** VERIFICATION: ALL NODES ARE DELETED
        boolean allDeleted = true;
        for (int i = 0; i < n; i++) {
            if (T.searchExactNode(nodes.get(i)) != T.NIL) {
                System.out.println("ERROR:");
                System.out.println("- Interval " + intervals.get(i) + " still found after deletion!");
                allDeleted = false;
            }
        }
        if (allDeleted) System.out.println("- All intervals deleted successfully");
        else System.out.println("- Some intervals still exist");
        System.out.println();
    }
}