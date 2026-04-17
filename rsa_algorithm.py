# rsa_algorithm.py
# RSA with detailed key generation and binary exponentiation trace

import math
from number_theory import extended_gcd

def mod_inverse(e, phi):
    gcd_val, x, y, _ = extended_gcd(e, phi)
    if gcd_val != 1:
        raise ValueError("e and phi(n) are not coprime.")
    return x % phi

def fermat_primality_test(n):
    steps = []
    steps.append(f"=== Fermat's Primality Test for {n} ===")

    if n <= 1:
        steps.append("Number must be greater than 1.")
        return False, steps

    if n == 2:
        steps.append("2 is prime.")
        return True, steps

    base = 2
    steps.append(f"Using base a = {base}")

    gcd_val = math.gcd(base, n)
    steps.append(f"gcd({base}, {n}) = {gcd_val}")

    if gcd_val != 1:
        steps.append(f"Since gcd ≠ 1 → {n} is NOT prime.")
        return False, steps

    # Standard Fermat check
    result = pow(base, n - 1, n)
    steps.append(f"Compute {base}^{n-1} mod {n}")
    steps.append(f"{base}^{n-1} mod {n} = {result}")

    if result == 1:
        steps.append(f"Since result = 1 → {n} is probably prime.")
        return True, steps
    else:
        steps.append(f"Since result ≠ 1 → {n} is NOT prime.")
        return False, steps

def binary_exponentiation_trace(base, exponent, mod):
    steps = []
    steps.append(f"Compute {base}^{exponent} mod {mod}")

    # -------- Binary Table --------
    powers_of_two = []
    temp = 1
    while temp <= exponent:
        powers_of_two.append(temp)
        temp *= 2

    powers_of_two.reverse()

    binary_line = []
    remaining = exponent

    for p in powers_of_two:
        if remaining >= p:
            binary_line.append(1)
            remaining -= p
        else:
            binary_line.append(0)

    steps.append("Binary representation of exponent:")
    steps.append(" ".join(f"{p:>4}" for p in powers_of_two))
    steps.append(" ".join(f"{b:>4}" for b in binary_line))

    # -------- Repeated Squaring --------
    steps.append("Repeated squaring:")

    power_values = {}
    power_values[1] = base % mod
    steps.append(f"{base}^1 mod {mod} = {power_values[1]}")

    power = 1
    while power * 2 <= exponent:
        prev = power
        power *= 2

        # mathematical identity
        steps.append(f"{base}^{power} = ({base}^{prev})^2")

        # numeric exponentiation result before mod
        raw_value = power_values[prev] ** 2
        steps.append(f"{base}^{power} = {raw_value}")

        # modulo reduction
        mod_value = raw_value % mod
        power_values[power] = mod_value
        steps.append(f"{base}^{power} mod {mod} = {mod_value}")

    # -------- Multiply Selected Powers --------
    steps.append("Selected powers:")
    result = 1
    expression = []

    for p, bit in zip(powers_of_two, binary_line):
        if bit == 1:
            expression.append(f"{base}^{p}")
            steps.append(f"Using {base}^{p} = {power_values[p]}")
            result = (result * power_values[p]) % mod

    if expression:
        steps.append(f"{base}^{exponent} = " + " × ".join(expression))

    steps.append(f"Final result = {result}")

    return result, steps


def rsa_key_generation(p, q, e):
    steps = []
    # Check p
    is_prime_p, p_steps = fermat_primality_test(p)
    steps.extend(p_steps)
    if not is_prime_p:
        raise ValueError("p failed Fermat primality test.")

    # Check q
    is_prime_q, q_steps = fermat_primality_test(q)
    steps.extend(q_steps)
    if not is_prime_q:
        raise ValueError("q failed Fermat primality test.")

    steps.append("Both p and q passed Fermat's Test.\n")

    steps.append("Both p and q passed Fermat's Test.\n=== RSA Key Generation ===")
    n = p * q
    steps.append(f"n = p × q = {p} × {q} = {n}")

    phi = (p - 1) * (q - 1)
    steps.append(f"phi(n) = (p-1)(q-1) = {phi}")

    gcd_val = math.gcd(e, phi)
    steps.append(f"Check gcd({e}, {phi}) = {gcd_val}")

    if gcd_val != 1:
        raise ValueError("e must be coprime with phi(n)")

    d = mod_inverse(e, phi)
    steps.append(f"d = e⁻¹ mod phi(n) = {d}")

    steps.append(f"\nPublic Key: ({e}, {n})")
    steps.append(f"Private Key: ({d}, {n})")

    return {
        "n": n,
        "phi": phi,
        "d": d,
        "steps": steps
    }


def rsa_encrypt_auto(message, e, n):
    steps = []

    # -------- Case 1: Only Digits --------
    if message.isdigit():
        steps.append("Input detected as numeric message.")
        number = int(message)
        steps.append(f"Encrypting number directly: {number}")
        cipher, exp_steps = binary_exponentiation_trace(number, e, n)
        steps.extend(exp_steps)
        return str(cipher), steps

    # -------- Case 2: Text / Mixed --------
    steps.append("Input detected as text. Converting to ASCII.")

    ascii_values = [ord(ch) for ch in message]
    for ch, val in zip(message, ascii_values):
        steps.append(f"{ch} → {val}")

    steps.append("Encrypting each ASCII value:")
    cipher_values = []

    for val in ascii_values:
        steps.append(f"\nEncrypting ASCII {val}:")
        cipher, exp_steps = binary_exponentiation_trace(val, e, n)
        cipher_values.append(cipher)
        steps.extend(exp_steps)

    cipher_string = " ".join(str(c) for c in cipher_values)
    return cipher_string, steps



def rsa_decrypt_auto(cipher_input, d, n):
    steps = []

    # If single numeric block (no spaces)
    if cipher_input.isdigit():
        steps.append("Detected single numeric ciphertext.")
        number = int(cipher_input)
        plain, exp_steps = binary_exponentiation_trace(number, d, n)
        steps.extend(exp_steps)
        return str(plain), steps

    # Multiple blocks (text case)
    steps.append("Detected multiple ciphertext blocks.")
    cipher_values = [int(x) for x in cipher_input.split()]
    decrypted_ascii = []

    for c in cipher_values:
        steps.append(f"\nDecrypting {c}:")
        plain, exp_steps = binary_exponentiation_trace(c, d, n)
        decrypted_ascii.append(plain)
        steps.extend(exp_steps)

    steps.append("ASCII to character conversion:")
    decrypted_text = ""

    for val in decrypted_ascii:
        ch = chr(val)
        steps.append(f"{val} → {ch}")
        decrypted_text += ch

    return decrypted_text, steps
