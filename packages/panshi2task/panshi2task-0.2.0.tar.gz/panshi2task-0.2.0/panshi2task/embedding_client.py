from typing import List

import grpc
import numpy as np
from google.protobuf.json_format import MessageToDict
from loguru import logger
from sklearn.metrics.pairwise import cosine_similarity

from panshi2task.base import common_grpc_opts
from panshi2task.grpc_gen import tei_pb2
from panshi2task.grpc_gen.tei_pb2_grpc import EmbedStub


@staticmethod
def find_most_similar_vector(query_vector, vector_list):
    max_similarity = -1
    most_similar_index = None
    query_vector = np.array(query_vector).reshape(1, -1)
    for idx, vector in enumerate(vector_list):
        vector = np.array(vector).reshape(1, -1)
        similarity = cosine_similarity(query_vector, vector)[0][0]
        if similarity > max_similarity:
            max_similarity = similarity
            most_similar_index = idx
    return most_similar_index


@staticmethod
def calculate_similar(va, vb):
    va = np.array(va).reshape(1, -1)
    vb = np.array(vb).reshape(1, -1)
    _val = cosine_similarity(va, vb)[0][0]
    return _val.item()


class EmbeddingTaskClient:
    def __init__(self, url: str):
        self.url = url
        opts = common_grpc_opts
        self.channel = grpc.insecure_channel(url, options=opts)
        self.stub = EmbedStub(self.channel)
        logger.info("embedding client 初始化完成...")

    def embedding(self, text: str, truncate: bool = True, normalize: bool = True) -> List[float]:
        pb2_req = tei_pb2.EmbedRequest(inputs=text, truncate=truncate, normalize=normalize)
        pb2_resp: tei_pb2.EmbedResponse = self.stub.Embed(pb2_req)
        resp = MessageToDict(pb2_resp)
        return resp["embeddings"]

    def batch_embedding(self, texts: List[str], truncate: bool = True, normalize: bool = True) -> List[List[float]]:
        result = []
        for text in texts:
            result.append(self.embedding(text=text, truncate=truncate, normalize=normalize))
        return result

    def text_similar(self, query: str, texts: List[str]) -> str:
        _all = [query]
        _all.extend(texts)
        vectors = self.batch_embedding(_all)
        query_vector = vectors[0]
        texts_vector = vectors[1:]
        idx = find_most_similar_vector(query_vector, texts_vector)
        return texts[idx]

    def terms_weight_analyse(self, terms: List[str]) -> List[int]:
        a = "".join(terms)
        texts = []
        for i in range(len(terms)):
            tp = terms.copy()
            tp.pop(i)
            texts.append("".join(tp))
        # embedding
        _all = [a]
        _all.extend(texts)
        vectors = self.batch_embedding(_all)
        va = vectors[0]
        texts_vector = vectors[1:]
        # calculate similar
        similars = []
        for vb in texts_vector:
            s = calculate_similar(va, vb)
            similars.append(s)
        # weight
        weights = [int(round((1 - s), 2) * 100) for s in similars]
        return weights

    def close(self):
        if self.channel:
            self.channel.close()
