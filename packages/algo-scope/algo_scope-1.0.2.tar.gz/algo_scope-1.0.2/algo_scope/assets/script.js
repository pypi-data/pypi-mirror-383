// Algo Scope - Full script.js (single file)
// Uses the SAME behavior and design as the original inline <script> in index.html.
// - Renders categories and algorithms dynamically
// - Clicking an algorithm shows its Python code in #codeDisplay and reveals #codeBlock

// ----------------------------
// Categories and algorithms
// ----------------------------
const data = {
  "Arrays & Strings": [
    "Linear Search", "Binary Search", "Ternary Search",
    "Bubble Sort", "Selection Sort", "Insertion Sort", "Merge Sort",
    "Quick Sort", "Counting Sort", "Radix Sort", "Bucket Sort",
    "Max Sum Subarray of Size K", "Longest Substring with K Distinct Characters",
    "Prefix Sum Array", "Difference Array", "Kadane’s Algorithm",
    "Spiral Matrix", "Rotate Matrix", "Search in 2D Matrix I & II",
    "Transpose Matrix", "Sort Colors", "Trapping Rain Water", "Container with Most Water",
    "Jump Game", "Minimum Platforms", "Naive Pattern Search", "KMP Algorithm",
    "Rabin-Karp Algorithm", "Z-Algorithm"
  ],
  "Linked Lists": [
    "Singly Linked List Operations", "Doubly Linked List Operations",
    "Circular Linked List", "Reverse Linked List",
    "Detect and Remove Loop", "Merge Two Sorted Lists",
    "Add Two Numbers", "Copy List with Random Pointer", "LRU Cache",
    "Intersection of Two LLs", "Sort LL using Merge Sort"
  ],
  "Stack & Queue": [
    "Implement Stack", "Stack using Two Queues", "Queue using Two Stacks",
    "Balanced Parentheses", "Next Greater Element", "Daily Temperatures",
    "Min Stack", "Infix to Postfix", "Evaluate Postfix", "Monotonic Stack",
    "Sliding Window Maximum"
  ],
  "Recursion & Backtracking": [
    "Tower of Hanoi", "Subsets", "Permutations", "Combination Sum",
    "Palindrome Partitioning", "Word Search", "N-Queens", "Sudoku Solver",
    "Generate Parentheses", "Rat in a Maze", "Letter Combinations of Phone Number"
  ],
  "Binary Trees": [
    "Tree Traversals", "Views (Top/Bottom/Side)", "Height/Depth",
    "Diameter of Binary Tree", "Balanced Tree", "Mirror Tree", "Build Tree",
    "Serialize/Deserialize", "Boundary Traversal", "Burn Tree", "LCA",
    "Flatten Binary Tree", "Vertical Order Traversal"
  ],
  "Binary Search Trees (BST)": [
    "Search/Insert/Delete", "Validate BST", "Kth Smallest/Largest",
    "LCA in BST", "Convert to BST", "Two Sum in BST", "Recover BST",
    "BST Iterator", "Merge Two BSTs", "Predecessor & Successor"
  ],
  "Heap / Priority Queue": [
    "Heapify", "Insert/Delete", "Kth Largest/Smallest",
    "Top K Frequent", "Median of Stream", "Sliding Window Median",
    "Reorganize String", "Sort K-Sorted Array"
  ],
  "Graphs": [
    "Adjacency List/Matrix", "Edge List", "BFS", "DFS", "Dijkstra's", "Bellman-Ford",
    "Floyd-Warshall", "A* Search", "Cycle Detection", "Topological Sort", "0-1 BFS",
    "Prim's", "Kruskal's", "Union-Find", "Kosaraju", "Tarjan", "Bridges", "Eulerian Path",
    "Detect Bipartite Graph"
  ],
  "Dynamic Programming": [
    "Fibonacci", "Climbing Stairs", "House Robber", "Jump Game",
    "Maximum Product Subarray", "Unique Paths", "Minimum Path Sum",
    "Maximum Square Sub-matrix", "Cherry Pickup", "Dungeon Game",
    "LCS", "LIS", "LPS", "Edit Distance", "Wildcard Matching",
    "Subset Sum", "Target Sum", "Palindrome Partitioning II",
    "0/1 Knapsack", "Unbounded Knapsack", "Rod Cutting",
    "Coin Change", "House Robber III", "TSP", "Assignment Problem"
  ],
  "Trie": [
    "Insert/Search/Delete", "StartsWith", "Word Search II", "Longest Word with Prefixes",
    "Replace Words", "Auto-complete", "Maximum XOR Pair", "XOR Trie Queries"
  ],
  "Segment Tree & BIT": [
    "Range Sum Query", "Min/Max Query", "Lazy Propagation",
    "Point Update", "Inversion Count", "2D BIT"
  ],
  "Bit Manipulation": [
    "Set Bits", "Power of Two", "XOR", "Missing Number",
    "Duplicate Number", "Single Number", "Bitmask Subsets", "Sum of XORs",
    "Swap/Toggle Bits"
  ],
  "Math & Number Theory": [
    "GCD/LCM", "Sieve of Eratosthenes", "Prime Factorization",
    "Modular Exponentiation", "Modular Inverse", "Fast Power",
    "nCr / Pascal's Triangle", "Matrix Exponentiation", "Trailing Zeros",
    "Armstrong Number", "Perfect Number"
  ],
  "Miscellaneous": [
    "Reservoir Sampling", "KMP", "Rabin-Karp", "Z-Algorithm",
    "Manacher’s Algorithm", "Union-Find Rollback", "Mo’s Algorithm",
    "Centroid Decomposition", "Convex Hull"
  ]
};

