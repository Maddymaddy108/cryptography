import math

# ---------- Left Rotate ----------
def left_rotate(x, c):
    return ((x << c) | (x >> (32 - c))) & 0xFFFFFFFF

# ---------- Padding Function ----------
def pad_message(message, steps):
    msg = bytearray(message, 'utf-8')
    length_in_bytes = len(msg)
    length_in_bits = length_in_bytes * 8
    original_len_bits = length_in_bits & 0xFFFFFFFFFFFFFFFF

    msg.append(0x80)
    while (len(msg) * 8) % 512 != 448:
        msg.append(0)

    msg += original_len_bits.to_bytes(8, byteorder='little')
    steps.append(f"[Pad] original length (bits)={length_in_bits}, padded length (bits)={len(msg)*8}")
    steps.append(f"[Pad] padded bytes: {msg.hex()}")
    return msg

# ---------- Initialize Buffers ----------
def init_buffers(steps):
    A = 0x67452301
    B = 0xefcdab89
    C = 0x98badcfe
    D = 0x10325476
    steps.append(f"[Init] A={A:08x}, B={B:08x}, C={C:08x}, D={D:08x}")
    return A, B, C, D

# ---------- Generate Constants ----------
def generate_constants(steps):
    K = [int(abs(math.sin(i + 1)) * (2**32)) & 0xFFFFFFFF for i in range(64)]
    s = [7,12,17,22]*4 + [5,9,14,20]*4 + [4,11,16,23]*4 + [6,10,15,21]*4
    steps.append("[Constants] K and shift amounts generated")
    return K, s

# ---------- Process Chunk ----------
def process_chunk(chunk, A, B, C, D, K, s, chunk_idx, steps):
    a, b, c, d = A, B, C, D
    steps.append(f"[Chunk {chunk_idx}] Starting chunk processing")

    W = [0] * 16
    for i in range(16):
        W[i] = int.from_bytes(chunk[i*4 : i*4+4], 'little')
    steps.append(f"[Chunk {chunk_idx}] W words:")
    for i in range(16):
        steps.append(f"   W[{i}] = {W[i]:08x}")

    for i in range(64):
        if i <= 15:
            f = (b & c) | (~b & d)
            g = i
        elif i <= 31:
            f = (d & b) | (~d & c)
            g = (5*i + 1) % 16
        elif i <= 47:
            f = b ^ c ^ d
            g = (3*i + 5) % 16
        else:
            f = c ^ (b | ~d)
            g = (7*i) % 16

        temp = d
        d = c
        c = b
        b = (b + left_rotate((a + f + K[i] + W[g]) & 0xFFFFFFFF, s[i])) & 0xFFFFFFFF
        a = temp

        if i % 8 == 0:
            steps.append(f"   [Round {i:2d}] a={a:08x}, b={b:08x}, c={c:08x}, d={d:08x}, f={f&0xFFFFFFFF:08x}, g={g}, W[g]={W[g]:08x}, K[i]={K[i]:08x}")

    A = (A + a) & 0xFFFFFFFF
    B = (B + b) & 0xFFFFFFFF
    C = (C + c) & 0xFFFFFFFF
    D = (D + d) & 0xFFFFFFFF
    steps.append(f"[Chunk {chunk_idx}] After chunk: A={A:08x}, B={B:08x}, C={C:08x}, D={D:08x}")

    return A, B, C, D

# ---------- Combine Hash ----------
def combine_hash(A, B, C, D, steps):
    digest = ''.join(x.to_bytes(4, 'little').hex() for x in [A, B, C, D])
    steps.append(f"[Combine] Final digest: {digest}")
    return digest

# ---------- Main MD5 Function ----------
def compute_md5_steps(message):
    steps = []
    steps.append("=== MD5 COMPUTATION START ===")
    msg = pad_message(message, steps)
    A, B, C, D = init_buffers(steps)
    K, s = generate_constants(steps)

    for i in range(0, len(msg), 64):
        chunk = msg[i:i+64]
        A, B, C, D = process_chunk(chunk, A, B, C, D, K, s, i//64, steps)

    digest = combine_hash(A, B, C, D, steps)
    steps.append("=== MD5 COMPUTATION END ===")
    return digest, steps

# ---------- CLI Driver ----------
if __name__ == '__main__':
    message = input("Enter message: ")
    digest, steps = compute_md5_steps(message)
    print("MD5 Hash:", digest)
    for line in steps:
        print(line)

