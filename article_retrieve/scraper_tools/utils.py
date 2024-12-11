'''Helper functions for the scraper'''
import os
import subprocess


def open_chrome(chrome_path):
    try:
        os.chdir(chrome_path)
        arguments = ["--remote-debugging-port=9222", "--no-remote"]
        if os.name == "nt":
            subprocess.Popen(["chrome.exe"]+arguments)
        elif os.name == "posix":
            subprocess.Popen(["google-chrome"]+arguments)
        print("Chrome opened successfully.")
    except FileNotFoundError:
        print(f"The directory {chrome_path} does not exist. Please check the path.")
    except subprocess.CalledProcessError as e:
        print(f"Failed to open Chrome: {e}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")


def read_doi_file(path):
    with open(path, 'r') as f:
        dois = f.readlines()
    doi_list = [doi.strip() for doi in dois]
    return doi_list


def make_batches(doi_list, batch_size=50):
    batches = [doi_list[i:i+batch_size] for i in range(0, len(doi_list), batch_size)]
    return batches