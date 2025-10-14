import asyncio  # Add asyncio import
import os
import sys
import time
import json
import requests
import sys
import os
import re
import bs4
from bs4 import BeautifulSoup
import sys
import json
import time
import codecs
import cachetools
from cachetools import cached, TTLCache
from concurrent.futures import ThreadPoolExecutor, as_completed
from bs4 import BeautifulSoup
import requests
import concurrent.futures
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
import time
import json
import codecs
import time
import os, sys
import time
import random

from typing import Deque, List, Optional, Tuple, Any, Dict
from pydantic import BaseModel

import httpx
from dotenv import load_dotenv
from mcp.server.fastmcp import Context, FastMCP

import logging

logging.basicConfig(
    filename='server.log',
    level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s - %(message)s',
    filemode='a'
)

class CustomFastMCP(FastMCP):
    async def _handle_list_tools(self, context):
        # print(f"ListTools Request Details: {context.request}")
        context.info(f"ListTools _handle_list_tools Request Details: {context.request}")
        context.info(f"ListTools _handle_list_tools Request Details: {str(context.request)}")
        return await super()._handle_list_tools(context)

# Initialize FastMCP server
server = CustomFastMCP(
    name="bing-image-search-mcp"
)


@server.prompt("system_prompt")
def system_prompt() -> str:
    """
    """
    prompt="""
    # Bing Image Search MCP is an MCP server to help users better use Bing Search Engine to search images.
    The tool 
    'search_images' takes query as input and return a list of dict of images' title, thumbnail and urls.
    'search_images_batch':  takes a list of query keywords as input and return a list of dict of images' title, thumbnail and urls.
    """
    return prompt

@server.tool()
def search_images(
        query: str = "",
        limit: int = 10
    ) -> List[Any]:
    """ Get Public Available Stock Symbols from Global Marketplace

        Args:
            query: str, query used in Bing search engine
            limit: int, number of images information returned
  
        Return: 
            str: json str with below values samples

            [{'title': 'Italy Travel Guide: The Ultimate 2-week Road Trip · Salt in our Hair',
               'thumbnail_url': 'http://ts2.mm.bing.net/th?id=OIP.TEuPMUk1s2A3OBkq3LrTnwHaFc&pid=15.1',
               'url': 'http://ts2.mm.bing.net/th?id=OIP.TEuPMUk1s2A3OBkq3LrTnwHaFc&pid=15.1'},
              {'title': '25 Best Places to Visit in Italy (+ Map to Find Them!) - Our Escape Clause',
               'thumbnail_url': 'http://ts2.mm.bing.net/th?id=OIP.kle1eO_p_4crE4lRtWK8AgHaE8&pid=15.1',
               'url': 'http://ts2.mm.bing.net/th?id=OIP.kle1eO_p_4crE4lRtWK8AgHaE8&pid=15.1'}
               ]
    """
    try:
        # results list of json
        result_map =request_image_from_bing(query, limit)
        result_list = []
        for q, items in result_map.items():
            result_list.extend(items)
        return result_list

    except httpx.HTTPError as e:
        return f"Error communicating with Bing Image Search API: {str(e)}"
        return []
    except Exception as e:
        return f"Unexpected error: {str(e)}"
        return []


