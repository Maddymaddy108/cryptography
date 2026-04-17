# des_single.py
# Single-DES (64-bit block) with key schedule and detailed tracing

# Permutation and S-box tables
IP = [58,50,42,34,26,18,10,2,
      60,52,44,36,28,20,12,4,
      62,54,46,38,30,22,14,6,
      64,56,48,40,32,24,16,8,
      57,49,41,33,25,17,9,1,
      59,51,43,35,27,19,11,3,
      61,53,45,37,29,21,13,5,
      63,55,47,39,31,23,15,7]

FP = [40,8,48,16,56,24,64,32,
      39,7,47,15,55,23,63,31,
      38,6,46,14,54,22,62,30,
      37,5,45,13,53,21,61,29,
      36,4,44,12,52,20,60,28,
      35,3,43,11,51,19,59,27,
      34,2,42,10,50,18,58,26,
      33,1,41,9,49,17,57,25]

E = [32,1,2,3,4,5,
     4,5,6,7,8,9,
     8,9,10,11,12,13,
     12,13,14,15,16,17,
     16,17,18,19,20,21,
     20,21,22,23,24,25,
     24,25,26,27,28,29,
     28,29,30,31,32,1]

P = [16,7,20,21,29,12,28,17,
     1,15,23,26,5,18,31,10,
     2,8,24,14,32,27,3,9,
     19,13,30,6,22,11,4,25]

SBOX = [
# S1
[14,4,13,1,2,15,11,8,3,10,6,12,5,9,0,7,
 0,15,7,4,14,2,13,1,10,6,12,11,9,5,3,8,
 4,1,14,8,13,6,2,11,15,12,9,7,3,10,5,0,
 15,12,8,2,4,9,1,7,5,11,3,14,10,0,6,13],
# S2
[15,1,8,14,6,11,3,4,9,7,2,13,12,0,5,10,
 3,13,4,7,15,2,8,14,12,0,1,10,6,9,11,5,
 0,14,7,11,10,4,13,1,5,8,12,6,9,3,2,15,
 13,8,10,1,3,15,4,2,11,6,7,12,0,5,14,9],
# S3
[10,0,9,14,6,3,15,5,1,13,12,7,11,4,2,8,
 13,7,0,9,3,4,6,10,2,8,5,14,12,11,15,1,
 13,6,4,9,8,15,3,0,11,1,2,12,5,10,14,7,
 1,10,13,0,6,9,8,7,4,15,14,3,11,5,2,12],
# S4
[7,13,14,3,0,6,9,10,1,2,8,5,11,12,4,15,
 13,8,11,5,6,15,0,3,4,7,2,12,1,10,14,9,
 10,6,9,0,12,11,7,13,15,1,3,14,5,2,8,4,
 3,15,0,6,10,1,13,8,9,4,5,11,12,7,2,14],
# S5
[2,12,4,1,7,10,11,6,8,5,3,15,13,0,14,9,
 14,11,2,12,4,7,13,1,5,0,15,10,3,9,8,6,
 4,2,1,11,10,13,7,8,15,9,12,5,6,3,0,14,
 11,8,12,7,1,14,2,13,6,15,0,9,10,4,5,3],
# S6
[12,1,10,15,9,2,6,8,0,13,3,4,14,7,5,11,
 10,15,4,2,7,12,9,5,6,1,13,14,0,11,3,8,
 9,14,15,5,2,8,12,3,7,0,4,10,1,13,11,6,
 4,3,2,12,9,5,15,10,11,14,1,7,6,0,8,13],
# S7
[4,11,2,14,15,0,8,13,3,12,9,7,5,10,6,1,
 13,0,11,7,4,9,1,10,14,3,5,12,2,15,8,6,
 1,4,11,13,12,3,7,14,10,15,6,8,0,5,9,2,
 6,11,13,8,1,4,10,7,9,5,0,15,14,2,3,12],
# S8
[13,2,8,4,6,15,11,1,10,9,3,14,5,0,12,7,
 1,15,13,8,10,3,7,4,12,5,6,11,0,14,9,2,
 7,11,4,1,9,12,14,2,0,6,10,13,15,3,5,8,
 2,1,14,7,4,10,8,13,15,12,9,0,3,5,6,11]
]

PC1 = [57,49,41,33,25,17,9,
       1,58,50,42,34,26,18,
       10,2,59,51,43,35,27,
       19,11,3,60,52,44,36,
       63,55,47,39,31,23,15,
       7,62,54,46,38,30,22,
       14,6,61,53,45,37,29,
       21,13,5,28,20,12,4]

PC2 = [14,17,11,24,1,5,
       3,28,15,6,21,10,
       23,19,12,4,26,8,
       16,7,27,20,13,2,
       41,52,31,37,47,55,
       30,40,51,45,33,48,
       44,49,39,56,34,53,
       46,42,50,36,29,32]