const codeSamples = {
 "Linear Search": `def linear_search(arr, target):
for i in range(len(arr)):
    if arr[i] == target:
        return i
return -1`,
"Binary Search": `def binary_search(arr, target):
left, right = 0, len(arr) - 1
while left <= right:
    mid = (left + right) // 2
    if arr[mid] == target:
        return mid
    elif arr[mid] < target:
        left = mid + 1
    else:
        right = mid - 1
return -1`,
"Ternary Search": `def ternary_search(arr, target):
left, right = 0, len(arr) - 1
while left <= right:
    mid1 = left + (right - left) // 3
    mid2 = right - (right - left) // 3
    if arr[mid1] == target:
        return mid1
    if arr[mid2] == target:
        return mid2
    if target < arr[mid1]:
        right = mid1 - 1
    elif target > arr[mid2]:
        left = mid2 + 1
    else:
        left = mid1 + 1
        right = mid2 - 1
return -1`,
"Bubble Sort": `def bubble_sort(arr):
n = len(arr)
for i in range(n):
  for j in range(0, n-i-1):
      if arr[j] > arr[j+1]:
          arr[j], arr[j+1] = arr[j+1], arr[j]
return arr`,
"Selection Sort": `def selection_sort(arr):
n = len(arr)
for i in range(n):
    min_idx = i
    for j in range(i+1, n):
        if arr[j] < arr[min_idx]:
            min_idx = j
    arr[i], arr[min_idx] = arr[min_idx], arr[i]
return arr`,

"Insertion Sort": `def insertion_sort(arr):
for i in range(1, len(arr)):
    key = arr[i]
    j = i - 1
    while j >= 0 and arr[j] > key:
        arr[j + 1] = arr[j]
        j -= 1
    arr[j + 1] = key
return arr`,
// 👇 New
"Merge Sort": `def merge_sort(arr):
if len(arr) > 1:
    mid = len(arr) // 2
    L = arr[:mid]
    R = arr[mid:]

    merge_sort(L)
    merge_sort(R)

    i = j = k = 0
    while i < len(L) and j < len(R):
        if L[i] < R[j]:
            arr[k] = L[i]
            i += 1
        else:
            arr[k] = R[j]
            j += 1
        k += 1

    while i < len(L):
        arr[k] = L[i]
        i += 1
        k += 1

    while j < len(R):
        arr[k] = R[j]
        j += 1
        k += 1
return arr`,

"Quick Sort": `def quick_sort(arr):
if len(arr) <= 1:
    return arr
pivot = arr[len(arr) // 2]
left = [x for x in arr if x < pivot]
middle = [x for x in arr if x == pivot]
right = [x for x in arr if x > pivot]
return quick_sort(left) + middle + quick_sort(right)`,

"Counting Sort": `def counting_sort(arr):
if not arr:
    return []
max_val = max(arr)
count = [0] * (max_val + 1)
for num in arr:
    count[num] += 1
output = []
for i in range(len(count)):
    output.extend([i] * count[i])
return output`,
 // 👇 New additions:
  "Radix Sort": `def counting_sort_exp(arr, exp):
n = len(arr)
output = [0] * n
count = [0] * 10

for i in range(n):
    index = (arr[i] // exp) % 10
    count[index] += 1

for i in range(1, 10):
    count[i] += count[i - 1]

i = n - 1
while i >= 0:
    index = (arr[i] // exp) % 10
    output[count[index] - 1] = arr[i]
    count[index] -= 1
    i -= 1

for i in range(n):
    arr[i] = output[i]

def radix_sort(arr):
if len(arr) == 0:
    return arr
max_num = max(arr)
exp = 1
while max_num // exp > 0:
    counting_sort_exp(arr, exp)
    exp *= 10
return arr`,

"Bucket Sort": `def bucket_sort(arr):
if len(arr) == 0:
    return arr
bucket_count = 10
max_val, min_val = max(arr), min(arr)
bucket_range = (max_val - min_val) / bucket_count
buckets = [[] for _ in range(bucket_count)]

for num in arr:
    index = int((num - min_val) / bucket_range)
    if index == bucket_count:
        index -= 1
    buckets[index].append(num)

sorted_arr = []
for bucket in buckets:
    sorted_arr.extend(sorted(bucket))
return sorted_arr`,

"Max Sum Subarray of Size K": `def max_sum_subarray_k(arr, k):
if not arr or k <= 0 or k > len(arr):
    return 0
window_sum = sum(arr[:k])
max_sum = window_sum
for i in range(k, len(arr)):
    window_sum += arr[i] - arr[i - k]
    max_sum = max(max_sum, window_sum)
return max_sum`,
 // 👇 New additions:
  "Longest Substring with K Distinct Characters": `def longest_substring_k_distinct(s, k):
from collections import defaultdict
if k == 0:
    return 0

left = 0
max_len = 0
char_count = defaultdict(int)

for right in range(len(s)):
    char_count[s[right]] += 1

    while len(char_count) > k:
        char_count[s[left]] -= 1
        if char_count[s[left]] == 0:
            del char_count[s[left]]
        left += 1

    max_len = max(max_len, right - left + 1)

return max_len`,

"Prefix Sum Array": `def prefix_sum_array(arr):
prefix = [0] * len(arr)
prefix[0] = arr[0]
for i in range(1, len(arr)):
    prefix[i] = prefix[i - 1] + arr[i]
return prefix`,

"Difference Array": `def create_diff_array(arr):
n = len(arr)
diff = [0] * (n + 1)
diff[0] = arr[0]
for i in range(1, n):
    diff[i] = arr[i] - arr[i - 1]
return diff

def apply_range_update(diff, l, r, val):
diff[l] += val
if r + 1 < len(diff):
    diff[r + 1] -= val

def final_array_from_diff(diff):
res = [0] * (len(diff) - 1)
res[0] = diff[0]
for i in range(1, len(res)):
    res[i] = res[i - 1] + diff[i]
return res`,
 // 👇 New additions:
"Kadane’s Algorithm": `def kadanes_algorithm(nums):
max_sum = curr_sum = nums[0]
for num in nums[1:]:
    curr_sum = max(num, curr_sum + num)
    max_sum = max(max_sum, curr_sum)
return max_sum`,

"Spiral Matrix": `def spiral_order(matrix):
res = []
if not matrix:
    return res
top, bottom = 0, len(matrix)-1
left, right = 0, len(matrix[0])-1

while top <= bottom and left <= right:
    for i in range(left, right+1):
        res.append(matrix[top][i])
    top += 1

    for i in range(top, bottom+1):
        res.append(matrix[i][right])
    right -= 1

    if top <= bottom:
        for i in range(right, left-1, -1):
            res.append(matrix[bottom][i])
        bottom -= 1

    if left <= right:
        for i in range(bottom, top-1, -1):
            res.append(matrix[i][left])
        left += 1
return res`,

"Rotate Matrix": `def rotate_matrix(matrix):
n = len(matrix)
for i in range(n):
    for j in range(i, n):
        matrix[i][j], matrix[j][i] = matrix[j][i], matrix[i][j]
for row in matrix:
    row.reverse()
return matrix`,
 // 👇 New additions:
  "Search in 2D Matrix I & II": `def search_matrix(matrix, target):
if not matrix or not matrix[0]:
    return False
row, col = 0, len(matrix[0]) - 1
while row < len(matrix) and col >= 0:
    if matrix[row][col] == target:
        return True
    elif matrix[row][col] > target:
        col -= 1
    else:
        row += 1
return False`,

"Transpose Matrix": `def transpose_matrix(matrix):
return [list(row) for row in zip(*matrix)]`,

"Sort Colors": `def sort_colors(nums):
low, mid, high = 0, 0, len(nums) - 1
while mid <= high:
    if nums[mid] == 0:
        nums[low], nums[mid] = nums[mid], nums[low]
        low += 1
        mid += 1
    elif nums[mid] == 1:
        mid += 1
    else:
        nums[mid], nums[high] = nums[high], nums[mid]
        high -= 1
return nums`,
 // 👇 New additions:
  "Trapping Rain Water": `def trap(height):
left, right = 0, len(height) - 1
left_max = right_max = 0
water = 0
while left < right:
    if height[left] < height[right]:
        left_max = max(left_max, height[left])
        water += left_max - height[left]
        left += 1
    else:
        right_max = max(right_max, height[right])
        water += right_max - height[right]
        right -= 1
return water`,

"Container with Most Water": `def max_area(height):
left, right = 0, len(height) - 1
max_water = 0
while left < right:
    max_water = max(max_water, min(height[left], height[right]) * (right - left))
    if height[left] < height[right]:
        left += 1
    else:
        right -= 1
return max_water`,

"Jump Game": `def can_jump(nums):
max_reach = 0
for i, num in enumerate(nums):
    if i > max_reach:
        return False
    max_reach = max(max_reach, i + num)
return True`,
 // 👇 New additions:
   "Minimum Platforms": `def find_platforms(arr, dep):
arr.sort()
dep.sort()
platform_needed = 1
result = 1
i = 1
j = 0
n = len(arr)
while i < n and j < n:
    if arr[i] <= dep[j]:
        platform_needed += 1
        i += 1
    elif arr[i] > dep[j]:
        platform_needed -= 1
        j += 1
    result = max(result, platform_needed)
return result`,

"Naive Pattern Search": `def naive_search(text, pattern):
n = len(text)
m = len(pattern)
for i in range(n - m + 1):
    if text[i:i+m] == pattern:
        print(f"Pattern found at index {i}")`,

"KMP Algorithm": `def kmp_search(text, pattern):
def compute_lps(pattern):
    lps = [0] * len(pattern)
    length = 0
    i = 1
    while i < len(pattern):
        if pattern[i] == pattern[length]:
            length += 1
            lps[i] = length
            i += 1
        else:
            if length != 0:
                length = lps[length - 1]
            else:
                lps[i] = 0
                i += 1
    return lps

lps = compute_lps(pattern)
i = j = 0
while i < len(text):
    if pattern[j] == text[i]:
        i += 1
        j += 1
    if j == len(pattern):
        print(f"Pattern found at index {i - j}")
        j = lps[j - 1]
    elif i < len(text) and pattern[j] != text[i]:
        if j != 0:
            j = lps[j - 1]
        else:
            i += 1`,
 // 👇 New additions:
   "Rabin-Karp Algorithm": `def rabin_karp(text, pattern, d=256, q=101):
n = len(text)
m = len(pattern)
h = pow(d, m-1) % q
p = 0  # hash for pattern
t = 0  # hash for text

for i in range(m):
    p = (d * p + ord(pattern[i])) % q
    t = (d * t + ord(text[i])) % q

for s in range(n - m + 1):
    if p == t:
        if text[s:s+m] == pattern:
            print(f"Pattern found at index {s}")
    if s < n - m:
        t = (d * (t - ord(text[s]) * h) + ord(text[s + m])) % q
        if t < 0:
            t += q`,

"Z-Algorithm": `def z_algorithm(s):
n = len(s)
z = [0] * n
l, r = 0, 0
for i in range(1, n):
    if i <= r:
        z[i] = min(r - i + 1, z[i - l])
    while i + z[i] < n and s[z[i]] == s[i + z[i]]:
        z[i] += 1
    if i + z[i] - 1 > r:
        l, r = i, i + z[i] - 1
return z`,
 // 👇 New additions:
"Singly Linked List Operations" : `class Node:
def __init__(self, data):
    self.data = data
    self.next = None

class SinglyLinkedList:
def __init__(self):
    self.head = None

def insert_at_end(self, data):
    new_node = Node(data)
    if not self.head:
        self.head = new_node
        return
    temp = self.head
    while temp.next:
        temp = temp.next
    temp.next = new_node

def delete_node(self, key):
    temp = self.head
    if temp and temp.data == key:
        self.head = temp.next
        return
    prev = None
    while temp and temp.data != key:
        prev = temp
        temp = temp.next
    if temp:
        prev.next = temp.next

def display(self):
    temp = self.head
    while temp:
        print(temp.data, end=" -> ")
        temp = temp.next
    print("None")
`,
"Doubly Linked List Operations": `class Node:
def __init__(self, data):
    self.data = data
    self.prev = None
    self.next = None

class DoublyLinkedList:
def __init__(self):
    self.head = None

def insert_at_end(self, data):
    new_node = Node(data)
    if not self.head:
        self.head = new_node
        return
    temp = self.head
    while temp.next:
        temp = temp.next
    temp.next = new_node
    new_node.prev = temp

def delete_node(self, key):
    temp = self.head
    while temp and temp.data != key:
        temp = temp.next
    if not temp:
        return
    if temp.prev:
        temp.prev.next = temp.next
    if temp.next:
        temp.next.prev = temp.prev
    if temp == self.head:
        self.head = temp.next

def display(self):
    temp = self.head
    while temp:
        print(temp.data, end=" <-> ")
        temp = temp.next
    print("None")
`,
"Circular Linked List": `class Node:
def __init__(self, data):
    self.data = data
    self.next = None

class CircularLinkedList:
def __init__(self):
    self.head = None

def insert(self, data):
    new_node = Node(data)
    if not self.head:
        self.head = new_node
        new_node.next = self.head
        return
    temp = self.head
    while temp.next != self.head:
        temp = temp.next
    temp.next = new_node
    new_node.next = self.head

def display(self):
    if not self.head:
        return
    temp = self.head
    while True:
        print(temp.data, end=" -> ")
        temp = temp.next
        if temp == self.head:
            break
    print("(back to head)")
`,
"Reverse Linked List": `class Node:
def __init__(self, data):
    self.data = data
    self.next = None

def reverse_linked_list(head):
prev = None
current = head
while current:
    next_node = current.next
    current.next = prev
    prev = current
    current = next_node
return prev`,

"Detect and Remove Loop": `class Node:
def __init__(self, data):
    self.data = data
    self.next = None

def detect_and_remove_loop(head):
slow = head
fast = head
while fast and fast.next:
    slow = slow.next
    fast = fast.next.next
    if slow == fast:
        break
else:
    return  # No loop found

slow = head
if slow == fast:
    while fast.next != slow:
        fast = fast.next
else:
    while slow.next != fast.next:
        slow = slow.next
        fast = fast.next
fast.next = None`,

"Merge Two Sorted Lists": `class Node:
def __init__(self, data):
    self.data = data
    self.next = None

def merge_sorted_lists(l1, l2):
dummy = Node(0)
tail = dummy
while l1 and l2:
    if l1.data < l2.data:
        tail.next = l1
        l1 = l1.next
    else:
        tail.next = l2
        l2 = l2.next
    tail = tail.next
tail.next = l1 or l2
return dummy.next`,
"Add Two Numbers": `class Node:
def __init__(self, data):
  self.data = data
  self.next = None

def add_two_numbers(l1, l2):
  dummy = Node(0)
  current = dummy
  carry = 0
  while l1 or l2 or carry:
      val1 = l1.data if l1 else 0
      val2 = l2.data if l2 else 0
      total = val1 + val2 + carry
      carry = total // 10
      current.next = Node(total % 10)
      current = current.next
      if l1: l1 = l1.next
      if l2: l2 = l2.next
  return dummy.next`,

"Copy List with Random Pointer": `class Node:
def __init__(self, val, next=None, random=None):
    self.val = val
    self.next = next
    self.random = random

def copy_random_list(head):
if not head:
    return None

old_to_new = {}
current = head

while current:
    old_to_new[current] = Node(current.val)
    current = current.next

current = head
while current:
    copy = old_to_new[current]
    copy.next = old_to_new.get(current.next)
    copy.random = old_to_new.get(current.random)
    current = current.next

return old_to_new[head]`,

"LRU Cache": `from collections import OrderedDict

class LRUCache:
def __init__(self, capacity):
    self.cache = OrderedDict()
    self.capacity = capacity

def get(self, key):
    if key in self.cache:
        self.cache.move_to_end(key)
        return self.cache[key]
    return -1

def put(self, key, value):
    if key in self.cache:
        self.cache.move_to_end(key)
    self.cache[key] = value
    if len(self.cache) > self.capacity:
        self.cache.popitem(last=False)`,
        "Intersection of Two LLs": `class Node:
def __init__(self, data):
    self.data = data
    self.next = None

def get_intersection_node(headA, headB):
if not headA or not headB:
    return None

a, b = headA, headB
while a != b:
    a = a.next if a else headB
    b = b.next if b else headA
return a`,

"Sort LL using Merge Sort": `class Node:
def __init__(self, data):
    self.data = data
    self.next = None

def merge_sort(head):
if not head or not head.next:
    return head

def get_middle(node):
    slow = fast = node
    prev = None
    while fast and fast.next:
        prev = slow
        slow = slow.next
        fast = fast.next.next
    if prev:
        prev.next = None
    return slow

def merge(l1, l2):
    dummy = Node(0)
    tail = dummy
    while l1 and l2:
        if l1.data < l2.data:
            tail.next, l1 = l1, l1.next
        else:
            tail.next, l2 = l2, l2.next
        tail = tail.next
    tail.next = l1 or l2
    return dummy.next

mid = get_middle(head)
left = merge_sort(head)
right = merge_sort(mid)
return merge(left, right)`,
"Implement Stack": `class Stack:
def __init__(self):
    self.stack = []

def push(self, data):
    self.stack.append(data)

def pop(self):
    if self.stack:
        return self.stack.pop()
    return None

def peek(self):
    if self.stack:
        return self.stack[-1]
    return None

def is_empty(self):
    return len(self.stack) == 0`,

"Stack using Two Queues": `from collections import deque

class Stack:
def __init__(self):
    self.q1 = deque()
    self.q2 = deque()

def push(self, x):
    self.q2.append(x)
    while self.q1:
        self.q2.append(self.q1.popleft())
    self.q1, self.q2 = self.q2, self.q1

def pop(self):
    if self.q1:
        return self.q1.popleft()
    return None

def top(self):
    if self.q1:
        return self.q1[0]
    return None

def is_empty(self):
    return not self.q1`,

"Queue using Two Stacks": `class Queue:
def __init__(self):
    self.s1 = []
    self.s2 = []

def enqueue(self, x):
    self.s1.append(x)

def dequeue(self):
    if not self.s2:
        while self.s1:
            self.s2.append(self.s1.pop())
    if self.s2:
        return self.s2.pop()
    return None`,

"Balanced Parentheses": `def is_balanced(expr):
stack = []
mapping = {')': '(', ']': '[', '}': '{'}
for char in expr:
    if char in mapping.values():
        stack.append(char)
    elif char in mapping:
        if not stack or mapping[char] != stack.pop():
            return False
return not stack`,
"Next Greater Element": `def next_greater_element(arr):
stack = []
result = [-1] * len(arr)
for i in range(len(arr)-1, -1, -1):
    while stack and stack[-1] <= arr[i]:
        stack.pop()
    if stack:
        result[i] = stack[-1]
    stack.append(arr[i])
return result`,

"Daily Temperatures": `def daily_temperatures(temps):
result = [0] * len(temps)
stack = []
for i in range(len(temps)):
    while stack and temps[i] > temps[stack[-1]]:
        prev_day = stack.pop()
        result[prev_day] = i - prev_day
    stack.append(i)
return result`,

"Min Stack": `class MinStack:
def __init__(self):
    self.stack = []
    self.min_stack = []

def push(self, val):
    self.stack.append(val)
    if not self.min_stack or val <= self.min_stack[-1]:
        self.min_stack.append(val)

def pop(self):
    if self.stack:
        val = self.stack.pop()
        if val == self.min_stack[-1]:
            self.min_stack.pop()

def top(self):
    if self.stack:
        return self.stack[-1]
    return None

def get_min(self):
    if self.min_stack:
        return self.min_stack[-1]
    return None`,

"Infix to Postfix": `def infix_to_postfix(expression):
precedence = {'+':1, '-':1, '*':2, '/':2, '^':3}
stack = []
output = ''
for char in expression:
    if char.isalnum():
        output += char
    elif char == '(':
        stack.append(char)
    elif char == ')':
        while stack and stack[-1] != '(':
            output += stack.pop()
        stack.pop()
    else:
        while stack and stack[-1] != '(' and precedence[char] <= precedence[stack[-1]]:
            output += stack.pop()
        stack.append(char)
while stack:
    output += stack.pop()
return output`,
"Evaluate Postfix": `def evaluate_postfix(expression):
stack = []
for char in expression.split():
    if char.isdigit():
        stack.append(int(char))
    else:
        b = stack.pop()
        a = stack.pop()
        if char == '+':
            stack.append(a + b)
        elif char == '-':
            stack.append(a - b)
        elif char == '*':
            stack.append(a * b)
        elif char == '/':
            stack.append(int(a / b))  # int() for floor division
return stack[0]`,

"Monotonic Stack": `def monotonic_stack(arr):
inc_stack = []
dec_stack = []
for num in arr:
    while inc_stack and num < inc_stack[-1]:
        inc_stack.pop()
    inc_stack.append(num)

    while dec_stack and num > dec_stack[-1]:
        dec_stack.pop()
    dec_stack.append(num)
return inc_stack, dec_stack`,

"Sliding Window Maximum": `from collections import deque

def sliding_window_max(nums, k):
result = []
dq = deque()
for i in range(len(nums)):
    while dq and dq[0] <= i - k:
        dq.popleft()
    while dq and nums[i] >= nums[dq[-1]]:
        dq.pop()
    dq.append(i)
    if i >= k - 1:
        result.append(nums[dq[0]])
return result`,
"Tower of Hanoi": `def tower_of_hanoi(n, source, target, auxiliary):
if n == 1:
    print(f"Move disk 1 from {source} to {target}")
    return
tower_of_hanoi(n-1, source, auxiliary, target)
print(f"Move disk {n} from {source} to {target}")
tower_of_hanoi(n-1, auxiliary, target, source)`,

"Subsets": `def subsets(nums):
result = []
def backtrack(start, path):
    result.append(path[:])
    for i in range(start, len(nums)):
        path.append(nums[i])
        backtrack(i + 1, path)
        path.pop()
backtrack(0, [])
return result`,

"Permutations": `def permutations(nums):
result = []
def backtrack(path, used):
    if len(path) == len(nums):
        result.append(path[:])
        return
    for i in range(len(nums)):
        if not used[i]:
            used[i] = True
            path.append(nums[i])
            backtrack(path, used)
            path.pop()
            used[i] = False
backtrack([], [False]*len(nums))
return result`,

"Combination Sum": `def combination_sum(candidates, target):
result = []
def backtrack(start, path, total):
    if total == target:
        result.append(path[:])
        return
    if total > target:
        return
    for i in range(start, len(candidates)):
        path.append(candidates[i])
        backtrack(i, path, total + candidates[i])
        path.pop()
backtrack(0, [], 0)
return result`,
"Palindrome Partitioning": `def partition(s):
result = []
def is_palindrome(sub):
    return sub == sub[::-1]
def backtrack(start, path):
    if start == len(s):
        result.append(path[:])
        return
    for end in range(start + 1, len(s) + 1):
        if is_palindrome(s[start:end]):
            path.append(s[start:end])
            backtrack(end, path)
            path.pop()
backtrack(0, [])
return result`,

"Word Search": `def exist(board, word):
rows, cols = len(board), len(board[0])
visited = [[False]*cols for _ in range(rows)]

def dfs(r, c, i):
    if i == len(word):
        return True
    if r < 0 or r >= rows or c < 0 or c >= cols:
        return False
    if visited[r][c] or board[r][c] != word[i]:
        return False

    visited[r][c] = True
    res = (dfs(r+1, c, i+1) or dfs(r-1, c, i+1) or
           dfs(r, c+1, i+1) or dfs(r, c-1, i+1))
    visited[r][c] = False
    return res

for i in range(rows):
    for j in range(cols):
        if dfs(i, j, 0):
            return True
return False`,

"N-Queens": `def solve_n_queens(n):
result = []
board = [["."]*n for _ in range(n)]

def is_safe(row, col):
    for i in range(row):
        if board[i][col] == "Q":
            return False
        if col - (row - i) >= 0 and board[i][col - (row - i)] == "Q":
            return False
        if col + (row - i) < n and board[i][col + (row - i)] == "Q":
            return False
    return True

def backtrack(row):
    if row == n:
        result.append(["".join(r) for r in board])
        return
    for col in range(n):
        if is_safe(row, col):
            board[row][col] = "Q"
            backtrack(row + 1)
            board[row][col] = "."
backtrack(0)
return result`,

"Sudoku Solver": `def solve_sudoku(board):
def is_valid(r, c, ch):
    for i in range(9):
        if board[r][i] == ch or board[i][c] == ch:
            return False
        if board[3*(r//3)+i//3][3*(c//3)+i%3] == ch:
            return False
    return True

def backtrack():
    for r in range(9):
        for c in range(9):
            if board[r][c] == ".":
                for ch in map(str, range(1, 10)):
                    if is_valid(r, c, ch):
                        board[r][c] = ch
                        if backtrack():
                            return True
                        board[r][c] = "."
                return False
    return True
backtrack()`,
"Generate Parentheses": `def generate_parentheses(n):
result = []
def backtrack(s, left, right):
    if len(s) == 2 * n:
        result.append(s)
        return
    if left < n:
        backtrack(s + "(", left + 1, right)
    if right < left:
        backtrack(s + ")", left, right + 1)
backtrack("", 0, 0)
return result`,

"Rat in a Maze": `def rat_in_maze(maze):
n = len(maze)
result = []
path = []

def is_safe(x, y, visited):
    return 0 <= x < n and 0 <= y < n and maze[x][y] == 1 and not visited[x][y]

def solve(x, y, visited, move):
    if x == n - 1 and y == n - 1:
        result.append("".join(move))
        return
    visited[x][y] = True
    for dx, dy, dir in [(1, 0, 'D'), (0, -1, 'L'), (0, 1, 'R'), (-1, 0, 'U')]:
        nx, ny = x + dx, y + dy
        if is_safe(nx, ny, visited):
            move.append(dir)
            solve(nx, ny, visited, move)
            move.pop()
    visited[x][y] = False

visited = [[False]*n for _ in range(n)]
if maze[0][0] == 1:
    solve(0, 0, visited, path)
return result`,

"Letter Combinations of Phone Number": `def letter_combinations(digits):
if not digits:
    return []
phone = {
    "2": "abc", "3": "def", "4": "ghi", "5": "jkl",
    "6": "mno", "7": "pqrs", "8": "tuv", "9": "wxyz"
}
result = []
def backtrack(index, path):
    if index == len(digits):
        result.append("".join(path))
        return
    for char in phone[digits[index]]:
        path.append(char)
        backtrack(index + 1, path)
        path.pop()
backtrack(0, [])
return result`,
"Tree Traversals": `class TreeNode:
def __init__(self, val=0, left=None, right=None):
    self.val = val
    self.left = left
    self.right = right

def inorder_traversal(root):
if root:
    inorder_traversal(root.left)
    print(root.val, end=' ')
    inorder_traversal(root.right)

def preorder_traversal(root):
if root:
    print(root.val, end=' ')
    preorder_traversal(root.left)
    preorder_traversal(root.right)

def postorder_traversal(root):
if root:
    postorder_traversal(root.left)
    postorder_traversal(root.right)
    print(root.val, end=' ')`,

"Views (Top/Bottom/Side)": `from collections import deque, defaultdict

def top_view(root):
if not root:
    return []
q = deque([(root, 0)])
hd_map = {}
while q:
    node, hd = q.popleft()
    if hd not in hd_map:
        hd_map[hd] = node.val
    if node.left:
        q.append((node.left, hd - 1))
    if node.right:
        q.append((node.right, hd + 1))
return [hd_map[k] for k in sorted(hd_map)]

def bottom_view(root):
if not root:
    return []
q = deque([(root, 0)])
hd_map = {}
while q:
    node, hd = q.popleft()
    hd_map[hd] = node.val
    if node.left:
        q.append((node.left, hd - 1))
    if node.right:
        q.append((node.right, hd + 1))
return [hd_map[k] for k in sorted(hd_map)]

def right_side_view(root):
if not root:
    return []
q = deque([root])
result = []
while q:
    size = len(q)
    for i in range(size):
        node = q.popleft()
        if i == size - 1:
            result.append(node.val)
        if node.left:
            q.append(node.left)
        if node.right:
            q.append(node.right)
return result`,

"Height/Depth": `def tree_height(root):
if not root:
    return 0
return 1 + max(tree_height(root.left), tree_height(root.right))

def tree_depth(root, target, depth=0):
if not root:
    return -1
if root.val == target:
    return depth
left = tree_depth(root.left, target, depth + 1)
if left != -1:
    return left
return tree_depth(root.right, target, depth + 1)`,
"Diameter of Binary Tree": `def diameter_of_binary_tree(root):
diameter = 0
def dfs(node):
    nonlocal diameter
    if not node:
        return 0
    left = dfs(node.left)
    right = dfs(node.right)
    diameter = max(diameter, left + right)
    return 1 + max(left, right)
dfs(root)
return diameter`,

"Balanced Tree": `def is_balanced(root):
def check(node):
    if not node:
        return 0, True
    left_height, left_balanced = check(node.left)
    right_height, right_balanced = check(node.right)
    balanced = left_balanced and right_balanced and abs(left_height - right_height) <= 1
    return 1 + max(left_height, right_height), balanced
_, balanced = check(root)
return balanced`,

"Mirror Tree": `def mirror_tree(root):
if root:
    root.left, root.right = mirror_tree(root.right), mirror_tree(root.left)
return root`,

"Build Tree": `def build_tree(preorder, inorder):
if not preorder or not inorder:
    return None
root_val = preorder[0]
root = TreeNode(root_val)
mid = inorder.index(root_val)
root.left = build_tree(preorder[1:mid+1], inorder[:mid])
root.right = build_tree(preorder[mid+1:], inorder[mid+1:])
return root`,
"Serialize/Deserialize": `import json

def serialize(root):
def dfs(node):
    if not node:
        return None
    return [node.val, dfs(node.left), dfs(node.right)]
return json.dumps(dfs(root))

def deserialize(data):
def build(tree_list):
    if tree_list is None:
        return None
    node = TreeNode(tree_list[0])
    node.left = build(tree_list[1])
    node.right = build(tree_list[2])
    return node
return build(json.loads(data))`,

"Boundary Traversal": `def boundary_traversal(root):
if not root:
    return []
result = []

def left_boundary(node):
    while node:
        if node.left or node.right:
            result.append(node.val)
        node = node.left if node.left else node.right

def right_boundary(node):
    stack = []
    while node:
        if node.left or node.right:
            stack.append(node.val)
        node = node.right if node.right else node.left
    while stack:
        result.append(stack.pop())

def leaves(node):
    if node:
        leaves(node.left)
        if not node.left and not node.right:
            result.append(node.val)
        leaves(node.right)

result.append(root.val)
left_boundary(root.left)
leaves(root.left)
leaves(root.right)
right_boundary(root.right)
return result`,

"Burn Tree": `from collections import deque, defaultdict

def burn_tree(root, target):
parent = {}
def map_parents(node, par=None):
    if node:
        parent[node] = par
        map_parents(node.left, node)
        map_parents(node.right, node)

def find_target(node):
    if not node:
        return None
    if node.val == target:
        return node
    return find_target(node.left) or find_target(node.right)

map_parents(root)
start = find_target(root)
visited = set()
q = deque([start])
time = -1
while q:
    for _ in range(len(q)):
        node = q.popleft()
        visited.add(node)
        for nei in [node.left, node.right, parent[node]]:
            if nei and nei not in visited:
                q.append(nei)
    time += 1
return time`,

"LCA": `def lowest_common_ancestor(root, p, q):
if not root or root == p or root == q:
    return root
left = lowest_common_ancestor(root.left, p, q)
right = lowest_common_ancestor(root.right, p, q)
if left and right:
    return root
return left if left else right`,
"Flatten Binary Tree": `def flatten(root):
def helper(node):
    nonlocal prev
    if not node:
        return
    helper(node.right)
    helper(node.left)
    node.right = prev
    node.left = None
    prev = node

prev = None
helper(root)`,

"Vertical Order Traversal": `from collections import defaultdict, deque

def vertical_order_traversal(root):
if not root:
    return []
col_table = defaultdict(list)
q = deque([(root, 0)])
while q:
    node, col = q.popleft()
    col_table[col].append(node.val)
    if node.left:
        q.append((node.left, col - 1))
    if node.right:
        q.append((node.right, col + 1))
return [col_table[x] for x in sorted(col_table)]`,
"Search/Insert/Delete": `class BST:
def search(self, root, key):
    if not root or root.val == key:
        return root
    if key < root.val:
        return self.search(root.left, key)
    return self.search(root.right, key)

def insert(self, root, key):
    if not root:
        return TreeNode(key)
    if key < root.val:
        root.left = self.insert(root.left, key)
    else:
        root.right = self.insert(root.right, key)
    return root

def delete(self, root, key):
    if not root:
        return None
    if key < root.val:
        root.left = self.delete(root.left, key)
    elif key > root.val:
        root.right = self.delete(root.right, key)
    else:
        if not root.left:
            return root.right
        if not root.right:
            return root.left
        temp = self.find_min(root.right)
        root.val = temp.val
        root.right = self.delete(root.right, temp.val)
    return root

def find_min(self, node):
    while node.left:
        node = node.left
    return node`,

"Validate BST": `def is_valid_bst(root):
def validate(node, low=float('-inf'), high=float('inf')):
    if not node:
        return True
    if not (low < node.val < high):
        return False
    return (validate(node.left, low, node.val) and
            validate(node.right, node.val, high))
return validate(root)`,

"Kth Smallest/Largest": `def kth_smallest(root, k):
stack = []
while root or stack:
    while root:
        stack.append(root)
        root = root.left
    root = stack.pop()
    k -= 1
    if k == 0:
        return root.val
    root = root.right

def kth_largest(root, k):
stack = []
while root or stack:
    while root:
        stack.append(root)
        root = root.right
    root = stack.pop()
    k -= 1
    if k == 0:
        return root.val
    root = root.left`,
"LCA in BST": `def lowest_common_ancestor_bst(root, p, q):
if not root:
    return None
if p.val < root.val and q.val < root.val:
    return lowest_common_ancestor_bst(root.left, p, q)
elif p.val > root.val and q.val > root.val:
    return lowest_common_ancestor_bst(root.right, p, q)
else:
    return root`,

"Convert to BST": `def sorted_array_to_bst(nums):
if not nums:
    return None
mid = len(nums) // 2
root = TreeNode(nums[mid])
root.left = sorted_array_to_bst(nums[:mid])
root.right = sorted_array_to_bst(nums[mid+1:])
return root`,

"Two Sum in BST": `def find_target(root, k):
seen = set()
def dfs(node):
    if not node:
        return False
    if k - node.val in seen:
        return True
    seen.add(node.val)
    return dfs(node.left) or dfs(node.right)
return dfs(root)`,

"Recover BST": `def recover_tree(root):
first = second = prev = None

def inorder(node):
    nonlocal first, second, prev
    if not node:
        return
    inorder(node.left)
    if prev and node.val < prev.val:
        if not first:
            first = prev
        second = node
    prev = node
    inorder(node.right)

inorder(root)
first.val, second.val = second.val, first.val`,
"BST Iterator": `class BSTIterator:
def __init__(self, root):
    self.stack = []
    self._leftmost_inorder(root)

def _leftmost_inorder(self, node):
    while node:
        self.stack.append(node)
        node = node.left

def next(self):
    top = self.stack.pop()
    if top.right:
        self._leftmost_inorder(top.right)
    return top.val

def hasNext(self):
    return len(self.stack) > 0`,

"Merge Two BSTs": `def merge_two_bsts(root1, root2):
def inorder(node, res):
    if node:
        inorder(node.left, res)
        res.append(node.val)
        inorder(node.right, res)

def merge_lists(l1, l2):
    i = j = 0
    merged = []
    while i < len(l1) and j < len(l2):
        if l1[i] < l2[j]:
            merged.append(l1[i])
            i += 1
        else:
            merged.append(l2[j])
            j += 1
    merged += l1[i:] + l2[j:]
    return merged

def sorted_list_to_bst(nums):
    if not nums:
        return None
    mid = len(nums) // 2
    root = TreeNode(nums[mid])
    root.left = sorted_list_to_bst(nums[:mid])
    root.right = sorted_list_to_bst(nums[mid+1:])
    return root

list1, list2 = [], []
inorder(root1, list1)
inorder(root2, list2)
merged = merge_lists(list1, list2)
return sorted_list_to_bst(merged)`,

"Predecessor & Successor": `def find_pre_suc(root, key):
pre = suc = None

def helper(node):
    nonlocal pre, suc
    if not node:
        return
    if node.val == key:
        if node.left:
            tmp = node.left
            while tmp.right:
                tmp = tmp.right
            pre = tmp
        if node.right:
            tmp = node.right
            while tmp.left:
                tmp = tmp.left
            suc = tmp
    elif key < node.val:
        suc = node
        helper(node.left)
    else:
        pre = node
        helper(node.right)

helper(root)
return pre, suc`,
"Heapify": `import heapq

def heapify_list(nums):
heapq.heapify(nums)
return nums  # min-heap by default

# To create a max-heap, store negative values:
def max_heapify_list(nums):
max_heap = [-n for n in nums]
heapq.heapify(max_heap)
return [-n for n in max_heap]`,

"Insert/Delete": `import heapq

class MinHeap:
def __init__(self):
    self.heap = []

def insert(self, val):
    heapq.heappush(self.heap, val)

def delete(self, val):
    try:
        idx = self.heap.index(val)
        self.heap[idx] = self.heap[-1]
        self.heap.pop()
        if idx < len(self.heap):
            heapq._siftup(self.heap, idx)
            heapq._siftdown(self.heap, 0, idx)
    except ValueError:
        pass  # Value not in heap

def get_min(self):
    return self.heap[0] if self.heap else None`,

"Kth Largest/Smallest": `import heapq

def kth_smallest(nums, k):
heapq.heapify(nums)
for _ in range(k - 1):
    heapq.heappop(nums)
return heapq.heappop(nums)

def kth_largest(nums, k):
max_heap = [-n for n in nums]
heapq.heapify(max_heap)
for _ in range(k - 1):
    heapq.heappop(max_heap)
return -heapq.heappop(max_heap)`,
"Top K Frequent": `from collections import Counter
import heapq

def top_k_frequent(nums, k):
count = Counter(nums)
return [item for item, _ in heapq.nlargest(k, count.items(), key=lambda x: x[1])]`,

"Median of Stream": `import heapq

class MedianFinder:
def __init__(self):
    self.small = []  # max heap
    self.large = []  # min heap

def add_num(self, num):
    heapq.heappush(self.small, -num)
    heapq.heappush(self.large, -heapq.heappop(self.small))

    if len(self.large) > len(self.small):
        heapq.heappush(self.small, -heapq.heappop(self.large))

def find_median(self):
    if len(self.small) == len(self.large):
        return (-self.small[0] + self.large[0]) / 2
    return -self.small[0]`,

"Sliding Window Median": `import heapq
from bisect import insort, bisect_left

def median_sliding_window(nums, k):
window = sorted(nums[:k])
medians = []

for i in range(k, len(nums) + 1):
    mid = k // 2
    if k % 2 == 0:
        medians.append((window[mid - 1] + window[mid]) / 2)
    else:
        medians.append(window[mid])

    if i == len(nums):
        break
    window.pop(bisect_left(window, nums[i - k]))
    insort(window, nums[i])
return medians`,
"Reorganize String": `from collections import Counter
import heapq

def reorganize_string(s):
count = Counter(s)
max_heap = [(-freq, ch) for ch, freq in count.items()]
heapq.heapify(max_heap)

prev_freq, prev_char = 0, ''
result = []

while max_heap:
    freq, char = heapq.heappop(max_heap)
    result.append(char)

    if prev_freq < 0:
        heapq.heappush(max_heap, (prev_freq, prev_char))

    prev_freq, prev_char = freq + 1, char  # decrease frequency

return ''.join(result) if len(result) == len(s) else ""`,

"Sort K-Sorted Array": `import heapq

def sort_k_sorted_array(arr, k):
heap = arr[:k+1]
heapq.heapify(heap)
idx = 0

for i in range(k+1, len(arr)):
    arr[idx] = heapq.heappop(heap)
    heapq.heappush(heap, arr[i])
    idx += 1

while heap:
    arr[idx] = heapq.heappop(heap)
    idx += 1

return arr`,
"Adjacency List/Matrix": `# Adjacency List
def build_adj_list(n, edges):
adj = [[] for _ in range(n)]
for u, v in edges:
    adj[u].append(v)
    adj[v].append(u)  # remove if directed
return adj

# Adjacency Matrix
def build_adj_matrix(n, edges):
matrix = [[0] * n for _ in range(n)]
for u, v in edges:
    matrix[u][v] = 1
    matrix[v][u] = 1  # remove if directed
return matrix`,

"Edge List": `# Just a list of all edges with optional weights
edges = [(0, 1), (1, 2), (2, 3)]  # unweighted
edges = [(0, 1, 4), (1, 2, 5)]    # weighted`,

"BFS": `from collections import deque

def bfs(graph, start):
visited = set()
queue = deque([start])
result = []

while queue:
    node = queue.popleft()
    if node not in visited:
        visited.add(node)
        result.append(node)
        queue.extend(graph[node])
return result`,

"DFS": `def dfs(graph, start, visited=None, result=None):
if visited is None:
    visited = set()
if result is None:
    result = []
visited.add(start)
result.append(start)
for neighbor in graph[start]:
    if neighbor not in visited:
        dfs(graph, neighbor, visited, result)
return result`,

"Dijkstra's": `import heapq

def dijkstra(n, edges, start):
graph = [[] for _ in range(n)]
for u, v, w in edges:
    graph[u].append((v, w))

dist = [float('inf')] * n
dist[start] = 0
heap = [(0, start)]

while heap:
    d, u = heapq.heappop(heap)
    if d > dist[u]:
        continue
    for v, w in graph[u]:
        if dist[u] + w < dist[v]:
            dist[v] = dist[u] + w
            heapq.heappush(heap, (dist[v], v))
return dist`,

"Bellman-Ford": `def bellman_ford(n, edges, start):
dist = [float('inf')] * n
dist[start] = 0

for _ in range(n - 1):
    for u, v, w in edges:
        if dist[u] + w < dist[v]:
            dist[v] = dist[u] + w

# Optional: detect negative cycle
for u, v, w in edges:
    if dist[u] + w < dist[v]:
        return "Negative cycle detected"

return dist`,
"Floyd-Warshall": `def floyd_warshall(n, graph):
dist = [[float('inf')] * n for _ in range(n)]
for u in range(n):
    dist[u][u] = 0
for u, v, w in graph:
    dist[u][v] = w  # if undirected: dist[v][u] = w too

for k in range(n):
    for i in range(n):
        for j in range(n):
            if dist[i][k] + dist[k][j] < dist[i][j]:
                dist[i][j] = dist[i][k] + dist[k][j]
return dist`,

"A* Search": `import heapq

def a_star(start, goal, graph, h):
open_set = [(h[start], 0, start)]
g_score = {start: 0}
came_from = {}

while open_set:
    _, cost, current = heapq.heappop(open_set)
    if current == goal:
        path = []
        while current in came_from:
            path.append(current)
            current = came_from[current]
        return path[::-1] + [goal]

    for neighbor, weight in graph[current]:
        tentative = cost + weight
        if neighbor not in g_score or tentative < g_score[neighbor]:
            g_score[neighbor] = tentative
            f = tentative + h[neighbor]
            heapq.heappush(open_set, (f, tentative, neighbor))
            came_from[neighbor] = current
return []`,

"Cycle Detection": `def has_cycle_directed(graph, n):
visited = [0] * n  # 0=unvisited, 1=visiting, 2=visited

def dfs(v):
    if visited[v] == 1:
        return True
    if visited[v] == 2:
        return False
    visited[v] = 1
    for neighbor in graph[v]:
        if dfs(neighbor):
            return True
    visited[v] = 2
    return False

for i in range(n):
    if visited[i] == 0:
        if dfs(i):
            return True
return False

def has_cycle_undirected(graph, n):
visited = [False] * n

def dfs(v, parent):
    visited[v] = True
    for neighbor in graph[v]:
        if not visited[neighbor]:
            if dfs(neighbor, v):
                return True
        elif neighbor != parent:
            return True
    return False

for i in range(n):
    if not visited[i]:
        if dfs(i, -1):
            return True
return False`,

"Topological Sort": `from collections import deque

def topological_sort_kahn(n, graph):
in_degree = [0] * n
for u in range(n):
    for v in graph[u]:
        in_degree[v] += 1

q = deque([i for i in range(n) if in_degree[i] == 0])
topo = []

while q:
    node = q.popleft()
    topo.append(node)
    for neighbor in graph[node]:
        in_degree[neighbor] -= 1
        if in_degree[neighbor] == 0:
            q.append(neighbor)

return topo if len(topo) == n else []  # empty if cycle`,

"0-1 BFS": `from collections import deque

def zero_one_bfs(n, edges, start):
graph = [[] for _ in range(n)]
for u, v, w in edges:  # w must be 0 or 1
    graph[u].append((v, w))

dist = [float('inf')] * n
dist[start] = 0
dq = deque([start])

while dq:
    u = dq.popleft()
    for v, w in graph[u]:
        if dist[u] + w < dist[v]:
            dist[v] = dist[u] + w
            if w == 0:
                dq.appendleft(v)
            else:
                dq.append(v)
return dist`,
"Fibonacci": `def fib(n):
if n <= 1: return n
dp = [0, 1]
for i in range(2, n+1):
    dp.append(dp[-1] + dp[-2])
return dp[n]`,

"Climbing Stairs": `def climb_stairs(n):
if n <= 2: return n
a, b = 1, 2
for _ in range(3, n+1):
    a, b = b, a + b
return b`,

"House Robber": `def rob(nums):
prev, curr = 0, 0
for num in nums:
    prev, curr = curr, max(curr, prev + num)
return curr`,

"Jump Game": `def can_jump(nums):
reach = 0
for i, num in enumerate(nums):
    if i > reach:
        return False
    reach = max(reach, i + num)
return True`,

"Maximum Product Subarray": `def max_product(nums):
max_prod = min_prod = result = nums[0]
for num in nums[1:]:
    choices = (num, max_prod * num, min_prod * num)
    max_prod = max(choices)
    min_prod = min(choices)
    result = max(result, max_prod)
return result`,

"Unique Paths": `def unique_paths(m, n):
dp = [[1]*n for _ in range(m)]
for i in range(1, m):
    for j in range(1, n):
        dp[i][j] = dp[i-1][j] + dp[i][j-1]
return dp[-1][-1]`,

"Minimum Path Sum": `def min_path_sum(grid):
m, n = len(grid), len(grid[0])
for i in range(1, m):
    grid[i][0] += grid[i-1][0]
for j in range(1, n):
    grid[0][j] += grid[0][j-1]
for i in range(1, m):
    for j in range(1, n):
        grid[i][j] += min(grid[i-1][j], grid[i][j-1])
return grid[-1][-1]`,

"Maximum Square Sub-matrix": `def maximal_square(matrix):
if not matrix: return 0
m, n = len(matrix), len(matrix[0])
dp = [[0]*n for _ in range(m)]
max_side = 0
for i in range(m):
    for j in range(n):
        if matrix[i][j] == '1':
            if i and j:
                dp[i][j] = min(dp[i-1][j], dp[i][j-1], dp[i-1][j-1]) + 1
            else:
                dp[i][j] = 1
            max_side = max(max_side, dp[i][j])
return max_side * max_side`,

"Cherry Pickup": `def cherry_pickup(grid):
n = len(grid)
dp = [[[-float('inf')]*n for _ in range(n)] for _ in range(n)]
dp[0][0][0] = grid[0][0]

for x1 in range(n):
    for y1 in range(n):
        for x2 in range(n):
            y2 = x1 + y1 - x2
            if 0 <= y2 < n:
                if grid[x1][y1] == -1 or grid[x2][y2] == -1:
                    continue
                val = grid[x1][y1]
                if x1 != x2:
                    val += grid[x2][y2]
                for dx1, dy1 in ((-1, 0), (0, -1)):
                    for dx2, dy2 in ((-1, 0), (0, -1)):
                        px1, py1, px2, py2 = x1 + dx1, y1 + dy1, x2 + dx2, y2 + dy2
                        if 0 <= px1 < n and 0 <= py1 < n and 0 <= px2 < n and 0 <= py2 < n:
                            dp[x1][y1][x2] = max(dp[x1][y1][x2], dp[px1][py1][px2] + val)
return max(0, dp[n-1][n-1][n-1])`,

"Dungeon Game": `def calculate_minimum_hp(dungeon):
m, n = len(dungeon), len(dungeon[0])
dp = [[float('inf')] * (n+1) for _ in range(m+1)]
dp[m][n-1] = dp[m-1][n] = 1
for i in reversed(range(m)):
    for j in reversed(range(n)):
        dp[i][j] = max(1, min(dp[i+1][j], dp[i][j+1]) - dungeon[i][j])
return dp[0][0]`,
"LCS": `def lcs(text1, text2):
m, n = len(text1), len(text2)
dp = [[0]*(n+1) for _ in range(m+1)]
for i in range(m):
    for j in range(n):
        if text1[i] == text2[j]:
            dp[i+1][j+1] = dp[i][j] + 1
        else:
            dp[i+1][j+1] = max(dp[i][j+1], dp[i+1][j])
return dp[m][n]`,

"LIS": `def lis(nums):
dp = []
from bisect import bisect_left
for num in nums:
    i = bisect_left(dp, num)
    if i == len(dp):
        dp.append(num)
    else:
        dp[i] = num
return len(dp)`,

"LPS": `def longest_palindromic_subseq(s):
n = len(s)
dp = [[0]*n for _ in range(n)]
for i in range(n-1, -1, -1):
    dp[i][i] = 1
    for j in range(i+1, n):
        if s[i] == s[j]:
            dp[i][j] = 2 + dp[i+1][j-1]
        else:
            dp[i][j] = max(dp[i+1][j], dp[i][j-1])
return dp[0][n-1]`,

"Edit Distance": `def edit_distance(word1, word2):
m, n = len(word1), len(word2)
dp = [[0]*(n+1) for _ in range(m+1)]
for i in range(m+1):
    for j in range(n+1):
        if i == 0:
            dp[i][j] = j
        elif j == 0:
            dp[i][j] = i
        elif word1[i-1] == word2[j-1]:
            dp[i][j] = dp[i-1][j-1]
        else:
            dp[i][j] = 1 + min(dp[i-1][j], dp[i][j-1], dp[i-1][j-1])
return dp[m][n]`,

"Wildcard Matching": `def is_match(s, p):
m, n = len(s), len(p)
dp = [[False]*(n+1) for _ in range(m+1)]
dp[0][0] = True
for j in range(1, n+1):
    if p[j-1] == '*':
        dp[0][j] = dp[0][j-1]
for i in range(1, m+1):
    for j in range(1, n+1):
        if p[j-1] == '*':
            dp[i][j] = dp[i][j-1] or dp[i-1][j]
        elif p[j-1] == '?' or s[i-1] == p[j-1]:
            dp[i][j] = dp[i-1][j-1]
return dp[m][n]`,

"Subset Sum": `def subset_sum(nums, target):
dp = [False] * (target + 1)
dp[0] = True
for num in nums:
    for t in range(target, num - 1, -1):
        dp[t] = dp[t] or dp[t - num]
return dp[target]`,

"Target Sum": `def find_target_sum_ways(nums, target):
total = sum(nums)
if (target + total) % 2 != 0 or total < abs(target):
    return 0
s = (target + total) // 2
dp = [0] * (s + 1)
dp[0] = 1
for num in nums:
    for j in range(s, num - 1, -1):
        dp[j] += dp[j - num]
return dp[s]`,

"Palindrome Partitioning II": `def min_cut(s):
n = len(s)
is_pal = [[False]*n for _ in range(n)]
for i in range(n):
    is_pal[i][i] = True
for l in range(2, n+1):
    for i in range(n - l + 1):
        j = i + l - 1
        if s[i] == s[j] and (l == 2 or is_pal[i+1][j-1]):
            is_pal[i][j] = True
cuts = [0]*n
for i in range(n):
    if is_pal[0][i]:
        cuts[i] = 0
    else:
        cuts[i] = min(cuts[j]+1 for j in range(i) if is_pal[j+1][i])
return cuts[-1]`,

"0/1 Knapsack": `def knapsack(wt, val, W):
n = len(wt)
dp = [[0]*(W+1) for _ in range(n+1)]
for i in range(1, n+1):
    for w in range(W+1):
        if wt[i-1] <= w:
            dp[i][w] = max(dp[i-1][w], val[i-1] + dp[i-1][w - wt[i-1]])
        else:
            dp[i][w] = dp[i-1][w]
return dp[n][W]`,

"Unbounded Knapsack": `def unbounded_knapsack(W, wt, val):
n = len(wt)
dp = [0] * (W + 1)
for w in range(W + 1):
    for i in range(n):
        if wt[i] <= w:
            dp[w] = max(dp[w], val[i] + dp[w - wt[i]])
return dp[W]`,

"Rod Cutting": `def rod_cutting(price, n):
dp = [0] * (n+1)
for i in range(1, n+1):
    for j in range(i):
        dp[i] = max(dp[i], price[j] + dp[i-j-1])
return dp[n]`,

"Coin Change": `def coin_change(coins, amount):
dp = [float('inf')] * (amount + 1)
dp[0] = 0
for coin in coins:
    for x in range(coin, amount + 1):
        dp[x] = min(dp[x], dp[x - coin] + 1)
return dp[amount] if dp[amount] != float('inf') else -1`,

"House Robber III": `def rob_tree(root):
def dfs(node):
    if not node:
        return (0, 0)
    left = dfs(node.left)
    right = dfs(node.right)
    rob = node.val + left[1] + right[1]
    not_rob = max(left) + max(right)
    return (rob, not_rob)
return max(dfs(root))`,

"TSP": `def tsp(graph):
n = len(graph)
dp = [[float('inf')] * n for _ in range(1 << n)]
dp[1][0] = 0
for mask in range(1, 1 << n):
    for u in range(n):
        if not (mask & (1 << u)):
            continue
        for v in range(n):
            if mask & (1 << v):
                continue
            dp[mask | (1 << v)][v] = min(dp[mask | (1 << v)][v], dp[mask][u] + graph[u][v])
return min(dp[-1][i] + graph[i][0] for i in range(n))`,

"Assignment Problem": `def assignment_problem(cost):
from functools import lru_cache
n = len(cost)

@lru_cache(None)
def dp(i, mask):
    if i == n:
        return 0
    ans = float('inf')
    for j in range(n):
        if not (mask & (1 << j)):
            ans = min(ans, cost[i][j] + dp(i+1, mask | (1 << j)))
    return ans

return dp(0, 0)`,
"Insert/Search/Delete": `class TrieNode:
def __init__(self):
    self.children = {}
    self.end = False

class Trie:
def __init__(self):
    self.root = TrieNode()

def insert(self, word):
    node = self.root
    for ch in word:
        node = node.children.setdefault(ch, TrieNode())
    node.end = True

def search(self, word):
    node = self.root
    for ch in word:
        if ch not in node.children:
            return False
        node = node.children[ch]
    return node.end

def delete(self, word):
    def _delete(node, word, depth):
        if depth == len(word):
            if not node.end:
                return False
            node.end = False
            return len(node.children) == 0
        ch = word[depth]
        if ch not in node.children:
            return False
        should_delete = _delete(node.children[ch], word, depth + 1)
        if should_delete:
            del node.children[ch]
            return not node.end and len(node.children) == 0
        return False
    _delete(self.root, word, 0)`,

"StartsWith": `def starts_with(self, prefix):
node = self.root
for ch in prefix:
    if ch not in node.children:
        return False
    node = node.children[ch]
return True`,

"Word Search II": `def find_words(board, words):
trie = Trie()
for word in words:
    trie.insert(word)
res, m, n = set(), len(board), len(board[0])

def dfs(i, j, node, path):
    if node.end:
        res.add(path)
    if not (0 <= i < m and 0 <= j < n):
        return
    ch = board[i][j]
    if ch not in node.children:
        return
    board[i][j] = "#"
    for dx, dy in [(-1,0),(1,0),(0,-1),(0,1)]:
        dfs(i+dx, j+dy, node.children[ch], path+ch)
    board[i][j] = ch

for i in range(m):
    for j in range(n):
        dfs(i, j, trie.root, "")
return list(res)`,

"Longest Word with Prefixes": `def longest_word(words):
trie = Trie()
for word in words:
    trie.insert(word)
res = ""
def dfs(node, path):
    nonlocal res
    if not node.end and node != trie.root:
        return
    if len(path) > len(res) or (len(path) == len(res) and path < res):
        res = path
    for ch in sorted(node.children.keys()):
        dfs(node.children[ch], path + ch)
dfs(trie.root, "")
return res`,

"Replace Words": `def replace_words(dictionary, sentence):
trie = Trie()
for word in dictionary:
    trie.insert(word)

def replace(word):
    node = trie.root
    prefix = ""
    for ch in word:
        if ch not in node.children or node.end:
            break
        node = node.children[ch]
        prefix += ch
    return prefix if node.end else word

return ' '.join(replace(w) for w in sentence.split())`,

"Auto-complete": `def autocomplete(trie, prefix):
node = trie.root
for ch in prefix:
    if ch not in node.children:
        return []
    node = node.children[ch]
results = []
def dfs(n, path):
    if n.end:
        results.append(path)
    for ch in n.children:
        dfs(n.children[ch], path + ch)
dfs(node, prefix)
return results`,

"Maximum XOR Pair": `def find_max_xor(nums):
class XORTrie:
    def __init__(self):
        self.root = {}

    def insert(self, num):
        node = self.root
        for i in range(31, -1, -1):
            bit = (num >> i) & 1
            if bit not in node:
                node[bit] = {}
            node = node[bit]

    def max_xor(self, num):
        node = self.root
        xor = 0
        for i in range(31, -1, -1):
            bit = (num >> i) & 1
            opp = 1 - bit
            if opp in node:
                xor |= (1 << i)
                node = node[opp]
            else:
                node = node.get(bit, {})
        return xor

trie = XORTrie()
max_result = 0
for num in nums:
    trie.insert(num)
for num in nums:
    max_result = max(max_result, trie.max_xor(num))
return max_result`,

"XOR Trie Queries": `def xor_queries(nums, queries):
class XORTrie:
    def __init__(self):
        self.root = {}

    def insert(self, num):
        node = self.root
        for i in range(31, -1, -1):
            bit = (num >> i) & 1
            if bit not in node:
                node[bit] = {}
            node = node[bit]

    def max_xor(self, num):
        node = self.root
        if not node:
            return -1
        xor = 0
        for i in range(31, -1, -1):
            bit = (num >> i) & 1
            toggled = 1 - bit
            if toggled in node:
                xor |= (1 << i)
                node = node[toggled]
            else:
                node = node.get(bit, {})
        return xor

res = []
trie = XORTrie()
nums.sort()
queries = sorted([(x, m, i) for i, (x, m) in enumerate(queries)], key=lambda x: x[1])
i = 0
for x, m, idx in queries:
    while i < len(nums) and nums[i] <= m:
        trie.insert(nums[i])
        i += 1
    res.append((idx, trie.max_xor(x)))
res.sort()
return [x[1] for x in res]`,
"Range Sum Query": `class SegmentTree:
def __init__(self, nums):
    n = len(nums)
    self.n = n
    self.tree = [0] * (2 * n)
    for i in range(n):
        self.tree[n + i] = nums[i]
    for i in range(n - 1, 0, -1):
        self.tree[i] = self.tree[i << 1] + self.tree[i << 1 | 1]

def update(self, index, value):
    pos = index + self.n
    self.tree[pos] = value
    while pos > 1:
        pos >>= 1
        self.tree[pos] = self.tree[pos << 1] + self.tree[pos << 1 | 1]

def query(self, left, right):
    res = 0
    left += self.n
    right += self.n
    while left < right:
        if left & 1:
            res += self.tree[left]
            left += 1
        if right & 1:
            right -= 1
            res += self.tree[right]
        left >>= 1
        right >>= 1
    return res`,

"Min/Max Query": `class MinSegmentTree:
def __init__(self, nums):
    n = len(nums)
    self.n = n
    self.tree = [float('inf')] * (2 * n)
    for i in range(n):
        self.tree[n + i] = nums[i]
    for i in range(n - 1, 0, -1):
        self.tree[i] = min(self.tree[i << 1], self.tree[i << 1 | 1])

def update(self, index, value):
    pos = index + self.n
    self.tree[pos] = value
    while pos > 1:
        pos >>= 1
        self.tree[pos] = min(self.tree[pos << 1], self.tree[pos << 1 | 1])

def query(self, left, right):
    res = float('inf')
    left += self.n
    right += self.n
    while left < right:
        if left & 1:
            res = min(res, self.tree[left])
            left += 1
        if right & 1:
            right -= 1
            res = min(res, self.tree[right])
        left >>= 1
        right >>= 1
    return res`,

"Lazy Propagation": `class LazySegmentTree:
def __init__(self, n):
    self.n = n
    self.tree = [0] * (4 * n)
    self.lazy = [0] * (4 * n)

def update_range(self, start, end, val, l=0, r=None, node=1):
    if r is None:
        r = self.n - 1
    if self.lazy[node] != 0:
        self.tree[node] += (r - l + 1) * self.lazy[node]
        if l != r:
            self.lazy[2*node] += self.lazy[node]
            self.lazy[2*node+1] += self.lazy[node]
        self.lazy[node] = 0
    if r < start or l > end:
        return
    if start <= l and r <= end:
        self.tree[node] += (r - l + 1) * val
        if l != r:
            self.lazy[2*node] += val
            self.lazy[2*node+1] += val
        return
    mid = (l + r) // 2
    self.update_range(start, end, val, l, mid, 2*node)
    self.update_range(start, end, val, mid+1, r, 2*node+1)
    self.tree[node] = self.tree[2*node] + self.tree[2*node+1]

def query_range(self, start, end, l=0, r=None, node=1):
    if r is None:
        r = self.n - 1
    if self.lazy[node] != 0:
        self.tree[node] += (r - l + 1) * self.lazy[node]
        if l != r:
            self.lazy[2*node] += self.lazy[node]
            self.lazy[2*node+1] += self.lazy[node]
        self.lazy[node] = 0
    if r < start or l > end:
        return 0
    if start <= l and r <= end:
        return self.tree[node]
    mid = (l + r) // 2
    return self.query_range(start, end, l, mid, 2*node) + self.query_range(start, end, mid+1, r, 2*node+1)`,

"Point Update": `class BIT:
def __init__(self, n):
    self.n = n + 1
    self.bit = [0] * self.n

def update(self, i, delta):
    i += 1
    while i < self.n:
        self.bit[i] += delta
        i += i & -i

def query(self, i):
    i += 1
    res = 0
    while i > 0:
        res += self.bit[i]
        i -= i & -i
    return res`,

"Inversion Count": `def count_inversions(arr):
max_val = max(arr)
bit = BIT(max_val + 1)
inv_count = 0
for i in reversed(arr):
    inv_count += bit.query(i - 1)
    bit.update(i, 1)
return inv_count`,

"2D BIT": `class BIT2D:
def __init__(self, m, n):
    self.m = m + 1
    self.n = n + 1
    self.bit = [[0] * self.n for _ in range(self.m)]

def update(self, x, y, delta):
    xi = x + 1
    while xi < self.m:
        yi = y + 1
        while yi < self.n:
            self.bit[xi][yi] += delta
            yi += yi & -yi
        xi += xi & -xi

def query(self, x, y):
    res = 0
    xi = x + 1
    while xi > 0:
        yi = y + 1
        while yi > 0:
            res += self.bit[xi][yi]
            yi -= yi & -yi
        xi -= xi & -xi
    return res

def range_sum(self, x1, y1, x2, y2):
    return self.query(x2, y2) - self.query(x1 - 1, y2) - self.query(x2, y1 - 1) + self.query(x1 - 1, y1 - 1)`,
"Set Bits": `def count_set_bits(n):
count = 0
while n:
    count += n & 1
    n >>= 1
return count`,

"Power of Two": `def is_power_of_two(n):
return n > 0 and (n & (n - 1)) == 0`,

"XOR": `def xor_upto(n):
# XOR from 1 to n
if n % 4 == 0: return n
if n % 4 == 1: return 1
if n % 4 == 2: return n + 1
return 0`,

"Missing Number": `def find_missing(nums):
n = len(nums)
xor_all = 0
for i in range(n + 1):
    xor_all ^= i
for num in nums:
    xor_all ^= num
return xor_all`,

"Duplicate Number": `def find_duplicate(nums):
slow = fast = nums[0]
while True:
    slow = nums[slow]
    fast = nums[nums[fast]]
    if slow == fast:
        break
slow = nums[0]
while slow != fast:
    slow = nums[slow]
    fast = nums[fast]
return slow`,

"Single Number": `def single_number(nums):
res = 0
for num in nums:
    res ^= num
return res`,

"Bitmask Subsets": `def subsets(nums):
n = len(nums)
result = []
for mask in range(1 << n):
    subset = []
    for i in range(n):
        if mask & (1 << i):
            subset.append(nums[i])
    result.append(subset)
return result`,

"Sum of XORs": `def subset_xor_sum(nums):
total = 0
for mask in range(1 << len(nums)):
    xor_sum = 0
    for i in range(len(nums)):
        if mask & (1 << i):
            xor_sum ^= nums[i]
    total += xor_sum
return total`,

"Swap/Toggle Bits": `def swap_bits(n, i, j):
if ((n >> i) & 1) != ((n >> j) & 1):
    n ^= (1 << i) | (1 << j)
return n

def toggle_bit(n, i):
return n ^ (1 << i)`,
"GCD/LCM": `from math import gcd
def lcm(a, b):
return a * b // gcd(a, b)`,

"Sieve of Eratosthenes": `def sieve(n):
is_prime = [True] * (n + 1)
is_prime[0:2] = [False, False]
for i in range(2, int(n**0.5) + 1):
    if is_prime[i]:
        for j in range(i*i, n+1, i):
            is_prime[j] = False
return [i for i, prime in enumerate(is_prime) if prime]`,

"Prime Factorization": `def prime_factors(n):
factors = []
i = 2
while i * i <= n:
    while n % i == 0:
        factors.append(i)
        n //= i
    i += 1
if n > 1:
    factors.append(n)
return factors`,

"Modular Exponentiation": `def mod_pow(a, b, mod):
result = 1
a %= mod
while b > 0:
    if b & 1:
        result = (result * a) % mod
    a = (a * a) % mod
    b >>= 1
return result`,

"Modular Inverse": `def mod_inv(a, mod):
# Fermat’s little theorem: a^(mod-2) % mod
return mod_pow(a, mod - 2, mod)`,

"Fast Power": `def fast_pow(a, b):
res = 1
while b > 0:
    if b % 2 == 1:
        res *= a
    a *= a
    b //= 2
return res`,

"nCr / Pascal's Triangle": `def pascal_triangle(n):
C = [[0] * (n+1) for _ in range(n+1)]
for i in range(n+1):
    C[i][0] = 1
    for j in range(1, i+1):
        C[i][j] = C[i-1][j-1] + C[i-1][j]
return C`,

"Matrix Exponentiation": `def mat_mult(a, b):
return [
    [a[0][0]*b[0][0] + a[0][1]*b[1][0],
     a[0][0]*b[0][1] + a[0][1]*b[1][1]],
    [a[1][0]*b[0][0] + a[1][1]*b[1][0],
     a[1][0]*b[0][1] + a[1][1]*b[1][1]]
]

def mat_pow(mat, n):
res = [[1, 0], [0, 1]]
while n > 0:
    if n % 2 == 1:
        res = mat_mult(res, mat)
    mat = mat_mult(mat, mat)
    n //= 2
return res`,

"Trailing Zeros": `def trailing_zeros(n):
count = 0
while n >= 5:
    n //= 5
    count += n
return count`,

"Armstrong Number": `def is_armstrong(n):
digits = list(map(int, str(n)))
power = len(digits)
return sum(d ** power for d in digits) == n`,

"Perfect Number": `def is_perfect(n):
divisors = [1]
for i in range(2, int(n**0.5)+1):
    if n % i == 0:
        divisors.extend([i, n//i] if i != n//i else [i])
return sum(divisors) == n and n != 1`,
"Reservoir Sampling": `import random
def reservoir_sampling(stream, k):
reservoir = stream[:k]
for i in range(k, len(stream)):
    j = random.randint(0, i)
    if j < k:
        reservoir[j] = stream[i]
return reservoir`,

"KMP": `def kmp(pattern, text):
def compute_lps(pat):
    lps = [0] * len(pat)
    length = 0
    i = 1
    while i < len(pat):
        if pat[i] == pat[length]:
            length += 1
            lps[i] = length
            i += 1
        elif length != 0:
            length = lps[length - 1]
        else:
            lps[i] = 0
            i += 1
    return lps

lps = compute_lps(pattern)
i = j = 0
while i < len(text):
    if pattern[j] == text[i]:
        i += 1
        j += 1
    if j == len(pattern):
        print(f"Pattern found at index {i - j}")
        j = lps[j - 1]
    elif i < len(text) and pattern[j] != text[i]:
        if j != 0:
            j = lps[j - 1]
        else:
            i += 1`,

"Rabin-Karp": `def rabin_karp(text, pattern, d=256, q=101):
n = len(text)
m = len(pattern)
h = pow(d, m-1) % q
p = 0  # hash for pattern
t = 0  # hash for text

for i in range(m):
    p = (d * p + ord(pattern[i])) % q
    t = (d * t + ord(text[i])) % q

for s in range(n - m + 1):
    if p == t:
        if text[s:s+m] == pattern:
            print(f"Pattern found at index {s}")
    if s < n - m:
        t = (d * (t - ord(text[s]) * h) + ord(text[s + m])) % q
        if t < 0:
            t += q`,

"Z-Algorithm": `def z_algorithm(s):
n = len(s)
z = [0] * n
l, r = 0, 0
for i in range(1, n):
    if i <= r:
        z[i] = min(r - i + 1, z[i - l])
    while i + z[i] < n and s[z[i]] == s[i + z[i]]:
        z[i] += 1
    if i + z[i] - 1 > r:
        l, r = i, i + z[i] - 1
return z`,

"Manacher’s Algorithm": `def manachers(s):
t = '#'.join('^{}$'.format(s))
n = len(t)
p = [0] * n
center = right = 0
for i in range(1, n-1):
    mirror = 2 * center - i
    if i < right:
        p[i] = min(right - i, p[mirror])
    while t[i + (1 + p[i])] == t[i - (1 + p[i])]:
        p[i] += 1
    if i + p[i] > right:
        center, right = i, i + p[i]
return max(p)`,

"Union-Find Rollback": `class RollbackDSU:
def __init__(self, n):
    self.parent = list(range(n))
    self.rank = [1]*n
    self.history = []

def find(self, x):
    while x != self.parent[x]:
        x = self.parent[x]
    return x

def union(self, x, y):
    x, y = self.find(x), self.find(y)
    if x == y:
        self.history.append((-1, -1))
        return False
    if self.rank[x] < self.rank[y]:
        x, y = y, x
    self.history.append((y, self.rank[x]))
    self.parent[y] = x
    self.rank[x] += self.rank[y]
    return True

def rollback(self):
    y, rx = self.history.pop()
    if y == -1:
        return
    x = self.parent[y]
    self.rank[x] = rx
    self.parent[y] = y`,

"Mo’s Algorithm": `import math
def mo_algorithm(queries, arr):
block_size = int(len(arr) ** 0.5)
queries.sort(key=lambda x: (x[0] // block_size, x[1]))

curr_l, curr_r, ans = 0, 0, 0
freq = [0] * (max(arr)+1)
res = [0] * len(queries)

def add(x):
    nonlocal ans
    freq[x] += 1
    if freq[x] == 1:
        ans += 1

def remove(x):
    nonlocal ans
    freq[x] -= 1
    if freq[x] == 0:
        ans -= 1

for i, (l, r) in enumerate(queries):
    while curr_l > l:
        curr_l -= 1
        add(arr[curr_l])
    while curr_r <= r:
        add(arr[curr_r])
        curr_r += 1
    while curr_l < l:
        remove(arr[curr_l])
        curr_l += 1
    while curr_r > r + 1:
        curr_r -= 1
        remove(arr[curr_r])
    res[i] = ans
return res`,

"Centroid Decomposition": `from collections import defaultdict
class CentroidDecomposition:
def __init__(self, n):
    self.tree = defaultdict(list)
    self.size = [0] * n
    self.centroid_parent = [-1] * n
    self.n = n
    self.visited = [False] * n

def add_edge(self, u, v):
    self.tree[u].append(v)
    self.tree[v].append(u)

def dfs_size(self, u, p):
    self.size[u] = 1
    for v in self.tree[u]:
        if v != p and not self.visited[v]:
            self.size[u] += self.dfs_size(v, u)
    return self.size[u]

def find_centroid(self, u, p, n):
    for v in self.tree[u]:
        if v != p and not self.visited[v] and self.size[v] > n // 2:
            return self.find_centroid(v, u, n)
    return u

def decompose(self, u, p):
    n = self.dfs_size(u, -1)
    centroid = self.find_centroid(u, -1, n)
    self.visited[centroid] = True
    self.centroid_parent[centroid] = p
    for v in self.tree[centroid]:
        if not self.visited[v]:
            self.decompose(v, centroid)`,

"Convex Hull": `def convex_hull(points):
points = sorted(set(points))
if len(points) <= 1:
    return points

def cross(o, a, b):
    return (a[0] - o[0]) * (b[1] - o[1]) - \
           (a[1] - o[1]) * (b[0] - o[0])

lower, upper = [], []
for p in points:
    while len(lower) >= 2 and cross(lower[-2], lower[-1], p) <= 0:
        lower.pop()
    lower.append(p)
for p in reversed(points):
    while len(upper) >= 2 and cross(upper[-2], upper[-1], p) <= 0:
        upper.pop()
    upper.append(p)
return lower[:-1] + upper[:-1]`,




}; // Placeholder: you can add real code snippets here.

(function initAlgoScope(){
  const container = document.getElementById("container");
  if (!container) return;

  for (const category in data) {
    const catDiv = document.createElement("div");
    catDiv.className = "category";
    catDiv.innerHTML = `<h2>${category}</h2><div class="algo-list"></div>`;

    const list = catDiv.querySelector(".algo-list");
    data[category].forEach((algo) => {
      const card = document.createElement("div");
      card.className = "algo-card";
      card.textContent = algo;
      card.onclick = () => {
        const code = codeSamples[algo] || `// 📌 ${algo} implementation coming soon...`;
        const codeDisplay = document.getElementById("codeDisplay");
        const codeBlock = document.getElementById("codeBlock");
        if (codeDisplay && codeBlock) {
          codeDisplay.textContent = code;
          codeBlock.style.display = "block";
          window.scrollTo({ top: document.body.scrollHeight, behavior: "smooth" });
        }
      };
      list.appendChild(card);
    });

    container.appendChild(catDiv);
  }
})();
