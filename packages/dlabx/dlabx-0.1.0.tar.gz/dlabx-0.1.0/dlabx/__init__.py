# Import submodules so they are accessible via dlabx.sorting, dlabx.searching, etc.
__version__ = "0.1.0"

# Sorting submodules
from .sorting.Bubble_Sort import Bubble_Sort
from .sorting.Selection_Sort import Selection_Sort
from .sorting.Insertion_Sort import Insertion_Sort
from .sorting.Quick_Sort import Quick_Sort
from .sorting.Counting_Sort import Counting_Sort
from .sorting.Radix_Sort import Radix_Sort
from .sorting.Counting_Sort_By_Digit import Counting_Sort_By_Digit
from .sorting.Heap_Sort import Heap_Sort
from .sorting.Merge_Sort import Merge_Sort
from .sorting.Shell_Sort import Shell_Sort
from .sorting.Cocktail_Shaker_Sort import Cocktail_Shaker_Sort
from .sorting.Comb_Sort import Comb_Sort
from .sorting.Gnome_Sort import Gnome_Sort
from .sorting.Cycle_Sort import Cycle_Sort

# Searching submodules
from .searching.Linear_Search import Linear_Search
from .searching.Binary_Search import Binary_Search
from .searching.Interpolation_Search import Interpolation_Search
from .searching.Exponential_Search import Exponential_Search
from .searching.Binary_Search_Range import Binary_Search_Range
from .searching.Jump_Search import Jump_Search
from .searching.Ternary_Search import Ternary_Search
from .searching.Fibonacci_Search import Fibonacci_Search
from .searching.Bfs import Bfs
from .searching.Dfs import Dfs

# Greedy algorithms
from .greedy.Kruskal_Mst import Kruskal_Mst
from .greedy.Prim_Mst import Prim_Mst
from .greedy.Dijkstra import Dijkstra
from .greedy.Bellman_Ford import Bellman_Ford
from .greedy.Activity_Selection import Activity_Selection
from .greedy.Job_Scheduling_Min_Lateness import Job_Scheduling_Min_Lateness
from .greedy.Huffman_Coding import Huffman_Coding
from .greedy.Fractional_Knapsack import Fractional_Knapsack
from .greedy.Greedy_Coloring import Greedy_Coloring
from .greedy.Greedy_Set_Cover import Greedy_Set_Cover
from .greedy.Interval_Scheduling import Interval_Scheduling
from .greedy.Coin_Change import Coin_Change

# Dynamic programming
from .dynamic_programming.Longest_Common_Subsequence import Longest_Common_Subsequence
from .dynamic_programming.Longest_Palindromic_Subsequence import Longest_Palindromic_Subsequence
from .dynamic_programming.Edit_Distance import Edit_Distance
from .dynamic_programming.Knapsack_01 import Knapsack_01
from .dynamic_programming.Unbounded_Knapsack import Unbounded_Knapsack
from .dynamic_programming.Subset_Sum import Subset_Sum
from .dynamic_programming.Can_Partition import Can_Partition
from .dynamic_programming.Unique_Paths import Unique_Paths
from .dynamic_programming.Min_Path_Sum import Min_Path_Sum
from .dynamic_programming.Longest_Increasing_Path import Longest_Increasing_Path
from .dynamic_programming.Matrix_Chain_Order import Matrix_Chain_Order
from .dynamic_programming.Optimal_Bst import Optimal_Bst
from .dynamic_programming.Catalan_Numbers import Catalan_Numbers
from .dynamic_programming.Bell_Numbers import Bell_Numbers
from .dynamic_programming.Count_Paths import Count_Paths

# Backtracking
from .backtracking.N_Queens import N_Queens
from .backtracking.Sudoku import Sudoku
from .backtracking.Maze import Maze
from .backtracking.Generate_Permutations import Generate_Permutations
from .backtracking.Generate_Combinations import Generate_Combinations
from .backtracking.Subset_Sum import Subset_Sum
from .backtracking.Knights_Tour import Knights_Tour
from .backtracking.Exist_Word import Exist_Word
from .backtracking.Hamiltonian_Path import Hamiltonian_Path
from .backtracking.Graph_Coloring import Graph_Coloring
from .backtracking.Partition_Array import Partition_Array
from .backtracking.K_Coloring import K_Coloring
from .backtracking.Sum_Of_Subsets import Sum_Of_Subsets
from .backtracking.Generate_Power_Set import Generate_Power_Set
from .backtracking.Partition_Into_K_Subsets import Partition_Into_K_Subsets

# Brute-force
from .bruteforce.Generate_Permutations import Generate_Permutations
from .bruteforce.Generate_Subsets import Generate_Subsets
from .bruteforce.Naive_Search import Naive_Search
from .bruteforce.Distance import Distance
from .bruteforce.Tsp_Brute_Force import Tsp_Brute_Force
from .bruteforce.Knapsack_Bruteforce import Knapsack_Bruteforce

# Divide and conquer
from .divide_and_conquer.Strassen_Matrix_Multiplication import Strassen_Matrix_Multiplication
from .divide_and_conquer.Closest_Pair_Of_Points import Closest_Pair_Of_Points
from .divide_and_conquer.Fft import Fft
from .divide_and_conquer.Karatsuba import Karatsuba
from .divide_and_conquer.Convex_Hull import Convex_Hull
from .divide_and_conquer.Maximum_Subarray import Maximum_Subarray

