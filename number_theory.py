# number_theory.py
# Euclidean and Extended Euclidean Algorithm

def gcd(a, b):
    """
    Compute the Greatest Common Divisor of a and b using Euclidean Algorithm
    Returns: (gcd, steps)
    """
    a = abs(int(a))
    b = abs(int(b))

    steps = []
    # Enforce first value >= second; if not, swap and record
    if a < b:
        steps.append(f"Input ordered as ({a}, {b}) — swapping to ({b}, {a}) for algorithm.")
        a, b = b, a

    if b == 0:
        steps.append(f"{a} = {a} × 1 + 0")
        return a, steps

    original_a, original_b = a, b

    while b != 0:
        q = a // b
        r = a % b
        steps.append(f"{a} = {b} × {q} + {r}")
        a, b = b, r

    return a, steps


def extended_gcd(a, b):
    """
    Extended Euclidean Algorithm
    Finds gcd(a, b) and coefficients x, y such that ax + by = gcd(a,b)
    Returns: (gcd, x, y, steps)
    """
    # Keep originals for final reporting
    orig_a, orig_b = int(a), int(b)

    # Work with absolute values for the algorithm
    A = abs(orig_a)
    B = abs(orig_b)

    steps = []
    swapped = False
    if A < B:
        steps.append(f"Input ordered as ({A}, {B}) — swapping to ({B}, {A}) for algorithm.")
        A, B = B, A
        swapped = True

    # Store divisions
    divisions = []
    a_val, b_val = A, B
    if b_val == 0:
        steps.append(f"{a_val} = {a_val} × 1 + 0")
        gcd_value = a_val
        # coefficients
        x_res = 1
        y_res = 0
        # Map back if swapped
        if swapped:
            x_res, y_res = y_res, x_res
        # Adjust signs to match originals
        if orig_a < 0: x_res = -x_res
        if orig_b < 0: y_res = -y_res
        steps.append(f"\n=== Result ===")
        steps.append(f"{orig_a} × ({x_res}) + {orig_b} × ({y_res}) = {gcd_value}")
        return gcd_value, x_res, y_res, steps

    while b_val != 0:
        q = a_val // b_val
        r = a_val % b_val
        divisions.append((a_val, b_val, q, r))
        a_val, b_val = b_val, r

    gcd_value = a_val

    # Extended algorithm - forward iteration (standard coefficients)
    old_r, r = A, B
    old_s, s = 1, 0
    old_t, t = 0, 1

    steps.append("=== Euclidean Algorithm (Forward Pass) ===")
    for A_v, B_v, q, remainder in divisions:
        steps.append(f"{A_v} = {B_v} × {q} + {remainder}")

    steps.append(f"\nGCD = {gcd_value}\n=== Extended Euclidean Algorithm (Forward Iteration) ===\nInitialize: \n old_r = {A}, r = {B}\n old_s = 1, s = 0\n old_t = 0, t = 1")
 
    # Recompute with coefficient tracking for display
    old_r, r = A, B
    old_s, s = 1, 0
    old_t, t = 0, 1
    iteration = 0
    
    while r != 0:
        quotient = old_r // r
        iteration += 1      
        new_r = old_r - quotient * r
        new_s = old_s - quotient * s
        new_t = old_t - quotient * t
        old_r, r = r, new_r
        old_s, s = s, new_s
        old_t, t = t, new_t
        steps.append(f"\nIteration {iteration}: \n quotient = {old_r} ÷ {r} = {quotient} \n new_r = {old_r} - {quotient} × {r} = {new_r} \n new_s = {old_s} - {quotient} × {s} = {new_s} \n new_t = {old_t} - {quotient} × {t} = {new_t} \n After swap: old_r={old_r}, r={r}, old_s={old_s}, s={s}, old_t={old_t}, t={t}")

    steps.append(f"\n=== Final Coefficients (before sign adjustment) ===\n x = {old_s}, y = {old_t}")
    
    # Coefficients relative to A and B
    x_coeff, y_coeff = old_s, old_t

    # If inputs were swapped for algorithm, map coefficients back to original order
    if swapped:
        x_coeff, y_coeff = y_coeff, x_coeff

    # Adjust signs according to original signs
    if orig_a < 0:
        x_coeff = -x_coeff
    if orig_b < 0:
        y_coeff = -y_coeff

    steps.append(f"\n=== Result ===\n{orig_a} × ({x_coeff}) + {orig_b} × ({y_coeff}) = {gcd_value}\nVerification: {orig_a} × {x_coeff} + {orig_b} × {y_coeff} = {orig_a * x_coeff + orig_b * y_coeff}")

    return gcd_value, x_coeff, y_coeff, steps


def compute_gcd_display(a, b):
    """Wrapper for displaying GCD computation"""
    try:
        gcd_val, steps = gcd(a, b)
        return {
            'gcd': gcd_val,
            'steps': steps,
            'error': None
        }
    except Exception as e:
        return {
            'gcd': None,
            'steps': [],
            'error': str(e)
        }


def compute_extended_gcd_display(a, b):
    """Wrapper for displaying Extended GCD computation"""
    try:
        gcd_val, x, y, steps = extended_gcd(a, b)
        return {
            'gcd': gcd_val,
            'x': x,
            'y': y,
            'steps': steps,
            'equation': f"{int(a)}×({x}) + {int(b)}×({y}) = {gcd_val}",
            'error': None
        }
    except Exception as e:
        return {
            'gcd': None,
            'x': None,
            'y': None,
            'steps': [],
            'equation': None,
            'error': str(e)
        }
