from ast import While
from typing import Dict, List
import json
from attr import field
import numpy as np
from sympy import total_degree
import umap
import requests
from sklearn.preprocessing import StandardScaler
import time

MAX_BATCH_SIZE = 16
URL = "http://api.semanticscholar.org/graph/v1/paper/search?query="

def chunks(lst, chunk_size=MAX_BATCH_SIZE):
    """Splits a longer list to respect batch size"""
    for i in range(0, len(lst), chunk_size):
        yield lst[i : i + chunk_size]

def embed(papers):
    embeddings_by_paper_id: Dict[str, List[float]] = {}

    for chunk in chunks(papers):
        # Allow Python requests to convert the data above to JSON
        response = requests.post(URL, json=chunk)

        if response.status_code != 200:
            raise RuntimeError("Sorry, something went wrong, please try later!")

        for paper in response.json()["preds"]:
            embeddings_by_paper_id[paper["paper_id"]] = paper["embedding"]

    return embeddings_by_paper_id


def getAllRecPapers(keywords, fields):
    kw_str = ""
    for kw in keywords:
        kw_str += kw.lower()
        kw_str += "+"
    fd_str = ""
    for f in fields:
        fd_str += f.lower()
        fd_str += ","

    offset = 0
    limit = 1
    cnt = 1
    qry = URL + kw_str[:-1]+"&offset={}&limit={}&fields=".format(offset,limit)+fd_str[:-1]
    response = requests.get(qry).json()
    print(response)
    res = response["data"]
    total = response["total"]
    offset = limit
    limit = 100
    
    while cnt < total:
        try:
            qry = URL + kw_str[:-1]+"&offset={}&limit={}&fields=".format(offset,limit)+fd_str[:-1]
            print(qry)
            response = requests.get(qry).json()
            data = response["data"]
            res += data
            offset += limit
            cnt += len(data)
        except:
            break
    print(cnt)
    with open("query.json", 'w') as f:
        json.dump({"data":res}, f)
            

def getEmbeddings():
    with open("query.json", "r") as f:
        data = json.load(f)["data"]
    i = 0
    total = len(data)
    file_cnt = 0
    while (i < total):
        dic = data[i]
        pid = dic["paperId"]
        qry = "https://api.semanticscholar.org/graph/v1/paper/"+pid+"?fields=embedding"
        print("{}/{} Querying: {}".format(i, total, dic["title"]))
        response = requests.get(qry)
        try:
            embedding = response.json()["embedding"]["vector"]
            data[i]["embedding"] = embedding
            i+=1
        except:
            print(response.json())
            with open("embedding-{}.json".format(file_cnt), "w") as f:
                json.dump({"data":data}, f)
                file_cnt += 1
            print("Too many requests, wait for 5 min")
            time.sleep(5*60)
    with open("embedding.json", "w") as f:
        json.dump({"data":data}, f)
    


def getRecommendedPaperList(url):
    print(url)
    response = requests.get(url)
    with open("./query.json", 'w') as f:
        json.dump(response.json(), f)
    query_data = response.json()["data"]
    paper_list = []
    for paper in query_data:
        paper_list.append(paper["paperId"])
    return paper_list


if __name__ == "__main__":
    plist = getRecommendedPaperList(URL)
    # getAllRecPapers(['wifi', 'sensing', 'localization'], ['title'])
    # getEmbeddings()
    # embed_vec_list = []
    # for pid in plist:
    #     qry = "https://api.semanticscholar.org/graph/v1/paper/"+pid+"?fields=embedding"
    #     response = requests.get(qry)
    #     embedding = response.json()["embedding"]["vector"]
    #     embed_vec_list.append(embedding)
    #     print(len(embedding))
    # embed_vec_list = np.array(embed_vec_list)
    # print(embed_vec_list.shape)
    # scaled__data = StandardScaler().fit_transform(embed_vec_list)
    # reducer = umap.UMAP()
