# hill_cipher.py
import math
from crypto_utils import char_to_index, index_to_lower_char, index_to_upper_char

MOD = 26

def mod(n, m=MOD): return ((n % m) + m) % m

def parse_square_matrix(text, size=None):
    """Parse a square matrix from space/comma separated numbers.

    If size is provided (int or string convertible), it ensures exactly size*size entries.
    If size is None or empty string, it will infer size if the number of tokens is a perfect square.
    """
    tokens = text.replace(',', ' ').split()
    if not tokens:
        raise ValueError("Matrix input is empty.")

    if size is None or size == '':
        # infer size from number of tokens
        l = len(tokens)
        import math
        root = int(math.isqrt(l))
        if root * root != l:
            raise ValueError("Number of entries is not a perfect square; provide explicit size or a proper key text.")
        size = root
    else:
        try: size = int(size)
        except: raise ValueError("Size must be an integer.")
        if size <= 0: raise ValueError("Dimension must be positive.")

    if len(tokens) != size * size:
        raise ValueError(f"Expected {size*size} values, got {len(tokens)}.")

    matrix = []
    it = iter(tokens)
    try:
        for _ in range(size):
            matrix.append([int(next(it)) for _ in range(size)])
    except ValueError:
        raise ValueError("Matrix entries must be integers (space-separated).")
    return matrix


def parse_key_text(text, size=None):
    """Create a square key matrix from text. Letters a-z are used (a=0..z=25).

    If size is None, the length of the letters must be a perfect square and size inferred.
    If size is provided and there are fewer letters than needed the key is padded with 'x'.
    Extra letters are truncated.
    """
    indices = [char_to_index(c) for c in text if char_to_index(c) != -1]
    if not indices:
        raise ValueError("Key text must contain letters a-z.")

    if size is None:
        import math
        l = len(indices)
        root = int(math.isqrt(l))
        if root * root != l:
            raise ValueError("Key length must be a perfect square when size is not provided.")
        size = root
    else:
        try: size = int(size)
        except: raise ValueError("Size must be an integer.")
        if size <= 0: raise ValueError("Size must be positive.")
        needed = size * size
        if len(indices) < needed:
            indices += [char_to_index('x')] * (needed - len(indices))
        elif len(indices) > needed:
            indices = indices[:needed]

    matrix = []
    it = iter(indices)
    for _ in range(size):
        matrix.append([next(it) for _ in range(size)])
    return matrix


def determinant(m):
    if len(m) == 1: return m[0][0]
    if len(m) == 2: return m[0][0]*m[1][1] - m[0][1]*m[1][0]
    det = 0
    for c in range(len(m)):
        det += ((-1)**c) * m[0][c] * determinant([row[:c] + row[c+1:] for row in m[1:]])
    return det

def transpose(m):
    return [[m[j][i] for j in range(len(m))] for i in range(len(m[0]))]

def cofactor_matrix(m):
    n = len(m)
    cof = [[0]*n for _ in range(n)]
    for r in range(n):
        for c in range(n):
            minor = [row[:c] + row[c+1:] for row in (m[:r] + m[r+1:])]
            cof[r][c] = ((-1)**(r+c)) * determinant(minor)
    return cof

def extended_gcd(a, b):
    old_r, r = a, b
    old_s, s = 1, 0
    while r != 0:
        q = old_r // r
        old_r, r = r, old_r - q * r
        old_s, s = s, old_s - q * s
    return old_r, old_s

def mod_inverse(a, m=MOD):
    g, x = extended_gcd(a, m)
    if g != 1: raise ValueError(f"No inverse for {a} mod {m} (gcd={g}).")
    return mod(x, m)

def inverse_matrix_mod26(m):
    det = determinant(m)
    det_inv = mod_inverse(det, 26)
    cof = cofactor_matrix(m)
    adj = transpose(cof)
    return [[mod(val * det_inv, 26) for val in row] for row in adj]

def encrypt_hill(plaintext, matrix):
    """Encrypt and return step information (without determinant/cofactor/inverse).

    Returns a dict with keys:
      - text: ciphertext (string)
      - matrix: key matrix
      - blocks: list of dicts describing each block multiplication
    """
    n = len(matrix)

    indices = [char_to_index(c) for c in plaintext if char_to_index(c) != -1]
    if not indices:
        raise ValueError("No valid letters in plaintext.")
    while len(indices) % n != 0:
        indices.append(char_to_index('x'))

    res = ""
    blocks = []
    for i in range(0, len(indices), n):
        vec = indices[i:i+n]
        block_info = {'vec': vec, 'products': [], 'sums': [], 'sums_mod': [], 'letters': []}
        # For each output component (column j)
        for j in range(n):
            products = [vec[k] * matrix[k][j] for k in range(n)]
            s = sum(products)
            s_mod = mod(s)
            letter = index_to_upper_char(s_mod)
            block_info['products'].append(products)
            block_info['sums'].append(s)
            block_info['sums_mod'].append(s_mod)
            block_info['letters'].append(letter)
        blocks.append(block_info)
        res += "".join(block_info['letters'])

    return {
        'text': res,
        'matrix': matrix,
        'blocks': blocks,
    }


def decrypt_hill(ciphertext, matrix):
    """Decrypt and return detailed step information.

    Returns dict which includes determinant/cofactor/inverse according to the formula and shows multiplication with inverse matrix.
    """
    n = len(matrix)

    # determinant and related values per formula (useful for students tracing the inverse)
    det = determinant(matrix)
    det_mod = mod(det)
    det_inv = None
    try:
        det_inv = mod_inverse(det_mod)
    except Exception:
        det_inv = None

    cof = cofactor_matrix(matrix)
    adj = transpose(cof)

    inv_matrix = inverse_matrix_mod26(matrix)

    indices = [char_to_index(c) for c in ciphertext if char_to_index(c) != -1]
    if len(indices) % n != 0:
        raise ValueError("Ciphertext length invalid.")

    res = ""
    blocks = []
    for i in range(0, len(indices), n):
        vec = indices[i:i+n]
        block_info = {'vec': vec, 'products': [], 'sums': [], 'sums_mod': [], 'letters': []}
        for j in range(n):
            # use inv_matrix for decryption
            products = [vec[k] * inv_matrix[k][j] for k in range(n)]
            s = sum(products)
            s_mod = mod(s)
            letter = index_to_lower_char(s_mod)
            block_info['products'].append(products)
            block_info['sums'].append(s)
            block_info['sums_mod'].append(s_mod)
            block_info['letters'].append(letter)
        blocks.append(block_info)
        res += "".join(block_info['letters'])

    return {
        'text': res,
        'matrix': matrix,
        'det': det,
        'det_mod': det_mod,
        'det_inv': det_inv,
        'cofactor': cof,
        'adjugate': adj,
        'inv_matrix': inv_matrix,
        'blocks': blocks,
    }