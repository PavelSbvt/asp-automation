def print_out_string(text):
    out_string_size = 150
    if len(text) % 2 != 0:
        text += " "

    output_string = "|" + " " * int((out_string_size - len(text) - 2) / 2) + text + " " * int(
        (out_string_size - len(text) - 2) / 2) + "|"
    print(output_string)

def print_separator():
    print("|" + "_" * 148 + "|")

def print_separator_points():
    print("|" + "." * 148 + "|")

def print_big_separator():
    print("|" + "=" * 148 + "|")