"""primitive_root.py
Utilities to check for primitive roots modulo n and to find them.
"""
import math


def gcd(a, b):
    while b:
        a, b = b, a % b
    return abs(a)


def prime_factors(n):
    n = abs(n)
    factors = set()
    d = 2
    while d * d <= n:
        while n % d == 0:
            factors.add(d)
            n //= d
        d += 1 if d == 2 else 2
    if n > 1:
        factors.add(n)
    return factors


def totient(n):
    if n <= 0:
        raise ValueError('n must be a positive integer')
    result = n
    for p in prime_factors(n):
        result = result // p * (p - 1)
    return result


def _is_prime_power(n):
    """Return (True, p, k) if n == p**k for some prime p and integer k>=1.
    Otherwise return (False, None, None).
    """
    if n <= 1:
        return False, None, None
    for p in prime_factors(n):
        tmp = n
        k = 0
        while tmp % p == 0:
            tmp //= p
            k += 1
        if tmp == 1:
            return True, p, k
    return False, None, None


def primitive_root_exists(n):
    """Return True if multiplicative group modulo n is cyclic (i.e., primitive roots exist)."""
    if n in (2, 4):
        return True
    is_pp, p, k = _is_prime_power(n)
    if is_pp and p != 2:
        return True
    if n % 2 == 0:
        m = n // 2
        is_pp2, p2, k2 = _is_prime_power(m)
        if is_pp2 and p2 != 2:
            return True
    return False


def get_primitive_roots_info(n, show_steps=True, max_step_lines=5000):
    """Return information about primitive roots modulo n.

    This function collects intermediate calculation messages under the 'steps' key. Steps are always collected by default.
    """
    if n <= 1:
        raise ValueError('Modulus must be an integer greater than 1')

    steps = [] if show_steps else None

    exists = primitive_root_exists(n)
    if show_steps:
        steps.append(f"Check primitive root existence for n={n}: {exists}")

    info = {'exists': exists, 'phi': None, 'roots': [], 'count': 0}
    if not exists:
        if show_steps:
            steps.append("No primitive roots: multiplicative group modulo n is not cyclic.")
            info['steps'] = steps
        return info

    phi = totient(n)
    info['phi'] = phi
    if show_steps:
        steps.append(f"phi({n}) = {phi}")

    # expected number of primitive roots = phi(phi(n))
    expected = totient(phi)
    info['count'] = expected
    if show_steps:
        steps.append(f"Expected number of primitive roots = phi(phi({n})) = {expected}")

    # get prime factors of phi for test
    pf = prime_factors(phi)
    if show_steps:
        steps.append(f"Prime factors of phi({n})={phi}: {sorted(pf)}")

    roots = []
    step_lines = 0
    expected_set = set(x for x in range(1, n) if gcd(x, n) == 1)

    for g in range(2, n):
        if gcd(g, n) != 1:
            if show_steps:
                steps.append(f"g={g}: gcd({g},{n}) != 1; skip")
                step_lines += 1
            continue

        if show_steps:
            steps.append(f"Testing g={g}:")
            step_lines += 1
            # show powers g^1..g^phi
            seq = []
            for k in range(1, phi + 1):
                val = pow(g, k, n)
                seq.append(val)
                steps.append(f"  {g}^{k} ≡ {val} (mod {n})")
                step_lines += 1
                if step_lines >= max_step_lines:
                    break

            # summary of produced values
            seq_display = "{" + ", ".join(str(x) for x in seq) + "}"
            steps.append(f"  Result: The powers of {g} produce {seq_display}.")
            step_lines += 1

            # decide primitive root by comparing sets
            seq_set = set(seq)
            if seq_set == expected_set:
                steps.append(f"  Thus {g} is a primitive root modulo {n}.")
                roots.append(g)
                step_lines += 1
            else:
                steps.append(f"  Thus {g} is NOT a primitive root modulo {n}.")
                step_lines += 1

        else:
            # faster check when steps not requested (use prime-factor exponent test)
            good = True
            for q in sorted(pf):
                val = pow(g, phi // q, n)
                if val == 1:
                    good = False
                    break
            if good:
                roots.append(g)

        # truncate steps if too long
        if show_steps and step_lines >= max_step_lines:
            steps.append("... (steps truncated due to length) ...")
            info['steps_truncated'] = True
            break

    info['roots'] = roots
    if show_steps:
        info['steps'] = steps
    return info


if __name__ == '__main__':
    # Quick manual test
    import sys
    if len(sys.argv) > 1:
        n = int(sys.argv[1])
        info = get_primitive_roots_info(n)
        print(info)
    else:
        print('Usage: python primitive_root.py <n>')