SHIFTS = [1,1,2,2,2,2,2,2,1,2,2,2,2,2,2,1]


def _bits_from_hex_or_bin(s, expected_bits):
    s = s.strip()
    if all(c in '01' for c in s) and len(s) == expected_bits:
        return [int(b) for b in s]
    try:
        if s.startswith('0x'):
            s = s[2:]
        b = bytes.fromhex(s)
        bits = []
        for byte in b:
            bits += [(byte >> (7-i)) & 1 for i in range(8)]
        if len(bits) == expected_bits:
            return bits
    except Exception:
        pass
    return None

def _bits_to_hex(bits):
    by = 0
    res = []
    for i,b in enumerate(bits):
        by = (by<<1) | b
        if (i%8)==7:
            res.append(by)
            by = 0
    return ''.join(f"{x:02x}" for x in res)

def _bits_to_bytes(bits):
    out = []
    by = 0
    for i,b in enumerate(bits):
        by = (by<<1) | b
        if (i%8)==7:
            out.append(by)
            by = 0
    return bytes(out)

def permute(bits, table):
    return [bits[i-1] for i in table]

def left_rotate(lst, n):
    return lst[n:]+lst[:n]

def generate_subkeys(key_bits):
    # key_bits: 64 bits
    key56 = [key_bits[i-1] for i in PC1]
    C = key56[:28]
    D = key56[28:]
    subkeys = []
    for i in range(16):
        s = SHIFTS[i]
        C = left_rotate(C, s)
        D = left_rotate(D, s)
        CD = C + D
        K = [CD[j-1] for j in PC2]
        subkeys.append(K)
    return subkeys

def sbox_substitution(bits48):
    out = []
    for i in range(8):
        block = bits48[6*i:6*(i+1)]
        row = (block[0]<<1) | block[5]
        col = (block[1]<<3) | (block[2]<<2) | (block[3]<<1) | block[4]
        val = SBOX[i][16*row + col]
        out += [(val >> (3-j)) & 1 for j in range(4)]
    return out

