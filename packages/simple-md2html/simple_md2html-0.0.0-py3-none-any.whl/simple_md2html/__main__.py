from .md2html import get_html_content_for_markdown
import sys
import argparse
import os

def main():
    # Create argument parser
    parser = argparse.ArgumentParser(
        description='Process the specified markdown file and output as an HTML file',
        formatter_class=argparse.RawTextHelpFormatter
    )
    
    # Add required input file argument (positional argument)
    parser.add_argument(
        'input_file',
        help='Input filename to be processed (required argument)'
    )
    
    # Add optional output file argument (-o)
    parser.add_argument(
        '-o', '--output',
        default='a.html',  # Default output filename
        help='Specify the output HTML filename (default: a.html)'
    )
    
    # Parse command line arguments
    args = parser.parse_args()
    
    # Check if file exist
    if not os.path.isfile(args.input_file):
        sys.stderr.write(f"{args.input_file}: input file not found.\n")
        sys.exit(1)

    # Processing logic
    with open(args.input_file, 'r', encoding='utf-8') as f_in:
        content = f_in.read()
    with open(args.output, 'w', encoding='utf-8') as f_out:
        f_out.write(get_html_content_for_markdown(content))

if __name__ == '__main__':
    main()
