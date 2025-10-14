from typing import Iterable, List, Dict

from panshi2task.base import GrpcServerInfo, DPLUS_3_4_GRPC_SERVER
from panshi2task.embedding_client import EmbeddingTaskClient
from panshi2task.llm_client import LlmTaskClient, QAItem
from panshi2task.paddle_client import PaddleTaskClient, OcrPageResult, BoxRecItem
from panshi2task.rerank_client import RerankTaskClient, RankItem
from panshi2task.torch_client import TorchTaskClient


class PanshiTaskClient:
    def __init__(self, server_info: GrpcServerInfo):
        if server_info.llm_server_url:
            self.llm_client = LlmTaskClient(server_info.llm_server_url)
        if server_info.paddle_server_url:
            self.paddle_client = PaddleTaskClient(server_info.paddle_server_url)
        if server_info.torch_server_url:
            self.torch_client = TorchTaskClient(server_info.torch_server_url)
        if server_info.embedding_server_url:
            self.embedding_client = EmbeddingTaskClient(server_info.embedding_server_url)
        if server_info.rerank_server_url:
            self.rerank_client = RerankTaskClient(server_info.rerank_server_url)

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.close()

    def close(self):
        if self.llm_client:
            self.llm_client.close()
        if self.paddle_client:
            self.paddle_client.close()
        if self.torch_client:
            self.torch_client.close()
        if self.embedding_client:
            self.embedding_client.close()
        if self.rerank_client:
            self.rerank_client.close()

    # ========================llm====================
    def entity_mining(self, schema: List[Dict[str, str]], text: str, except_num: int) -> Dict[str, List[str]]:
        assert self.llm_client is not None, "请提供llm_server_url地址"
        return self.llm_client.entity_mining(schema, text, except_num)

    def faq_mining(self, text: str, except_num=3) -> List[QAItem]:
        assert self.llm_client is not None, "请提供llm_server_url地址"
        return self.llm_client.faq_mining(text, except_num)

    def question_gen(self, text: str, except_num=3) -> List[str]:
        return self.llm_client.question_gen(text, except_num)

    def summary(self, text: str) -> str:
        assert self.llm_client is not None, "请提供llm_server_url地址"
        return self.llm_client.summary(text)

    def topic_mining(self, summary: str, titles: List[str] | None = None, except_num: int = 3) -> List[str]:
        assert self.llm_client is not None, "请提供llm_server_url地址"
        return self.llm_client.topic_mining(summary, titles, except_num)

    # ========================paddle====================
    def pdf_ocr(self, file_path: str, file_name: str | None = None) -> Iterable[OcrPageResult]:
        assert self.paddle_client is not None, "请提供paddle_server_url地址"
        return self.paddle_client.pdf_ocr(file_path, file_name)

    def pdf_ocr_bytes(self, local_file_path: str) -> Iterable[OcrPageResult]:
        assert self.paddle_client is not None, "请提供paddle_server_url地址"
        return self.paddle_client.pdf_ocr_bytes(local_file_path)

    def pdf_structure(self, file_path: str, file_name: str | None = None) -> Iterable[BoxRecItem]:
        assert self.paddle_client is not None, "请提供paddle_server_url地址"
        return self.paddle_client.pdf_structure(file_path, file_name)

    def pdf_structure_bytes(self, local_file_path: str) -> Iterable[BoxRecItem]:
        assert self.paddle_client is not None, "请提供paddle_server_url地址"
        return self.paddle_client.pdf_structure_bytes(local_file_path)

    def entity_extract(self, schema: List[str], inputs: List[str]) -> List[Dict]:
        assert self.paddle_client is not None, "请提供paddle_server_url地址"
        return self.paddle_client.entity_extract(schema, inputs)

    def relation_extract(self, schema: Dict, inputs: List[str]) -> List[Dict]:
        assert self.paddle_client is not None, "请提供paddle_server_url地址"
        return self.paddle_client.relation_extract(schema, inputs)

    # ========================torch====================
    def text_error_correction(self, texts: List[str]) -> List[str]:
        assert self.torch_client is not None, "请提供torch_server_url地址"
        return self.torch_client.text_error_correction(texts)

    def doc_seg(self, text: str) -> List[str]:
        assert self.torch_client is not None, "请提供torch_server_url地址"
        return self.torch_client.doc_seg(text)

    # ========================embedding====================
    def embedding(self, text: str, truncate: bool = True, normalize: bool = True) -> List[float]:
        assert self.embedding_client is not None, "请提供embedding_server_url地址"
        return self.embedding_client.embedding(text, truncate, normalize)

    def batch_embedding(self, texts: List[str], truncate: bool = True, normalize: bool = True) -> List[List[float]]:
        assert self.embedding_client is not None, "请提供embedding_server_url地址"
        return self.embedding_client.batch_embedding(texts, truncate, normalize)

    def text_similar(self, query, texts: List[str]) -> str:
        assert self.embedding_client is not None, "请提供embedding_server_url地址"
        return self.embedding_client.text_similar(query, texts)

    def terms_weight_analyse(self, terms: List[str]) -> List[int]:
        assert self.embedding_client is not None, "请提供embedding_server_url地址"
        return self.embedding_client.terms_weight_analyse(terms)

    # ========================rerank====================
    def rerank(self, query: str, texts: List[str], truncate: bool = True, raw_scores: bool = False,
               return_text: bool = True) -> List[RankItem]:
        assert self.rerank_client is not None, "请提供rerank_server_url地址"
        return self.rerank_client.rerank(query, texts, truncate, raw_scores, return_text)


if __name__ == '__main__':
    with PanshiTaskClient(DPLUS_3_4_GRPC_SERVER) as client:
        s = "asdad"