def compute_des_trace(plaintext, key, mode='ECB', operation='ENCRYPT'):
    # parse key bits
    kb = _bits_from_hex_or_bin(key, 64)
    if kb is None:
        raise ValueError('Key must be 64-bit hex (16 hex chars) or 64-bit binary string')

    # Prepare plaintext/ciphertext blocks (list of 64-bit bit lists)
    pb_bits_blocks = []
    
    if operation.upper() == 'DECRYPT':
        # For decryption, input is hex string (ciphertext)
        try:
            b = bytes.fromhex(plaintext)
        except Exception:
            raise ValueError('For decryption, plaintext must be valid hex string (ciphertext)')
        # Split into 8-byte blocks
        blocks = [b[i:i+8] for i in range(0, len(b), 8)]
        if len(blocks) == 0:
            blocks = [b'\x00'*8]
        for bl in blocks:
            if len(bl) < 8:
                bl = bl + bytes(8-len(bl))
            bits = []
            for byte in bl:
                bits += [(byte >> (7-i)) & 1 for i in range(8)]
            pb_bits_blocks.append(bits)
    else:
        # For encryption, input is text (plaintext)
        pb_given_bits = _bits_from_hex_or_bin(plaintext, 64)
        if pb_given_bits is not None:
            pb_bits_blocks = [pb_given_bits]
        else:
            # ascii text -> bytes -> pad to 8 bytes blocks
            b = plaintext.encode('utf-8')
            blocks = [ b[i:i+8] for i in range(0, len(b), 8) ]
            if len(blocks) == 0:
                blocks = [b'\x00'*8]
            for bl in blocks:
                if len(bl) < 8:
                    bl = bl + bytes(8-len(bl))
                bits = []
                for byte in bl:
                    bits += [(byte >> (7-i)) & 1 for i in range(8)]
                pb_bits_blocks.append(bits)

    # hardcoded IV for CBC (8 bytes)
    IV_bytes = bytes.fromhex('0123456789abcdef')
    IV_bits = []
    for byte in IV_bytes:
        IV_bits += [(byte >> (7-i)) & 1 for i in range(8)]

    steps = []
    steps.append('Key (hex): ' + _bits_to_hex(kb))
    steps.append('Mode: ' + mode)
    if mode.upper() == 'CBC':
        steps.append('IV (hex): ' + IV_bytes.hex())

    subkeys = generate_subkeys(kb)

    cipher_hex_blocks = []
    prev_ct_bits = IV_bits
    for bi, plain_bits in enumerate(pb_bits_blocks):
        steps.append(f'=== Block {bi+1} ===')
        if operation.upper() == 'ENCRYPT':
            steps.append('Plaintext (hex): ' + _bits_to_hex(plain_bits))
            if mode.upper() == 'CBC':
                xored_input = [a ^ b for a,b in zip(plain_bits, prev_ct_bits)]
                steps.append('After XOR with IV/prev ciphertext: ' + _bits_to_hex(xored_input))
                block_bits = xored_input
            else:
                block_bits = plain_bits

            steps.append('After Initial Permutation (IP):')
            ip = permute(block_bits, IP)
            steps.append('IP: ' + _bits_to_hex(ip))

            L = ip[:32]
            R = ip[32:]

            for r in range(16):
                steps.append(f'--- Round {r+1} ---')
                expanded = permute(R, E)
                steps.append('Expanded R (48-bit): ' + _bits_to_hex(expanded))
                subk = subkeys[r]
                steps.append('Round subkey: ' + _bits_to_hex(subk))
                xored = [a ^ b for a,b in zip(expanded, subk)]
                steps.append('After XOR with subkey: ' + _bits_to_hex(xored))
                sboxed = sbox_substitution(xored)
                steps.append('After S-boxes (32-bit): ' + _bits_to_hex(sboxed))
                pboxed = permute(sboxed, P)
                steps.append('After P permutation: ' + _bits_to_hex(pboxed))
                newR = [a ^ b for a,b in zip(L, pboxed)]
                steps.append('New R: ' + _bits_to_hex(newR))
                L = R
                R = newR

            preoutput = R + L
            steps.append('Before Final Permutation (preoutput): ' + _bits_to_hex(preoutput))
            cipher_bits = permute(preoutput, FP)
            steps.append('Ciphertext: ' + _bits_to_hex(cipher_bits))

            cipher_hex_blocks.append(_bits_to_hex(cipher_bits))
            prev_ct_bits = cipher_bits
        else:
            # DECRYPT
            steps.append('Ciphertext (hex): ' + _bits_to_hex(plain_bits))
            ciphertext_bits = plain_bits  # Save original ciphertext
            block_bits = plain_bits

            steps.append('After Initial Permutation (IP):')
            ip = permute(block_bits, IP)
            steps.append('IP: ' + _bits_to_hex(ip))

            L = ip[:32]
            R = ip[32:]

            # use reversed subkeys for decryption
            for r in range(16):
                steps.append(f'--- Round {r+1} (using reversed subkey) ---')
                expanded = permute(R, E)
                steps.append('Expanded R (48-bit): ' + _bits_to_hex(expanded))
                subk = subkeys[15-r]
                steps.append('Round subkey: ' + _bits_to_hex(subk))
                xored = [a ^ b for a,b in zip(expanded, subk)]
                steps.append('After XOR with subkey: ' + _bits_to_hex(xored))
                sboxed = sbox_substitution(xored)
                steps.append('After S-boxes (32-bit): ' + _bits_to_hex(sboxed))
                pboxed = permute(sboxed, P)
                steps.append('After P permutation: ' + _bits_to_hex(pboxed))
                newR = [a ^ b for a,b in zip(L, pboxed)]
                steps.append('New R: ' + _bits_to_hex(newR))
                L = R
                R = newR
            preoutput = R + L
            steps.append('Before Final Permutation (preoutput): ' + _bits_to_hex(preoutput))
            decrypted_bits = permute(preoutput, FP)
            steps.append('Decrypted (pre-XOR) bits: ' + _bits_to_hex(decrypted_bits))

            if mode.upper() == 'CBC':
                plain_out = [a ^ b for a,b in zip(decrypted_bits, prev_ct_bits)]
                steps.append('After XOR with IV/prev ciphertext: ' + _bits_to_hex(plain_out))
                cipher_hex_blocks.append(_bits_to_hex(plain_out))
                prev_ct_bits = ciphertext_bits  # Update to current ciphertext for next iteration
            else:
                cipher_hex_blocks.append(_bits_to_hex(decrypted_bits))

    # assemble bytes
    out_bytes = b''
    if operation.upper() == 'ENCRYPT':
        for h in cipher_hex_blocks:
            # h may be hex string representing bytes
            out_bytes += bytes.fromhex(h)
        # For encryption, return hex string of ciphertext bytes
        out_text = out_bytes.hex()
    else:
        # cipher_hex_blocks already holds hex of plain-out bits
        for h in cipher_hex_blocks:
            out_bytes += bytes.fromhex(h)
        # strip zero padding then decode utf-8 if possible
        stripped = out_bytes.rstrip(b'\x00')
        try:
            out_text = stripped.decode('utf-8')
        except Exception:
            out_text = stripped.decode('latin-1')

    return {'ciphertext': out_text, 'steps': steps}