# Data Structures
from .data_structure.linear_data_structure.array import Array
from .data_structure.linear_data_structure.stack import Stack
from .data_structure.linear_data_structure.queue import Queue
from .data_structure.linear_data_structure.linked_list import (
    SinglyLinkedList,
    DoublyLinkedList,
    CircularLinkedList
)
from .data_structure.non_linear_data_structure.graph_representations import AdjacencyMatrix, AdjacencyList
from .data_structure.non_linear_data_structure.tree import (
    BinaryTree,
    BinarySearchTree,
    AVLTree,
    RedBlackTree,
    Trie,
    NAryTree
)
from .data_structure.non_linear_data_structure.graphs import (
    Graph,
    UndirectedGraph,
    DirectedGraph,
    WeightedGraph,
    BipartiteGraph
)

#String Matching
from .string_matching.Ahocorasick_Search import Ahocorasick_Search
from .string_matching.Bitap_Search import Bitap_Search
from .string_matching.Boyer_Moore_Search import Boyer_Moore_Search
from .string_matching.Boyer_Moore_Horspool_Search import Boyer_Moore_Horspool_Search
from .string_matching.Finite_Automaton_Search import Finite_Automaton_Search
from .string_matching.Kmp_Search import Kmp_Search
from .string_matching.Levenshtein_Distance_Search import Levenshtein_Distance_Search
from .string_matching.Naive_Search import Naive_Search
from .string_matching.Rabin_Karp_Search import Rabin_Karp_Search
from .string_matching.Streaming_Pattern_Matcher_Search import Streaming_Pattern_Matcher_Search
from .string_matching.Suffix_Array_Search import Suffix_Array_Search
from .string_matching.Suffix_Automaton_Search import Suffix_Automaton_Search
from .string_matching.Suffix_Tree_Search import Suffix_Tree_Search
from .string_matching.Sunday_Search import Sunday_Search
from .string_matching.Wumanber_Search import Wumanber_Search
from .string_matching.Z_Array_Search import Z_Array_Search



__all__ = [
    # Sorting algorithms
           'Bubble_Sort', 'Selection_Sort', 'Insertion_Sort', 'Quick_Sort', 
           'Counting_Sort', 'Radix_Sort', 'Counting_Sort_By_Digit', 'Heap_Sort', 
           'Merge_Sort', 'Shell_Sort', 'Cocktail_Shaker_Sort', 'Comb_Sort',
           'Gnome_Sort', 'Cycle_Sort',

    # Searching algorithms
            'Linear_Search', 'Binary_Search', 'Interpolation_Search', 
           'Exponential_Search', 'Binary_Search_Range', 'Jump_Search',
           'Ternary_Search', 'Fibonacci_Search', 'Bfs', 'Dfs',

    # Greedy algorithms
            'Kruskal_Mst', 'Prim_Mst', 'Dijkstra',
           'Bellman_Ford', 'Activity_Selection',
           'Job_Scheduling_Min_Lateness', 'Huffman_Coding',
           'Fractional_Knapsack', 'Greedy_Coloring', 
           'Greedy_Set_Cover', 'Interval_Scheduling', 
           'Coin_Change',

    # Dynamic programming
            'Longest_Common_Subsequence', 
           'Longest_Palindromic_Subsequence',
           'Edit_Distance', 'Knapsack_01', 
           'Unbounded_Knapsack', 'Subset_Sum',
           'Can_Partition', 'Unique_Paths',
           'Min_Path_Sum', 'Longest_Increasing_Path',
           'Matrix_Chain_Order', 'Optimal_Bst',
           'Catalan_Numbers', 'Bell_Numbers',
           'Count_Paths',

    # Backtracking
           'N_Queens', 'Sudoku', 'Maze',
           'Generate_Permutations',
           'Generate_Combinations',
           'Subset_Sum', 'Knights_Tour',
           'Exist_Word','Hamiltonian_Path',
           'Graph_Coloring', 'Partition_Array',
           'K_Coloring', 'Sum_Of_Subsets',
           'Generate_Power_Set',
           'Partition_Into_K_Subsets',

    # Brute-force
            'Generate_Permutations','Generate_Subsets',
           'Naive_Search', 'Distance', 'Tsp_Brute_Force',
           'Knapsack_Bruteforce',

    # Divide and conquer
            'Strassen_Matrix_Multiplication',
           'Closest_Pair_Of_Points', 'Fft',
           'Karatsuba', 'Convex_Hull',
           'Maximum_Subarray',

    # Data Structures
    'Array', 'Stack', 'Queue', 'SinglyLinkedList', 'DoublyLinkedList', 'CircularLinkedList',
    'AdjacencyMatrix', 'AdjacencyList',
    'BinaryTree', 'BinarySearchTree', 'AVLTree', 'RedBlackTree', 'Trie', 'NAryTree',
    'Graph', 'UndirectedGraph', 'DirectedGraph', 'WeightedGraph', 'BipartiteGraph',

    #String Matching

        'Ahocorasick_Search','Bitap_Search',
        'Boyer_Moore_Horspool_Search','Boyer_Moore_Search',
        'Finite_Automaton_Search','Kmp_Search',
        'Levenshtein_Distance_Search','Naive_Search',
        'Rabin_Karp_Search','Streaming_Pattern_Matcher_Search',
        'Suffix_Array_Search','Suffix_Automaton_Search',
        'Suffix_Tree_Search','Suffix_Tries_Search',
        'Sunday_Search','Wumanber_Search','Z_Array_Search'
]
