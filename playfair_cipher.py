# playfair_cipher.py

def playfair_prep(key):
    # Remove duplicates while keeping order
    key = "".join(dict.fromkeys(c for c in key.lower() if 'a' <= c <= 'z'))
    alphabet = "abcdefghiklmnopqrstuvwxyz" # 'j' is omitted
    # Construct the 25-char grid string
    grid_str = (key + "".join(c for c in alphabet if c not in key)).replace('j', 'i')
    return grid_str

def playfair_loc(char, grid):
    idx = grid.find(char)
    return idx // 5, idx % 5

def playfair_process(text, key, mode='encrypt'):
    grid = playfair_prep(key)
    
    # 1. Prepare Matrix for Display (List of 5 strings)
    matrix_display = [grid[i:i+5].upper() for i in range(0, 25, 5)]

    # 2. Clean Text
    text = "".join(c for c in text.lower() if 'a' <= c <= 'z').replace('j', 'i')
    
    # 3. Create Pairs (Digraphs)
    pairs = []
    i = 0
    while i < len(text):
        a = text[i]
        b = text[i+1] if i+1 < len(text) else 'x'
        if a == b:
            pairs.append((a, 'x'))
            i += 1
        else:
            pairs.append((a, b))
            i += 2
    if len(pairs) > 0 and len(pairs[-1]) == 1: 
        pairs[-1] = (pairs[-1][0], 'x') # Pad last if odd length

    # 4. Process Pairs
    original_pairs_display = []
    transformed_pairs_display = []
    res_chars = []
    
    shift = 1 if mode == 'encrypt' else 4 # 4 is equivalent to -1 mod 5
    
    for a, b in pairs:
        r1, c1 = playfair_loc(a, grid)
        r2, c2 = playfair_loc(b, grid)
        
        na, nb = '', ''
        
        if r1 == r2: # Same row
            na = grid[r1*5 + (c1+shift)%5]
            nb = grid[r2*5 + (c2+shift)%5]
        elif c1 == c2: # Same col
            na = grid[((r1+shift)%5)*5 + c1]
            nb = grid[((r2+shift)%5)*5 + c2]
        else: # Rectangle
            na = grid[r1*5 + c2]
            nb = grid[r2*5 + c1]
            
        res_chars.append(na + nb)
        
        # Store display data
        original_pairs_display.append((a + b).upper())
        transformed_pairs_display.append((na + nb).upper())

    final_text = "".join(res_chars)
    if mode == 'encrypt':
        final_text = final_text.upper()
    
    return {
        "text": final_text,
        "matrix": matrix_display,
        "orig_pairs": " ".join(original_pairs_display),
        "trans_pairs": " ".join(transformed_pairs_display)
    }