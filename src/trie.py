class Node:
    def __init__(self, c):
        self.c = c
        self.end = False  # final de paraula
        self.count = 0  # numero de vegades que s'ha insertat
        self.children = {}

class Trie(object):
    def __init__(self):
        self.root = Node("")

    def insert(self, word):
        node = self.root

        for c in word:
            if c in node.children:
                node = node.children[char]
            else:
                new_node = Node(c)
                node.children(c) = new_node
                node = new_node
        node.is_end = True
        node.counter += 1

    def dfs(self, node, prefix):
        if node.is_end:
            self.output.append((prefix + node.char, node.counter))
        for child in node.children.values():
            self.dfs(child, prefix + node.char)

    def query(self, x):
        """Given an input (a prefix), retrieve all words stored in
        the trie with that prefix, sort the words by the number of 
        times they have been inserted
        """
        # Use a variable within the class to keep all possible outputs
        # As there can be more than one word with such prefix
        self.output = []
        node = self.root

        # Check if the prefix is in the trie
        for char in x:
            if char in node.children:
                node = node.children[char]
            else:
                # cannot found the prefix, return empty list
                return []

        # Traverse the trie to get all candidates
        self.dfs(node, x[:-1])

        # Sort the results in reverse order and return
        return sorted(self.output, key=lambda x: x[1], reverse=True)
