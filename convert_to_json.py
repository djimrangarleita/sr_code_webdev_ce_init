#!/usr/bin/env python3

import json
import argparse

def code_file_to_json(source_file, output_file="json_output.txt"):
    try:
        with open(source_file, "r", encoding="utf-8") as file:
            code = file.read()  # Read content from the source file
        
        json_string = json.dumps(code)  # Convert to JSON-compatible string
        
        with open(output_file, "w", encoding="utf-8") as file:
            file.write(json_string)  # Write JSON string to output file
        
        print(f"Code from {source_file} successfully converted to JSON and written to {output_file}.")
    
    except FileNotFoundError:
        print(f"Error: The file {source_file} was not found.")
    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Convert a code file to a JSON string and save it to an output file.")
    parser.add_argument("source_file", help="Path to the source code file")
    parser.add_argument("output_file", nargs="?", default="output.txt", help="Path to save the JSON-formatted output (default: output.txt)")

    args = parser.parse_args()
    code_file_to_json(args.source_file, args.output_file)
