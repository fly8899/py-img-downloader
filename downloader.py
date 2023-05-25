import requests
import os
import sys
import concurrent.futures
from urlextract import URLExtract
import uuid 

threadpool = concurrent.futures.ThreadPoolExecutor(max_workers=20)
image_directory = "images"
utf = "utf-32"
headers = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 13_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/113.0.0.0 Safari/537.36"
}

def is_img_url(url: str) -> bool:
    return url.endswith(".png") or url.endswith(".jpg") or url.endswith(".jpeg") or url.endswith(".svg")

def parse_text_file_for_image_urls(file, encoding = utf) -> set[str]: 
    extractor = URLExtract()
    lines = open(file, encoding = encoding).readlines()
    result = set()
    iter = threadpool.map(extractor.find_urls, lines)
    
    for list in iter:
        for valid_url in [url for url in list if is_img_url(url)]:
            result.add(valid_url)

    return result

def write_file(name: str, content: str, mode: str, encoding: str = None):
    file = open(name, mode, encoding = encoding)
    file.write(content)
    file.flush()
    os.fsync(file.fileno())
    file.close()

def get_response(url: str) -> requests.Response:
    return requests.get(url, headers=headers)

def get_random_string() -> str:
    return uuid.uuid4().hex[:20].upper()

def get_file_type(url: str) -> str:
    return url[::-1].split(".", maxsplit = 1).pop(0)[::-1]

def get_image_name(file_type: str) -> str:
    return image_directory + '/' + get_random_string() + '.' + file_type

def download_and_persist_image(url: str):
    try:
        bytes = get_response(url).content
        file_type = get_file_type(url)
        write_file(get_image_name(file_type), bytes, "wb")
        print("Saved: " + url)
    except:
        print("Skipping: " + url)
    
def main():
    print("Checking setup.")

    if not sys.argv[1:]:
        print("No arguments passed.")
        return

    if os.path.exists(image_directory):
        print("Skipping folder creation.")
    else: 
        print("Creating images folder.")
        os.mkdir(image_directory)

    website_target_url = sys.argv[1:].pop(0)
    print("Connecting to: " + website_target_url)

    website_text = get_response(website_target_url).text
    website_text_file_name = "page_content.txt"

    write_file(website_text_file_name, website_text, "w", utf)
    urls = parse_text_file_for_image_urls(website_text_file_name)
    
    threadpool.map(download_and_persist_image, urls, timeout=10)
    threadpool.shutdown(wait = True)

    print("Done.")

main()