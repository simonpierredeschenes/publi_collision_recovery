#! /usr/bin/python3.6

if __name__ == "__main__":
    import sys

    if len(sys.argv) != 2:
        raise RuntimeError("Incorrect number of arguments! Argument 1 is the matrix file.")

    with open(sys.argv[1]) as file:
        lines = file.readlines()
        matrix = "["
        for row_index, line in enumerate(lines):
            matrix += "["
            tokens = line[:-1].split(" ")
            col_index = 0
            for token in tokens:
                if token != "":
                    matrix += token
                    if col_index < 3:
                        matrix += ","
                    col_index += 1
            matrix += "]"
            if row_index < 3:
                matrix += ","
        matrix += "]"
        print(matrix)
