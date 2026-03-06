import java.util.*;

public class TwoFourTree<Key extends Comparable<Key>, Item> {

    TreeNode root;        // root of tree

    class TreeNode {

        List<Key> keys;
        List<Item> items;
        List<TreeNode> children;
        TreeNode parent;    // node's parent
        int height;         // node's height

        TreeNode() {
            keys = new ArrayList<>();
            items = new ArrayList<>();
            children = new ArrayList<>();
            this.parent = null;
            this.height = 1;
        }

        @Override
        public String toString(){
            String keyStr = "[";
            for (int i = 0; i<keys.size(); i++){
                if (i < keys.size()-1) keyStr += keys.get(i)+",";
                else keyStr += keys.get(i)+"]";
            }
            return keyStr;
        }
    }

    //******************** HELPER METHODS */
    private TreeNode findNode(Key key) {
        TreeNode node = root;

        while (node != null) {

            boolean dived = false;
            for (int i = 0; i<node.keys.size(); i++) {
                int comp = key.compareTo(node.keys.get(i));

                if (comp == 0) {
                    return node;
                } else if (comp < 0) {
                    if (node.children.isEmpty()) return null;
                    node = node.children.get(i);
                    dived = true;
                    break;
                }
            }
            if (!dived) {
                if (node.children.isEmpty()) return null;
                node = node.children.get(node.keys.size());
            }
        }
        return null;
    }

    //split node with 4 keys (5 children)
    private void splitFiveNode(TreeNode node) {
        TreeNode x = new TreeNode(); //this is the new node

        //move largest key to new sibling
        x.keys.add(node.keys.remove(3));
        x.items.add(node.items.remove(3));

        //move 2 children if they exist, from old node to new sibling
        if (!node.children.isEmpty()) {
            TreeNode ch4 = node.children.remove(4);
            TreeNode ch3 = node.children.remove(3);

            // add to new node, x
            x.children.add(ch3);
            x.children.add(ch4);

            // update parent
            ch3.parent = x;
            ch4.parent = x;
        }

        //from now on, put the next key to the parent

        Key newKey = node.keys.remove(2);
        Item newItem = node.items.remove(2);
        TreeNode parent = node.parent;

        // if parent is null, make it the new root
        if (parent == null) {
            TreeNode r = new TreeNode();
            r.keys.add(newKey);
            r.items.add(newItem);
            r.children.add(node);
            r.children.add(x);

            node.parent = r;
            x.parent = r;
            root = r;
        }
        // parent exists
        else {
            int j = 0;
            // loop to find the correct position for the key
            while (j < parent.keys.size()) {
                if (newKey.compareTo(parent.keys.get(j)) < 0) break;
                j++;
            }
            
            // insert to parent
            parent.keys.add(j, newKey);
            parent.items.add(j, newItem);
            parent.children.add(j+1, x); // insert x as the right child of parent
            x.parent = parent;

            // recurse if needed
            if (parent.keys.size() == 4) splitFiveNode(parent);
        }
    }

    public int getTreeHeight(){
        if (root == null) return 0;

        int hght = 1;
        TreeNode node = root;
        while (!node.children.isEmpty()){
            hght++;
            node=node.children.get(0);
        }
        return hght;
    }

    //******************** CORE FUNCTIONS */
    // search for item with key
    public Item search(Key key) {
        TreeNode node = findNode(key);
        if (node == null) return null;

        for (int i = 0; i<node.keys.size(); i++) {
            if (key.compareTo(node.keys.get(i)) == 0) {
                return node.items.get(i);
            }
        }
        return null;
    }

    public void insert(Key key, Item item){
        if (root == null) {
            root = new TreeNode();
            root.keys.add(key);
            root.items.add(item);
            return;
        }

        TreeNode node = root;
        while (!node.children.isEmpty()) {
            boolean dived = false; // flag to check if we moved to child 

            for (int i=0; i<node.keys.size(); i++) {
                int comp = key.compareTo(node.keys.get(i));
                if (comp == 0) return;
                if (comp < 0) {
                    node = node.children.get(i);
                    dived = true;
                    break;
                }
            }
            //if inserted key is bigger than all the keys in node, go to the last child
            if (!dived) node = node.children.get(node.keys.size());
        }

        //insert key sorted
        int i = 0;
        while (i < node.keys.size()) {
            int comp = key.compareTo(node.keys.get(i));
            if (comp == 0) return;
            if (comp < 0) break;
            i++;
        }
        node.keys.add(i, key);
        node.items.add(i, item);

        if (node.keys.size() == 4) splitFiveNode(node);
    }

