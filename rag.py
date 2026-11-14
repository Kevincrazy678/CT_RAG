"""
Module xử lý RAG (Retrieval-Augmented Generation) cho Lumen Travel Assistant - Đà Nẵng.
Tuân thủ đầy đủ các yêu cầu cốt lõi của Bài thực hành số 03 (Assignment 03):
- Mô hình nhúng (Embedding): embeddinggemma (hỗ trợ cả /api/embed và /api/embeddings của Ollama)
- Thuật toán trích xuất: Cosine Similarity (NumPy) xếp hạng Top-k
- Cơ chế Caching: @st.cache_resource (chỉ nhúng cẩm nang 1 lần duy nhất)
- Mô hình sinh ngôn ngữ: qwen3:4b (hỗ trợ /api/chat và /api/generate)
- Quy tắc chống ảo giác: Kích hoạt 'Tôi không biết' 2 tầng (Tầng 1: Ngưỡng Cosine < 0.45; Tầng 2: Ràng buộc ngữ cảnh nghiêm ngặt)
- Làm sạch output: Tự động loại bỏ khối suy luận <think>...</think> nếu có.
"""

import json
import os
from pathlib import Path
import re
from typing import Any, Dict, List, Tuple
from dotenv import load_dotenv
import numpy as np
import requests
import streamlit as st

# Tải biến môi trường từ file .env cùng thư mục
load_dotenv(Path(__file__).with_name(".env"), override=False)

OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434").rstrip("/")
EMBED_MODEL = os.getenv("EMBEDDING_MODEL", "embeddinggemma").strip()
GEN_MODEL = os.getenv("CHAT_MODEL", "qwen3:4b").strip()

# Ngưỡng tương đồng cosine tối thiểu để kích hoạt quy tắc "Tôi không biết"
SIMILARITY_THRESHOLD = float(os.getenv("SIMILARITY_THRESHOLD", "0.45"))
DEFAULT_TOP_K = int(os.getenv("TOP_K", "3"))
REQUEST_TIMEOUT = 120  # Thời gian chờ phản hồi tối đa từ Ollama/Pinggy


class OllamaError(Exception):
    """Ngoại lệ an toàn khi xảy ra lỗi kết nối hoặc xử lý từ phía máy chủ Ollama/Pinggy."""
    pass


def _clean_llm_output(text: str) -> str:
    """Loại bỏ khối suy luận <think>...</think> (nếu có) từ mô hình reasoning/chat."""
    cleaned = re.sub(r"<think>.*?</think>", "", text, flags=re.DOTALL)
    return cleaned.strip()


def load_knowledge_base(file_name: str = "knowledge_base.json") -> List[Dict[str, Any]]:
    """Đọc dữ liệu cẩm nang từ file JSON."""
    file_path = Path(__file__).resolve().parent / file_name
    if not file_path.exists():
        raise FileNotFoundError(f"Không tìm thấy file cẩm nang tại: {file_path}")
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        if not isinstance(data, list):
            raise ValueError("Dữ liệu cẩm nang phải là một danh sách các mục (list).")
        return data
    except Exception as e:
        raise OllamaError(f"Lỗi khi đọc file cẩm nang {file_name}: {e}") from e


def get_embedding(text: str, model: str = EMBED_MODEL) -> np.ndarray:
    """
    Gửi yêu cầu nhúng vector tới máy chủ Ollama.
    Tự động hỗ trợ cả endpoint chuẩn mới (/api/embed) và endpoint cũ (/api/embeddings).
    """
    if not text or not text.strip():
        raise OllamaError("Không thể tạo vector nhúng cho văn bản rỗng.")

    if not OLLAMA_BASE_URL:
        raise OllamaError(
            "Chưa cấu hình OLLAMA_BASE_URL trong file .env. Vui lòng kiểm tra lại."
        )

    res = None
    # 1. Thử gọi endpoint mới /api/embed (chuẩn từ Ollama 0.1.34+)
    try:
        res = requests.post(
            f"{OLLAMA_BASE_URL}/api/embed",
            json={"model": model, "input": text},
            timeout=REQUEST_TIMEOUT,
        )
        # 2. Nếu trả về 404 và không phải do thiếu model, fallback về /api/embeddings
        if res.status_code == 404 and "model" not in res.text.lower():
            res = requests.post(
                f"{OLLAMA_BASE_URL}/api/embeddings",
                json={"model": model, "prompt": text},
                timeout=REQUEST_TIMEOUT,
            )
    except requests.exceptions.ConnectionError:
        raise OllamaError(
            f"Không thể kết nối đến máy chủ Ollama/Pinggy tại '{OLLAMA_BASE_URL}'. "
            "Vui lòng kiểm tra lại xem dịch vụ Ollama hoặc đường hầm Pinggy có đang hoạt động không."
        ) from None
    except requests.exceptions.Timeout:
        raise OllamaError(
            "Hết thời gian chờ phản hồi tạo embedding từ máy chủ Ollama/Pinggy (Timeout)."
        ) from None
    except requests.RequestException as e:
        raise OllamaError(f"Lỗi kết nối khi gửi yêu cầu embedding: {e}") from e

    if res is None:
        raise OllamaError("Không nhận được phản hồi từ máy chủ Ollama.")

    if res.status_code == 404:
        raise OllamaError(
            f"Máy chủ Ollama không tìm thấy model embedding '{model}'. "
            f"Vui lòng mở terminal máy chủ và chạy: ollama pull {model}"
        )
    if res.status_code in (502, 503, 504):
        raise OllamaError(
            f"Đường hầm Pinggy hoặc máy chủ Ollama phản hồi mã lỗi {res.status_code} (Bad Gateway / Unavailable)."
        )
    if not res.ok:
        raise OllamaError(f"Máy chủ Ollama trả về mã lỗi embedding: {res.status_code} ({res.text})")

    try:
        data = res.json()
    except Exception:
        raise OllamaError("Máy chủ Ollama trả về dữ liệu embedding không hợp lệ (không phải JSON).")

    # Trích xuất vector từ phản hồi (hỗ trợ cả trường 'embeddings' và 'embedding')
    embeddings = data.get("embeddings") or ([data.get("embedding")] if data.get("embedding") else [])
    if embeddings and isinstance(embeddings, list) and embeddings[0]:
        vec = np.array(embeddings[0], dtype=np.float32)
        norm = np.linalg.norm(vec)
        return vec / norm if norm > 0 else vec

    raise OllamaError(f"Phản hồi từ Ollama không chứa vector embedding cho model '{model}'.")


