import requests
import time
import os
import sys
import concurrent.futures
from urlextract import URLExtract

image_directory = "images"

def parse_text_file_for_image_links(file, encoding = "utf-8"): 
    urls = set()
    extractor = URLExtract()
    lines = open(file, encoding = encoding).readlines()

    for line in lines:
        matches = extractor.find_urls(line)
        
        for url in matches:
            if (url.endswith(".png") or url.endswith(".jpg")):
                urls.add(url)

    return urls

# str = "w", encoding = "utf-8"
# bytes = "wb"
def write_file(name, content, mode, encoding = None):
    # force new_line. (html)
    if (content is str):
        content = content.replace("/>", "\n")

    file = open(name, mode, encoding = encoding)
    file.write(content)
    file.close()

# .content = image bytes
# .text = website str
def get_response(url):
    return requests.get(url)

def get_image_name():
    return image_directory + '/' + str(time.time()) + '.jpg'

def download_and_persist_image(url):
    print("Trying: " + url)
    try: 
        bytes = get_response(url).content
        write_file(get_image_name(), bytes, "wb")
        print("Success.")
    except:
        print("Skipping.")
    
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
    print(website_target_url)   
    print("Connecting to: " + website_target_url)

    website_text = get_response(website_target_url).text
    website_text_file_name = "page_content.txt"

    write_file(website_text_file_name, website_text, "w", "utf-8")
    urls = parse_text_file_for_image_links(website_text_file_name)

    executor = concurrent.futures.ThreadPoolExecutor(max_workers=10)

    for url in urls:
        executor.submit(download_and_persist_image(url))

    executor.shutdown()

    print("Done.")

main()