    public void delete(Key key) {
        //searching for node with key inside it
        TreeNode node = findNode(key);
        if (node == null) return;

        int index = -1;
        for (int i=0; i<node.keys.size(); i++){
            if (key.compareTo(node.keys.get(i)) == 0){
                index = i;
                break;
            }
        }

        //swap with successor
        if (!node.children.isEmpty()) {
            TreeNode successor = node.children.get(index + 1);
            while (!successor.children.isEmpty()) {
                successor = successor.children.get(0);
            }

            //swap values
            Key successorKey = successor.keys.get(0);
            Item successorItem = successor.items.get(0);

            successor.keys.set(0, key);
            successor.items.set(0, node.items.get(index));

            node.keys.set(index, successorKey);
            node.items.set(index, successorItem);

            node = successor;
            index = 0;
        }

        //remove from node X
        node.keys.remove(index);
        node.items.remove(index);

        //while node X is 1-node
        while (node.keys.isEmpty() && node != root) {
            TreeNode parent = node.parent;
            int i = 0;
            //find position of X in parent children list
            while (i < parent.children.size()) {
                if (parent.children.get(i) == node) break;
                i++;
            }

            //lend from left
            if (i > 0 && parent.children.get(i - 1).keys.size() > 1) {
                TreeNode leftBrother = parent.children.get(i - 1);
                
                //take parent's key down
                node.keys.add(0, parent.keys.get(i - 1));
                node.items.add(0, parent.items.get(i - 1));
                
                //move brother's key up
                parent.keys.set(i - 1, leftBrother.keys.remove(leftBrother.keys.size() - 1));
                parent.items.set(i - 1, leftBrother.items.remove(leftBrother.items.size() - 1));

                //move child
                if (!leftBrother.children.isEmpty()) {
                    TreeNode child = leftBrother.children.remove(leftBrother.children.size() - 1);
                    node.children.add(0, child);
                    child.parent = node;
                }
                return;
            }
            
            //lend from right
            else if (i < parent.children.size() - 1 && parent.children.get(i + 1).keys.size() > 1) {
                TreeNode rightBrother = parent.children.get(i + 1);
                
                //take parent's key down
                node.keys.add(parent.keys.get(i));
                node.items.add(parent.items.get(i));
                
                //move brother's key up
                parent.keys.set(i, rightBrother.keys.remove(0));
                parent.items.set(i, rightBrother.items.remove(0));

                //move child
                if (!rightBrother.children.isEmpty()) {
                    TreeNode child = rightBrother.children.remove(0);
                    node.children.add(child);
                    child.parent = node;
                }
                return;
            }

            //merge
            else {
                if (i > 0) {
                    //merge with left
                    TreeNode leftBrother = parent.children.get(i - 1);
                    
                    leftBrother.keys.add(parent.keys.remove(i - 1));
                    leftBrother.items.add(parent.items.remove(i - 1));
                    
                    //remove node X from parent
                    parent.children.remove(i);

                    //put all children in leftBrother
                    if (!node.children.isEmpty()) {
                        for (TreeNode c : node.children) {
                            leftBrother.children.add(c);
                            c.parent = leftBrother;
                        }
                    }
                    node = parent;

                } else {
                    //merge with left
                    TreeNode rightBrother = parent.children.get(i + 1);
                    
                    node.keys.add(parent.keys.remove(i));
                    node.items.add(parent.items.remove(i));
                    
                    //add all right's values in node 
                    node.keys.addAll(rightBrother.keys);
                    node.items.addAll(rightBrother.items);
                    
                    //put all children in node
                    if (!rightBrother.children.isEmpty()) {
                        for (TreeNode c : rightBrother.children) {
                            node.children.add(c);
                            c.parent = node;
                        }
                    }
                    
                    parent.children.remove(i + 1);
                    node = parent;
                }
            }
        }

        //check root
        if (root.keys.isEmpty()) {
            if (root.children.isEmpty()) {
                root = null;
            } else {
                root = root.children.get(0);
                root.parent = null;
            }
        }
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

        //just for allignement purposes
        int totalNodes = (int)(Math.pow(2, height));
        int nodeLength = 10;
        int betweenBros = 2; //for last level
        int betweenTrees = 1; //for last level
        int maxLength = (totalNodes*nodeLength) + (totalNodes*(betweenBros/2)) + (betweenTrees*(totalNodes-1));

        for (int i = 0; i < height; i++) {
            int fromSides = (maxLength/(int)(Math.pow(2, i+1))) - nodeLength/2;
            betweenBros = 2*fromSides;
            printSpaces(fromSides);

            List<TreeNode> nextLevel = new ArrayList<>();

            for (TreeNode node : currentLevel) {
                System.out.print(node);
                    
                nextLevel.addAll(node.children);

                //compare nodes biggest key with the biggest key of the parent
                int comp = 0;
                if (i > 1){
                    if (node.parent != null) comp = node.keys.get(node.keys.size()-1).compareTo(node.parent.keys.get(node.parent.keys.size()-1));
                    if (comp > 0) printSpaces(betweenBros*2 - nodeLength/2);
                    else printSpaces(betweenBros/2);
                }
                else printSpaces(betweenBros);
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
        System.out.println("\n[*]     Test TwoFour Tree     [*]");
        System.out.println("=================================");
        if (args.length == 0) {
            System.out.println("Usage: java TwoFourTree <n>");
            return;
        }

        int n = Integer.parseInt(args[0]);
        System.out.println("- Number of keys n = " + n);

        TwoFourTree<Integer, String> T = new TwoFourTree<Integer, String>();

        Random rand = new Random(0);
        int[] keys = new int[n];
        for (int i = 0; i < n; i++) { // store n random numbers in [0,2n)
            keys[i] = rand.nextInt(2 * n);
        }

        long startTime = System.currentTimeMillis();
        for (int i = 0; i < n; i++) {
            String item = "item" + i;
            T.insert(keys[i], item);
            //T.printTree(); //DEBUG: UNCOMMENT TO SEE THE TREE DURING CREATION
        }

        long endTime = System.currentTimeMillis();
        long totalTime = endTime - startTime;

        if (n <= 50){
            System.out.println("\nConstructed Two-Four Tree:");
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

        System.out.println("Remains of Two-Four Tree:");
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
        if (allDeleted) {
            System.out.println("- All keys deleted successfully");
        }
        System.out.println();
    }
    
}

