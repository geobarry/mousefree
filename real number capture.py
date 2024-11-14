from talon import Context,Module

mod = Module()


@mod.capture(rule="[(minus|negative)] <number> [point <number_small>+]")
def real_number(m) -> float:
    """a spoken float"""
    print("CAPTURE: real_number")

    m = list(m)
    if len(m) == 1:
        # positive integer
        return float(m[0])
    if "point" in m:
        # decimal
        pos = list(m).index("point")
        print(f'pos: {pos}')
        num_digits_after_decimal = len(m) - pos - 1
        decimal_part = int("".join([str(x) for x in m[pos + 1:]]))
        decimal_part = decimal_part/(10**num_digits_after_decimal)
        if pos == 1:
            # positive decimal
            print(f"m[2]: {m[2]}")
            return float(m[0]) + decimal_part
        else:
            # negative decimal
            power_of_ten = 10**len(str(m[3]))
            return -1 * (float(m[1]) + decimal_part)
    else:
        # negative integer
        return -1 * float(m[1])
