def highlight_mismatches(l1, l2):
    if not l1 and not l2:
        return l1, l2

    l1 = l1.ljust(max(len(l1), len(l2)), " ")
    l2 = l2.ljust(max(len(l1), len(l2)), " ")

    chars_1 = [l1[0]]
    chars_2 = [l2[0]]
    UNDERLINE_ON = "\x1b[21m"
    UNDERLINE_OFF = "\x1b[24m"

    is_invert = False

    for c1, c2 in zip(l1[1:], l2[1:]):
        if not is_invert and c1 != c2:
            chars_1.append(UNDERLINE_ON)
            chars_2.append(UNDERLINE_ON)
            is_invert = True
        if is_invert and c1 == c2:
            chars_1.append(UNDERLINE_OFF)
            chars_2.append(UNDERLINE_OFF)
            is_invert = False
        chars_1.append(c1)
        chars_2.append(c2)
    chars_1.append(UNDERLINE_OFF)
    chars_2.append(UNDERLINE_OFF)
    return "".join(chars_1), "".join(chars_2)