@st.cache_resource(show_spinner="⏳ Đang tải và tạo vector nhúng cẩm nang du lịch (chỉ chạy 1 lần)...")
def get_cached_embeddings() -> Tuple[List[Dict[str, Any]], np.ndarray]:
    """
    Tính toán vector embedding cho toàn bộ cẩm nang MỘT LẦN DUY NHẤT và lưu vào bộ nhớ cache.
    Kết hợp title, category, text và tags để tạo đại diện ngữ nghĩa phong phú nhất cho cả Bài 3 và Bài 4.
    """
    docs = load_knowledge_base()
    embeddings = []
    for doc in docs:
        tags_str = ", ".join(doc.get("tags", [])) if doc.get("tags") else ""
        category_str = doc.get("category", "")
        # Kết hợp các thuộc tính ngữ nghĩa chính
        combined_text = f"{doc['title']} - Phân loại: {category_str}: {doc['text']} Từ khóa: {tags_str}".strip()
        emb = get_embedding(combined_text)
        embeddings.append(emb)

    return docs, np.array(embeddings, dtype=np.float32)


def cosine_similarity(v1: np.ndarray, v2: np.ndarray) -> float:
    """Tính độ tương đồng cosin giữa 2 vector số thực bằng NumPy."""
    norm1 = np.linalg.norm(v1)
    norm2 = np.linalg.norm(v2)
    if norm1 == 0.0 or norm2 == 0.0:
        return 0.0
    return float(np.dot(v1, v2) / (norm1 * norm2))


def retrieve_top_k(
    query: str,
    k: int = DEFAULT_TOP_K
) -> Tuple[List[Tuple[Dict[str, Any], float]], bool]:
    """
    Trích xuất top-k tài liệu có độ tương đồng cosin cao nhất với câu hỏi.
    Trả về danh sách các cặp (doc, score) và cờ is_out_of_scope nếu điểm cao nhất dưới ngưỡng.
    """
    if not query or not query.strip():
        return [], True

    docs, guide_embeddings = get_cached_embeddings()
    query_vec = get_embedding(query.strip())

    scored_docs = []
    for i, doc in enumerate(docs):
        score = cosine_similarity(query_vec, guide_embeddings[i])
        scored_docs.append((doc, score))

    # Sắp xếp giảm dần theo điểm tương đồng cosine
    scored_docs.sort(key=lambda item: item[1], reverse=True)

    top_docs = scored_docs[:k]
    max_score = top_docs[0][1] if top_docs else 0.0
    is_out_of_scope = max_score < SIMILARITY_THRESHOLD

    return top_docs, is_out_of_scope


