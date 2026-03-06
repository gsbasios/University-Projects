# Data Structures: Advanced Tree Implementations

This repository contains Java implementations of advanced tree data structures. The project includes self-adjusting trees, multi-way search trees, and augmented trees for spatial reasoning

## Implemented Data Structures

### 1. Splay Tree
A self-balancing Binary Search Tree (BST) that moves frequently accessed elements closer to the root using the **splay** operation
- Supports rotations
- Optimized for scenarios with non-uniform access patterns

### 2. 2-4 Tree (Two-Four Tree)
A balanced multi-way search tree where every internal node has 2, 3, or 4 children.
- Implements bottom-up splitting for insertions
- Implements balance restoration through underflow handling during deletions
- Guaranteed $O(\log n)$ performance for search, insert, and delete

### 3. Interval Tree
A specialized Red-Black Tree (RBT) augmented to store intervals `[low, high]`
- Each node maintains a `max` value representing the highest endpoint in its subtree
- Optimized for finding overlapping intervals in $O(\log n)$ time
- Maintains strict Red-Black balancing properties to ensure logarithmic height


## Project Structure

- `CliMain.java`: The main entry point featuring a CLI menu
- `SplayTree.java`: Core implementation of the Splay Tree logic
- `TwoFourTree.java`: Core implementation of the 2-4 Tree logic
- `IntervalTree.java`: Core implementation of the Interval Tree logic

---

## Getting Started

### Prerequisites
- Java Development Kit (JDK) 8 or higher.

### Compilation
Compile all files using the following command:
```
javac *.java
```
You can run the program through the interactive Cli:
```
java CliMain.java
```
Also, each Tree can be run independently:
```
java SplayTree.java [int nodes, eg 1000]
```
