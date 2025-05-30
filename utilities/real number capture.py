from talon import Context,Module

mod = Module()


@mod.capture(rule="[(minus|negative)] <number> [point <number_small>+]")
def real_number(m) -> float:
    """a spoken float"""
    m = list(m)
    if len(m) == 1:
        # positive integer
        return float(m[0])
    if "point" in m:
        # decimal
        pos = list(m).index("point")
        decimal_part = int("".join([str(x) for x in m[pos + 1:]]))
        num_digits_after_decimal = len(str(decimal_part))
        decimal_part = decimal_part/(10**num_digits_after_decimal)
        if pos == 1:
            # positive decimal
            return float(m[0]) + decimal_part
        else:
            # negative decimal
            power_of_ten = 10**len(str(m[3]))
            return -1 * (float(m[1]) + decimal_part)
    else:
        # negative integer
        return -1 * float(m[1])
