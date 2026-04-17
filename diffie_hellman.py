import random
import math
import primitive_root
from rsa_algorithm import fermat_primality_test

def fast_exp_trace(base, exponent, mod):

    steps = []

    # ---------- Binary Representation ----------
    powers = []
    temp = 1

    while temp <= exponent:
        powers.append(temp)
        temp *= 2

    powers.reverse()

    remaining = exponent
    bits = []

    for p in powers:
        if remaining >= p:
            bits.append(1)
            remaining -= p
        else:
            bits.append(0)

    steps.append("Binary representation of exponent:")
    steps.append(" ".join(f"{p:>4}" for p in powers))
    steps.append(" ".join(f"{b:>4}" for b in bits))

    # ---------- Repeated Squaring ----------
    steps.append("Repeated squaring:")

    values = {}
    values[1] = base % mod

    steps.append(f"{base}^1 mod {mod} = {values[1]}")

    power = 1

    while power * 2 <= exponent:

        prev = power
        power *= 2

        steps.append(f"{base}^{power} = ({base}^{prev})^2")

        raw = values[prev] ** 2
        steps.append(f"{base}^{power} = {raw}")

        mod_val = raw % mod
        values[power] = mod_val
        steps.append(f"{base}^{power} mod {mod} = {mod_val}")

    # ---------- Final Multiplication ----------
    result = 1
    selected_values = []
    selected_expr = []
    for p, bit in zip(powers, bits):
        if bit == 1:
            selected_expr.append(f"{base}^{p}")
            selected_values.append(values[p])
            result = (result * values[p]) % mod
            
    # Show selected powers
    steps.append("Selected powers from binary:")

    for expr, val in zip(selected_expr, selected_values):
        steps.append(f"{expr} = {val}")

    # Show multiplication expression
    if selected_values:
        mult_expr = " × ".join(str(v) for v in selected_values)
        raw_mult = 1
        for v in selected_values:
            raw_mult *= v

        steps.append("Final multiplication:")
        steps.append(f"Result = ({mult_expr}) mod {mod}")
        steps.append(f"Result = {raw_mult} mod {mod}")
        steps.append(f"Result = {result}")

    return result, steps

def is_primitive_root(q, alpha):
    # Get primitive root information from existing module
    info = primitive_root.get_primitive_roots_info(q, show_steps=False)
    if alpha in info['roots']:
        return True
    else:
        return False

# ---------- Main Diffie Hellman ----------
def diffie_hellman_process(q, alpha, a=None, b=None):

    steps_A = []
    steps_B = []
    is_valid = is_primitive_root(q, alpha)
    s,steps= fermat_primality_test(q)
    if not s:
        raise ValueError("Q is not a prime number")
    if not is_valid:
        raise ValueError("alpha is not a primitive root of q")

    steps_A.append(f"q (prime) = {q}")
    steps_A.append(f"alpha (primitive root) = {alpha}")

    steps_B.append(f"q (prime) = {q}")
    steps_B.append(f"alpha (primitive root) = {alpha}")

    # Generate private keys if not given
    if a is None:
        a = random.randint(2, q - 2)

    if b is None:
        b = random.randint(2, q - 2)

    steps_A.append(f"Private key of A = {a}")
    steps_B.append(f"Private key of B = {b}")

    # Public key A
    steps_A.append("Compute Public Key A = alpha^a mod q")
    A, pubA_steps = fast_exp_trace(alpha, a, q)
    steps_A.extend(pubA_steps)

    # Public key B
    steps_B.append("Compute Public Key B = alpha^b mod q")
    B, pubB_steps = fast_exp_trace(alpha, b, q)
    steps_B.extend(pubB_steps)

    steps_A.append(f"Public Key of A = {A}")
    steps_B.append(f"Public Key of B = {B}")

    steps_A.append("Public keys are exchanged between A and B")
    steps_B.append("Public keys are exchanged between A and B")

    # Common key generation
    steps_A.append("Compute Common Key = B^a mod q")
    KA, KA_steps = fast_exp_trace(B, a, q)
    steps_A.extend(KA_steps)

    steps_B.append("Compute Common Key = A^b mod q")
    KB, KB_steps = fast_exp_trace(A, b, q)
    steps_B.extend(KB_steps)

    steps_A.append(f"Shared Secret Key = {KA}")
    steps_B.append(f"Shared Secret Key = {KB}")

    return {
        "A_steps": steps_A,
        "B_steps": steps_B,
        "A_public": A,
        "B_public": B,
        "key": KA
    }