@server.tool()
def search_images_batch(
    query_list: List[str], 
    limit: int = 10
    ) -> Dict[str, List[Any]]:
    """ Batch Method of Search Images From Bing Web Search

        Args:
            query_list: List[str], List of query used in Bing Image search engine
            limit: int, number of images information returned
  
        Return: 
            Dict: json Dict with below values samples

            [{'title': 'Italy Travel Guide: The Ultimate 2-week Road Trip · Salt in our Hair',
               'thumbnail_url': 'http://ts2.mm.bing.net/th?id=OIP.TEuPMUk1s2A3OBkq3LrTnwHaFc&pid=15.1',
               'url': 'http://ts2.mm.bing.net/th?id=OIP.TEuPMUk1s2A3OBkq3LrTnwHaFc&pid=15.1'},
              {'title': '25 Best Places to Visit in Italy (+ Map to Find Them!) - Our Escape Clause',
               'thumbnail_url': 'http://ts2.mm.bing.net/th?id=OIP.kle1eO_p_4crE4lRtWK8AgHaE8&pid=15.1',
               'url': 'http://ts2.mm.bing.net/th?id=OIP.kle1eO_p_4crE4lRtWK8AgHaE8&pid=15.1'}
               ]
    """
    try:
        # results list of json
        result_map = request_image_from_bing_batch(query_list, limit)
        return result_map

    except httpx.HTTPError as e:
        return f"Error communicating with Bing Image Search API: {str(e)}"
        return []
    except Exception as e:
        return f"Unexpected error: {str(e)}"
        return []

### Utils
def read_data(data_file):
    file = codecs.open(data_file, "r", "utf-8")
    l = []
    for line in file:
        line = line.replace("\n", "")
        l.append(line)
    return l

def save_data(data_file, l):
    file = codecs.open(data_file, "w", "utf-8")
    for line in l:
        file.write(line + "\n")
    file.close()


def normalize_query(query):
    query_norm = query.lower()
    return query_norm

def normalize_search_engine_query(query):
    """
        Add Keywords "-"
        e.g.: Hello World -> HELLO+WORLD
    """
    token_list = query.split(" ")
    token_list_upper = [t.upper() for t in token_list]
    normalize_query = "+".join(token_list_upper)
    return normalize_query

def image_resource_convert(url):
    """
        Failed to load resource: net::ERR_CERT_AUTHORITY_INVALID
    """
    url_convert = url.replace("https", "http")
    return url_convert

def clean_unknown_token_from_query(query):
    query_norm = query.replace(chr(57344), "") # ue000
    query_norm = query_norm.replace(chr(57345), " ")
    query_norm = query_norm.replace(chr(57346), " ")
    return query_norm

#### Search Bing Image Util
def request_image_from_bing(query:str , limit: int = 10):
    """
        url = "https://cn.bing.com/images/search?q=FUJI+APPLE+SLICES&qs=n&form=QBIR&sp=-1&lq=0&pq=fuji+apple+slices&sc=10-17&cvid=AEDF646ED5764A70A306B8BEAD31F05D&ghsh=0&ghacc=0&first=1"
        @return
        {
            "apple":[
                {
                    "name": "XXXX",
                    "url": "XXXX"
                },
                {}
            ]
        }
    """

    try:
        # query = "FUJI APPLE SLICES"
        query_norm = normalize_search_engine_query(query)
        request_url = "https://cn.bing.com/images/search?q=%s&qs=n&form=HDRSC2&first=1&sp=-1&lq=0&sc=10-17&cvid=AEDF646ED5764A70A306B8BEAD31F05D&ghsh=0&ghacc=0&first=1" % query_norm

        headers = {
            "Accept": "application/json, text/plain, */*",
            "Content-Type": "application/json;charset=UTF-8;",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/106.0.0.0 Safari/537.36",
        }

        page_max = 100

        res = requests.get(request_url, headers=headers)
        soup = BeautifulSoup(res.text, 'html.parser')
        ## 新方法
        data_list =soup.select('div[id="mmComponent_images_1"]')
        ul_list = data_list[0].select('ul') if len(data_list) > 0 else []

        image_url_list = []

        image_json_list = []
        for ul in ul_list:
            li_list = ul.select('li')
            li_size = len(li_list)

            for (cur_size, li) in enumerate(li_list):
                if cur_size > limit:
                    continue
                div_list = li.select("div[class='imgpt']")
                if len(div_list) > 0:
                    a_class =div_list[0].select("a[class='iusc']")
                    if len(a_class)>0:
                        image_url= a_class[0]['m']
                        image_url_json = json.loads(image_url)
                        image_title_raw = image_url_json["t"] if "t" in image_url_json else ""
                        image_title = clean_unknown_token_from_query(image_title_raw)
                        image_url_thumbnail = image_url_json["turl"]
                        image_url_list.append(image_url_thumbnail)
                        image_info_json = {}
                        image_info_json["title"] = image_title
                        image_info_json["thumbnail_url"] = image_resource_convert(image_url_thumbnail)
                        image_info_json["url"] = image_resource_convert(image_url_thumbnail)

                        image_json_list.append(image_info_json)
        result_map = {}
        result_map[query] = image_json_list
        return result_map

    except Exception as e:
        print (f"Error: request_image_from_bing failed with error {e}")
        result_map = {}
        result_map[query] = []
        return result_map

