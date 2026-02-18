'''
Script to get text of article from html or xml file into json file
'''
import to_json
import os
import sys
import argparse
import re
from datetime import datetime

def main():
    # Parse command line arguments
    parser = argparse.ArgumentParser(description='Extract article text from files and save as JSON')
    parser.add_argument('--data_dir', help='Directory containing the article files')
    parser.add_argument('--save_dir', help='Directory to save extracted JSON files (optional)', default=None)
    
    args = parser.parse_args()
    
    data_dir = args.data_dir
    save_dir = args.save_dir
    
    # Validate data_dir exists
    if not os.path.exists(data_dir):
        print(f"Error: Data directory '{data_dir}' does not exist.")
        sys.exit(1)
    
    # Create save_dir if not provided
    if save_dir is None:
        parent_dir = os.path.dirname(os.path.abspath(data_dir))
        save_dir = os.path.join(parent_dir, 'extracted_json')
    
    # Create save_dir if it doesn't exist
    if not os.path.exists(save_dir):
        os.makedirs(save_dir)
        print(f"Created save directory: {save_dir}")
    
    # Set up logging to file in parent directory of data_dir
    parent_dir = os.path.dirname(os.path.abspath(data_dir))
    log_filename = f"extraction_log_{datetime.now().strftime('%Y%m%d_%H%M')}.txt"
    log_path = os.path.join(parent_dir, log_filename)
    
    # Redirect stdout to both console and log file
    log_file = open(log_path, 'w')

    class Tee:
        def __init__(self, *streams):
            self.streams = streams
        def write(self, data):
            for s in self.streams:
                s.write(data)
        def flush(self):
            for s in self.streams:
                s.flush()

    original_stdout = sys.stdout
    sys.stdout = Tee(original_stdout, log_file)

    print(f"Processing files from: {data_dir}")
    print(f"Saving JSON files to: {save_dir}")
    print(f"Log file: {log_path}")
    print("-" * 80)
    
    # Find all files matching the pattern: 10.{4-9 digits} followed by any characters .txt
    pattern = re.compile(r'^10\.\d{4,9}[^\s]*\.txt$')
    all_files = os.listdir(data_dir)
    matching_files = [f for f in all_files if pattern.match(f)]

    # Print how many files found
    print(f"Found {len(matching_files)} matching files")
    print("-" * 80)

    # Check if no files found
    if len(matching_files) == 0:
        print("No matching files found. Please check the directory.")
        print("Expected pattern: 10.{4-9 digits}[any characters].txt (e.g., 10.1016-j.ccr.2014.12.019.txt)")
        sys.stdout = original_stdout
        log_file.close()
        print(f"Log file created: {log_path}")
        return
    
    # Track failed files
    failed_files = []
    successful_count = 0
    
    # Process each file
    for filename in matching_files:
        try:
            print(f"Processing: {filename}")
            success = to_json.article_extractor(filename, data_dir, save_dir)
            if success:
                successful_count += 1
            else:
                failed_files.append(filename)
        except Exception as e:
            print(f"FAILED: {filename} - Error: {str(e)}")
            failed_files.append(filename)
    
    # Print summary
    print("-" * 80)
    print(f"Processing complete!")
    print(f"Total files processed: {len(matching_files)}")
    print(f"Successful: {successful_count}")
    print(f"Failed: {len(failed_files)}")
    
    if failed_files:
        print("\nFailed files:")
        for failed_file in failed_files:
            print(f"  - {failed_file}")
    
    # Close log file and restore stdout
    sys.stdout = original_stdout
    log_file.close()
    
    print(f"Processing complete. Log file created: {log_path}")
    print(f"Processed {successful_count}/{len(matching_files)} files successfully")
    if failed_files:
        print(f"Failed files: {len(failed_files)}")


if __name__ == '__main__':
    main()
