import os
import re

def find_longest_alphanumeric_sequence(line):
    alphanumeric_sequences = re.findall(r'[a-zA-Z0-9_-]+', line)
    if not alphanumeric_sequences:
        return ""
    longest_sequence = max(alphanumeric_sequences, key=len)
    return longest_sequence

def main():
    input_directory = "rawLinks"
    output_file = "GdocIDs.txt"

    # Get a list of all the files in the input directory
    input_files = [file for file in os.listdir(input_directory) if file.endswith(".txt")]

    # Sort the input files by their numerical part (if they are named like "part1.txt", "part2.txt", etc.)
    input_files.sort(key=lambda x: int(x[4:-4]) if x[4:-4].isdigit() else x)

    with open(output_file, "w") as outfile:
        for input_file in input_files:
            with open(os.path.join(input_directory, input_file), "r") as infile:
                for line in infile:
                    longest_sequence = find_longest_alphanumeric_sequence(line.strip())
                    outfile.write(longest_sequence + "\n")

            # Close the file before removing it
            infile.close()

            # Remove the processed file from the "rawLinks" directory
            os.remove(os.path.join(input_directory, input_file))

if __name__ == "__main__":
    main()
