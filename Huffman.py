from heapq import heapify, heappop, heappush
from collections import Counter, namedtuple
import json

__all__ = ['encode', 'decode', 'encode_to_files', 'encode_to_files']


Node = namedtuple('Node', ['count', 'letter', 'left', 'right'])
CompressNode = namedtuple('CompressNode', ['letter', 'left', 'right'])

def make_tree(heap):
    """Make a Huffman tree.

    heap: list of Nodes with the heap property
    """

    while len(heap) > 1:
        left = heappop(heap)
        right = heappop(heap)

        count = left.count + right.count
        node = Node(count, '\0', left, right)
        heappush(heap, node)

    return heappop(heap)


def is_leaf(node):
    '''Check that node is a leaf
    '''
    return node.left is None and node.right is None


def make_table_recursive(node, path, table):
    '''Transform Haffman tree to table (recursive function)

    node: root Node
    path: prefix of code
    table: dict {char: code}
    '''

    if node is None:
        return

    if is_leaf(node):
        table[node.letter] = path
        return

    make_table_recursive(node.left, path+'0', table)
    make_table_recursive(node.right, path+'1', table)


def make_table(root):
    '''Transform Haffman tree to table
    root: root Node of tree
    '''

    table = {}
    make_table_recursive(root, '', table)
    return table


def encode(text):
    '''Encode string to Huffman code
    text: input string

    return string of 0s and 1s (example: '1001101')
    '''

    # Count chars in text, create nodes with these chars and heapify them with their counts
    c = Counter(text)
    nodes = [Node(count, letter, None, None) for letter, count in c.items()]
    heap = nodes.copy()
    heapify(heap)

    # Criate Huffman tree for these counts
    root = make_tree(heap)
    # Criate table of codes for Huffman tree
    table = make_table(root)

    codes = [table[c] for c in text]

    return ''.join(codes), root


def decode(code, tree):
    ''' Decode string of 0s and 1s with Huffman code
    code: string of 0s and 1s
    tree: root Node

    '''
    result = []
    node = tree
    for c in code:
        if c == '0':
            node = node.left
        else:
            node = node.right

        if is_leaf(node):
            result.append(node.letter)
            node = tree

    return ''.join(result)


def tree_for_compression(tree):
    '''Remove count field from tree
    '''
    letter = tree.letter
    left = tree_for_compression(tree.left) if tree.left else None
    right = tree_for_compression(tree.right) if tree.right else None

    return CompressNode(letter, left, right)


def list_to_tree(l):
    '''json.load return list
    Then create CompressNode tree from this recursino lists
    '''

    letter = l[0]
    left = list_to_tree(l[1]) if l[1] else None
    right = list_to_tree(l[2]) if l[2] else None

    return CompressNode(letter, left, right)


def encode_to_files(text, codefile='output.huff', treefile='output.tree'):
    '''Encode string to Huffman code.
    Then create file for code and file for Huffman tree
    '''
    code, tree = encode(text)

    prefix_len = len(code) % 8

    data = []

    for i in range(len(code) // 8):
        byte = code[prefix_len + 8 * i: prefix_len + 8 * (i+1)]
        data.append(int(byte, 2))

    data = [prefix_len, int(code[:prefix_len], 2)] + data
    data = bytes(data)

    with open(codefile, 'wb') as file:
        file.write(data)

    with open(treefile, 'w') as file:
        json.dump(tree_for_compression(tree), file)


def byte_to_bits(byte):
    '''Get byte and return string of 1s and 0s with length = 8
    '''
    result = ['1' if byte & (1 << (7-n)) else '0' for n in range(8)]
    return ''.join(result)


def decode_from_files(codefile, treefile):
    '''Decode string from huffman code from codefile.
    We also need file, wich store Huffman tree.
    '''

    with open(treefile, 'rb') as file:
        lst = json.load(file)
        tree = list_to_tree(lst)

    with open(codefile, 'rb') as file:
        bts = file.read()
        prefix_len =  int(bts[0])

        codes = [byte_to_bits(x) for x in bts[1:]]
        codes[0] = codes[0][-prefix_len:]

        return decode(''.join(codes), tree)
