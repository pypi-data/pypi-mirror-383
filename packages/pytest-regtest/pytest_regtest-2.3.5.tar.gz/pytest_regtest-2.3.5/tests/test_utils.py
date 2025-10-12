from pytest_regtest.utils import highlight_mismatches


def test_highlight_mismatches(regtest):
    lines_1 = [
        "- 111 222 333 444 555",
        "- 111 222 333 444 555",
        "- 111 222 333 444 555",
        "",
    ]
    lines_2 = [
        "+ 111 xxx 333 444 555",
        "- 111 222 333 444 55x",
        "x 111 222 333 444 555",
        "",
    ]

    for l1, l2 in zip(lines_1, lines_2):
        l1, l2 = highlight_mismatches(l1, l2)
        print(l1, file=regtest)
        print(l2, file=regtest)
