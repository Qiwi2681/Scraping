import re

def find_longest_alphanumeric_sequence(line):
    alphanumeric_sequences = re.findall(r'[a-zA-Z0-9_-]+', line)
    if not alphanumeric_sequences:
        return ""
    longest_sequence = max(alphanumeric_sequences, key=len)
    return longest_sequence

def main():
    input_file = "GdocUrls.txt"
    output_file = "GdocIDs.txt"

    with open(input_file, "r") as infile, open(output_file, "w") as outfile:
        for line in infile:
            longest_sequence = find_longest_alphanumeric_sequence(line.strip())
            outfile.write(longest_sequence + "\n")

if __name__ == "__main__":
    main()