def create_robust_session():
    """"""
    session = requests.Session()
    
    retry_strategy = Retry(
        total=3,  
        backoff_factor=0.5, 
        status_forcelist=[429, 500, 502, 503, 504]
    )
    
    adapter = HTTPAdapter(max_retries=retry_strategy)
    session.mount("http://", adapter)
    session.mount("https://", adapter)
    
    return session

def request_image_from_bing_batch(queries: List[str], limit: int = 10, max_workers: int = None) -> Dict[str, List[Any]]:
    """
    """
    result_map = {}
    try: 
        if max_workers is None:
            import multiprocessing
            max_workers = multiprocessing.cpu_count() * len(queries)
        
        with create_robust_session() as session:
            with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
                future_to_query = {
                    executor.submit(request_image_from_bing, query, limit): query 
                    for query in queries
                }
                
                for future in concurrent.futures.as_completed(future_to_query):
                    query = future_to_query[future]
                    try:
                        single_result = future.result()
                        result_map[query] = single_result.get(query, [])
                    except Exception as e:
                        print(f"Search '{query}' Failed: {str(e)}")
                        result_map[query] = []

    except Exception as e:
        print (f"DEBUG: request_image_from_bing_batch failed {e}")
    return result_map

def test_request_image_from_bing_batch():
    image_query_list = ["italy sicily", "sicily churches"]
    limit = 5
    result_map = request_image_from_bing_batch(image_query_list, limit)

def download_image(file_path, image_url, image_name):
    try:
        headers = {
            "Accept": "application/json, text/plain, */*",
            "Content-Type": "application/json;charset=UTF-8;",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/106.0.0.0 Safari/537.36",
        }
        res = requests.get(url=image_url, headers=headers)
        if 200 == res.status_code:
            file_path = os.path.join(file_path, image_name)
            with open(file_path, 'wb') as file:
                file.write(res.content)
    except Exception as e:
        print ("DEBUG: download_image failed with error, url %s, name %s" % (image_url, image_name))
        print (e)

def download_image_from_bing(query, output_path, top_k):
    """ query = "FUJI+APPLE+SLICES"
    """
    image_result_map = request_image_from_bing(query)
    print(image_result_map)
    image_list = image_result_map[query]
    sub_image_list = image_list[0:top_k]

    output_tuple_list = []
    for (i, image_url) in enumerate(sub_image_list):
        image_name = query_to_file_name(query) + "_" + str(i) + ".png"
        # output_path = "/Users/rockingdingo/Desktop/workspace/wx/health"
        download_image(output_path, image_url, image_name)
        output_tuple_list.append((image_name, image_url))
    return output_tuple_list

def test_download_image():
    file_path = "./img"
    image_url = "https://tse4-mm.cn.bing.net/th?id=OIP.93JC7K3WrX3SSbFjgAy0ZwHaEZ&pid=15.1"
    image_name = "fuji_apple.png"
    download_image(file_path, image_url, image_name)

if __name__ == "__main__":
    # Initialize and run the server
    server.run(transport='stdio')