def generate_answer(
    query: str,
    top_scored_docs: List[Tuple[Dict[str, Any], float]],
    is_out_of_scope: bool = False
) -> str:
    """
    Sinh câu trả lời bằng mô hình qwen3:4b dựa trên ngữ cảnh được trích xuất.
    Đảm bảo 3 yêu cầu sống còn:
    1. Trích dẫn ID (ví dụ [G01], [G03])
    2. Chỉ sử dụng thông tin trong ngữ cảnh
    3. Trả lời 'Tôi không biết' khi điểm số dưới ngưỡng hoặc cẩm nang không có thông tin
    """
    # TẦNG 1 KIỂM SOÁT ẢO GIÁC: Nếu câu hỏi nằm ngoài phạm vi (Cosine Score < Threshold), từ chối ngay
    if is_out_of_scope or not top_scored_docs:
        return (
            "Tôi không biết. Cẩm nang du lịch hiện tại không có thông tin để trả lời câu hỏi này của bạn. "
            "Bạn vui lòng hỏi về các địa danh, giờ mở cửa, giá vé hoặc món ăn đặc sản tại Đà Nẵng nhé!"
        )

    # Xây dựng chuỗi ngữ cảnh từ top-k tài liệu
    context_chunks = []
    for doc, score in top_scored_docs:
        category_str = doc.get("category", "landmark")
        context_chunks.append(
            f"Mục [{doc['id']}] - {doc['title']} (Phân loại: {category_str}):\n"
            f"{doc['text']}\n"
            f"(Nguồn: {doc.get('source', 'Cẩm nang du lịch Đà Nẵng')})"
        )
    context_text = "\n\n".join(context_chunks)

    # System prompt nghiêm ngặt ép mô hình chỉ dựa vào cẩm nang và bắt buộc trích dẫn mã mục
    system_prompt = (
        "Bạn là trợ lý ảo chuyên nghiệp của công ty du lịch Lumen Travel dành riêng cho Thành phố Đà Nẵng.\n\n"
        "QUY TẮC BẮT BUỘC (STRICT COMPLIANCE REQUIRED):\n"
        "1. Bạn CHỈ ĐƯỢC PHÉP trả lời dựa vào phần 'NGỮ CẢNH CẨM NANG' được cung cấp bên dưới.\n"
        "2. TUYỆT ĐỐI KHÔNG tự suy đoán, bịa đặt hay sử dụng bất kỳ kiến thức nào nằm ngoài cẩm nang này.\n"
        "3. Khi đưa ra thông tin về địa điểm, giá vé, giờ mở cửa hay món ăn, BẮT BUỘC phải trích dẫn mã mục tương ứng trong ngoặc vuông, ví dụ: [G01], [G03].\n"
        "4. QUY TẮC 'TÔI KHÔNG BIẾT': Nếu trong ngữ cảnh KHÔNG CÓ thông tin để trả lời câu hỏi, hãy trả lời chính xác: "
        "'Tôi không có thông tin này trong cẩm nang du lịch.'\n"
        "5. Trả lời bằng tiếng Việt rõ ràng, ngắn gọn, lịch sự và hữu ích.\n\n"
        "=== [NGỮ CẢNH CẨM NANG] ===\n"
        f"{context_text}\n"
        "=== HẾT NGỮ CẢNH ==="
    )

    # 1. Thử gọi endpoint /api/chat (tối ưu nhất cho các mô hình chat như qwen3:4b)
    try:
        chat_payload = {
            "model": GEN_MODEL,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": query},
            ],
            "stream": False,
            "options": {
                "temperature": 0.1,  # Nhiệt độ thấp kiểm soát tối đa ảo giác
                "top_p": 0.9,
            },
        }
        res = requests.post(f"{OLLAMA_BASE_URL}/api/chat", json=chat_payload, timeout=REQUEST_TIMEOUT)
        if res.status_code == 200:
            data = res.json()
            content = data.get("message", {}).get("content", "").strip()
            if content:
                return _clean_llm_output(content)
    except requests.RequestException:
        pass  # Nếu lỗi hoặc endpoint chat không sẵn sàng, fallback sang /api/generate

    # 2. Dự phòng gọi endpoint /api/generate
    full_prompt = (
        f"{system_prompt}\n\n"
        f"CÂU HỎI CỦA NGƯỜI DÙNG: {query}\n\n"
        "CÂU TRẢ LỜI CỦA BẠN (kèm trích dẫn mã [Gxx]):"
    )
    gen_payload = {
        "model": GEN_MODEL,
        "prompt": full_prompt,
        "stream": False,
        "options": {
            "temperature": 0.1,
            "top_p": 0.9,
        },
    }

    try:
        res = requests.post(f"{OLLAMA_BASE_URL}/api/generate", json=gen_payload, timeout=REQUEST_TIMEOUT)
        if res.status_code == 404:
            raise OllamaError(
                f"Máy chủ Ollama không tìm thấy model sinh văn bản '{GEN_MODEL}'. "
                f"Vui lòng chạy lệnh: ollama pull {GEN_MODEL}"
            )
        if res.status_code in (502, 503, 504):
            raise OllamaError(
                f"Đường hầm Pinggy bị ngắt kết nối trong lúc sinh câu trả lời (HTTP {res.status_code})."
            )
        if not res.ok:
            raise OllamaError(f"Máy chủ Ollama trả về mã lỗi sinh câu trả lời: {res.status_code}")

        data = res.json()
        raw_answer = data.get("response", "").strip()
        if not raw_answer:
            return "Tôi không có thông tin này trong cẩm nang du lịch."
        return _clean_llm_output(raw_answer)

    except requests.exceptions.ConnectionError:
        raise OllamaError(
            "Mất kết nối với máy chủ Ollama/Pinggy trong lúc sinh câu trả lời. Vui lòng kiểm tra lại đường hầm Pinggy."
        ) from None
    except requests.exceptions.Timeout:
        raise OllamaError(
            "Quá thời gian chờ phản hồi sinh câu trả lời từ LLM (Timeout)."
        ) from None
    except Exception as e:
        if isinstance(e, OllamaError):
            raise
        raise OllamaError(f"Lỗi khi sinh câu trả lời: {str(e)}") from None
