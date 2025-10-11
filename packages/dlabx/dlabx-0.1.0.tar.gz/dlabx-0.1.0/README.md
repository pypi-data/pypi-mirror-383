# DLab - Dhruv's Lab

🧠 DLabX - Dhruv's Lab – Learn, Build, and Master Algorithms

DLabX (Dhruv’s Lab) is a comprehensive Python library for algorithms and data structures.
It provides efficient and easy-to-use implementations for sorting, searching, dynamic programming, graph algorithms, backtracking, string matching, and more.

DLabXS is ideal for:

🎓 Students learning algorithms and data structures
🧩 Researchers and educators
⚡ Competitive programmers and developers

---

## 📑 Table of Contents

1. [Installation](#-installation)
2. [Usage](#-how-to-use-dlabx)
3. [Sorting Algorithms](#️-sorting-algorithms)
4. [Searching Algorithms](#-searching-algorithms)
5. [Greedy Algorithms](#-greedy-algorithms)
6. [Dynamic Programming](#-dynamic-programming)
7. [Backtracking](#️-backtracking-algorithms)
8. [Brute Force](#-brute-force-algorithms)
9. [Divide and Conquer](#-divide-and-conquer-algorithms)
10. [Data Structures](#-data-structures)
11. [String Matching](#-string-matching-algorithms)
12. [License](#-license)
13. [Author](#-author)


## Features

- Sorting Algorithms  
- Searching Algorithms  
- Greedy Algorithms  
- Dynamic Programming  
- Backtracking Algorithms  
- Brute-force Algorithms  
- Divide and Conquer Algorithms  
- Data Structures(arrays, stacks, queues, linked lists, trees, graphs)  
- String Matching Algorithms

---

## 🚀 Installation

pip install dlabx

# 🧩 How To Use Dlab: 

Import the library:  import dlabx as ds

# ⚙️ Sorting Algorithms Example
arr = [5, 2, 9, 1, 5]
sorted_arr = ds.Bubble_Sort(arr)
print("Bubble Sort:", sorted_arr)

ds.Bubble_Sort(arr)
ds.Selection_Sort(arr)
ds.Insertion_Sort(arr)
ds.Quick_Sort(arr)
ds.Merge_Sort(arr)
ds.Heap_Sort(arr)
ds.Counting_Sort(arr)
ds.Radix_Sort(arr)
ds.Shell_Sort(arr)
ds.Cocktail_Shaker_Sort(arr)
ds.Comb_Sort(arr)
ds.Gnome_Sort(arr)
ds.Cycle_Sort(arr)

# 🔍 Searching Algorithms Example
index = ds.Binary_Search([1,2,3,4,5], 3)
print("Binary Search:", index)

arr = [1, 2, 3, 4, 5, 6, 7]
target = 5

ds.Linear_Search(arr, target)
ds.Binary_Search(arr, target)
ds.Interpolation_Search(arr, target)
ds.Exponential_Search(arr, target)
ds.Jump_Search(arr, target)
ds.Ternary_Search(arr, target)
ds.Fibonacci_Search(arr, target)

# Graph Searches
g = ds.Graph(3)
g.add_edge(0, 1)
g.add_edge(1, 2)
ds.Bfs(g, 0)
ds.Dfs(g, 0)


# 💰  Greedy Algorithm Example

edges = [(0,1,10), (0,2,6), (1,2,5)]
mst = ds.Kruskal_Mst(3, edges)
print("Kruskal MST:", mst)

edges = [(0,1,10), (0,2,6), (1,2,5)]
ds.Kruskal_Mst(3, edges)

graph = [[0, 2, 0], [2, 0, 3], [0, 3, 0]]
ds.Prim_Mst(graph)

graph = [[0, 4, 0], [4, 0, 8], [0, 8, 0]]
ds.Dijkstra(graph, 0)

edges = [(0,1,4),(0,2,5),(1,2,-2)]
ds.Bellman_Ford(3, edges, 0)

values = [60, 100, 120]
weights = [10, 20, 30]
capacity = 50
ds.Fractional_Knapsack(values, weights, capacity)

# 🧮 Dynamic Programming

ds.Longest_Common_Subsequence("AGGTAB","GXTXAYB")

ds.Longest_Palindromic_Subsequence("abacdfgdcaba")

ds.Edit_Distance("kitten","sitting")

ds.Knapsack_01([60,100,120],[10,20,30],50)

ds.Unbounded_Knapsack([60,100,120],[10,20,30],50)

ds.Subset_Sum([3,34,4,12,5,2], 9)

ds.Can_Partition([1,5,11,5])

ds.Unique_Paths(3,7)

ds.Min_Path_Sum([[1,3,1],[1,5,1],[4,2,1]])

ds.Longest_Increasing_Path([[9,9,4],[6,6,8],[2,1,1]])

ds.Matrix_Chain_Order([10,20,30,40])

ds.Optimal_Bst([10,12,20], [34,8,50], 3)

ds.Catalan_Numbers(5)

ds.Bell_Numbers(5)

ds.Count_Paths([[0,0,0],[0,0,0]])

# ♟️ Backtracking Algorithms

ds.N_Queens(4)

ds.Sudoku([[5,3,0,0,7,0,0,0,0], ...])

ds.Maze([...])

ds.Generate_Permutations([1,2,3])

ds.Generate_Combinations([1,2,3],2)

ds.Subset_Sum([1,2,3,4],5)

ds.Knights_Tour(8)

ds.Exist_Word([...],"word")

ds.Hamiltonian_Path([...])

ds.Graph_Coloring([...],3)

ds.Partition_Array([...])

ds.K_Coloring([...],3)

ds.Sum_Of_Subsets([...],10)

ds.Generate_Power_Set([1,2,3])

ds.Partition_Into_K_Subsets([1,2,3,4],2)

# 🧠 Brute-force Algorithms

ds.Generate_Permutations([1,2,3])

ds.Generate_Subsets([1,2,3])

ds.Naive_Search("pattern","text")

ds.Distance([...])

ds.Tsp_Brute_Force([...])

ds.Knapsack_Bruteforce([...])

# ⚡ Divide and Conquer Algorithms

ds.Strassen_Matrix_Multiplication([[1,2],[3,4]], [[5,6],[7,8]])

ds.Closest_Pair_Of_Points([...])

ds.Fft([...])

ds.Karatsuba(1234,5678)

ds.Convex_Hull([...])

ds.Maximum_Subarray([...])

# 🧱 Data Structures

# Stack
stack = ds.Stack()
stack.push(10)
stack.pop()

# Queue
queue = ds.Queue()
queue.enqueue(1)
queue.dequeue()

# Linked Lists
sll = ds.SinglyLinkedList()
dll = ds.DoublyLinkedList()
cll = ds.CircularLinkedList()

# Trees
bst = ds.BinarySearchTree()
avl = ds.AVLTree()
rbt = ds.RedBlackTree()
trie = ds.Trie()
nary = ds.NAryTree()

# Graphs
graph = ds.Graph(3)
weighted = ds.WeightedGraph(3)
bipartite = ds.BipartiteGraph()

# 🔡 String Matching Algorithms

text = "ABABDABACDABABCABAB"
pattern = "ABABCABAB"

ds.Kmp_Search(text, pattern)

ds.Rabin_Karp_Search(text, pattern)

ds.Boyer_Moore_Search(text, pattern)

ds.Boyer_Moore_Horspool_Search(text, pattern)

ds.Ahocorasick_Search([...], pattern)

ds.Bitap_Search(text, pattern)

ds.Finite_Automaton_Search(text, pattern)

ds.Z_Array_Search(text, pattern)

ds.Suffix_Array_Search(text, pattern)

ds.Suffix_Automaton_Search(text, pattern)

ds.Suffix_Tree_Search(text, pattern)

ds.Streaming_Pattern_Matcher_Search(text, pattern)

ds.Sunday_Search(text, pattern)

ds.Wumanber_Search(text, pattern)



🧾 License
Licensed under the MIT License.

👨‍💻 Author
Dhruv Sonani
Creator of DLab - Dhruv’s Lab

📧 Email: dhruvsonani788@gmail.com
🌐 GitHub: https://github.com/dhruv-005









