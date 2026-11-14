"""
Ứng dụng Web Streamlit: Lumen Travel Assistant - Trợ lý Du lịch Thành phố Đà Nẵng.
Bài thực hành số 03 (Practice 03: Sign-In Travel Assistant with RAG Chat).
Môn học: Tư duy Tính toán (Computational Thinking) - Trường ĐH Khoa học Tự nhiên, ĐHQG-HCM.

Tính năng:
1. Xác thực người dùng bằng Firebase Authentication (Sign-in, Sign-up, Sign-out).
2. Khóa bảo vệ: Trang chat RAG CHỈ hiển thị sau khi đăng nhập thành công.
3. RAG Pipeline: Nhúng câu hỏi bằng embeddinggemma, trích xuất Top-k bằng Cosine Similarity.
4. Mô hình sinh ngôn ngữ qwen3:4b chỉ trả lời từ cẩm nang và bắt buộc trích dẫn mã mục [Gxx].
5. Quy tắc chống ảo giác "Tôi không biết" khi điểm tương đồng dưới ngưỡng 0.45 hoặc cẩm nang không có câu trả lời.
6. Quản lý lịch sử hội thoại trong st.session_state và XÓA SẠCH hoàn toàn khi người dùng Đăng xuất.
"""

import os
from pathlib import Path
import streamlit as st

from firebase_client import FirebaseError, create_account, sign_in, validate_config
from rag import (
    DEFAULT_TOP_K,
    EMBED_MODEL,
    GEN_MODEL,
    OLLAMA_BASE_URL,
    SIMILARITY_THRESHOLD,
    OllamaError,
    generate_answer,
    retrieve_top_k,
)

# 1. Cấu hình trang Streamlit
st.set_page_config(
    page_title="Lumen Travel - Danang Assistant",
    page_icon="✈️",
    layout="wide",
    initial_sidebar_state="expanded",
)


def forget_user():
    """
    Xóa sạch toàn bộ thông tin tài khoản và lịch sử trò chuyện trong session_state khi Đăng xuất.
    Tuyệt đối không lưu trữ vào Firestore hay bất kỳ cơ sở dữ liệu nào khác (theo đúng yêu cầu đề bài).
    """
    st.session_state.clear()


# Khởi tạo danh sách tin nhắn hội thoại trong phiên nếu chưa có
if "messages" not in st.session_state:
    st.session_state["messages"] = []


# ==============================================================================
# MÀN HÌNH 1: GIAO DIỆN ĐĂNG KÝ / ĐĂNG NHẬP (HIỂN THỊ KHI CHƯA SIGN-IN)
# ==============================================================================
if "user" not in st.session_state:
    # Kiểm tra cấu hình .env trước khi render form
    config_warning = None
    try:
        validate_config()
    except FirebaseError as err:
        config_warning = str(err)

    col_center1, col_center2, col_center3 = st.columns([1, 2, 1])
    with col_center2:
        st.markdown("<h1 style='text-align: center;'>✈️ Lumen Travel Assistant</h1>", unsafe_allow_html=True)
        st.markdown(
            "<p style='text-align: center; color: #555;'>Trợ lý Cẩm nang Du lịch Thông minh — <b>Thành phố Đà Nẵng</b></p>",
            unsafe_allow_html=True,
        )
        st.markdown(
            "Chào mừng bạn đến với **Lumen Travel**! Để đảm bảo an toàn và cá nhân hóa trải nghiệm, "
            "tính năng trò chuyện thông minh **chỉ mở cho người dùng đã đăng nhập**."
        )

        if config_warning:
            st.warning(f"⚠️ Cảnh báo cấu hình Firebase:\n\n{config_warning}")
            st.info(
                "💡 Vui lòng sao chép file `.env.example` thành `.env`, điền `FIREBASE_API_KEY`, "
                "`FIREBASE_PROJECT_ID` và `OLLAMA_BASE_URL` thật của bạn để ứng dụng hoạt động."
            )

        with st.container(border=True):
            tab_login, tab_signup = st.tabs(["🔑 Đăng nhập", "📝 Đăng ký tài khoản"])

            # --- TAB ĐĂNG NHẬP ---
            with tab_login:
                with st.form("form_sign_in", clear_on_submit=False):
                    st.markdown("##### Đăng nhập tài khoản của bạn")
                    email_login = st.text_input(
                        "Địa chỉ Email",
                        placeholder="student@example.com",
                        key="login_email_input",
                    )
                    pass_login = st.text_input(
                        "Mật khẩu",
                        type="password",
                        placeholder="Nhập mật khẩu...",
                        key="login_pass_input",
                    )
                    submit_login = st.form_submit_button("Đăng nhập ngay", use_container_width=True)

                    if submit_login:
                        try:
                            user_session = sign_in(email_login, pass_login)
                            # Lưu thông tin phiên vào session_state (tuyệt đối không lưu mật khẩu)
                            st.session_state["user"] = user_session
                            st.session_state["messages"] = []  # Khởi tạo phiên chat mới
                            st.success("🎉 Đăng nhập thành công! Đang chuyển hướng...")
                            st.rerun()
                        except FirebaseError as fb_err:
                            st.error(f"❌ {fb_err}")

            # --- TAB ĐĂNG KÝ ---
            with tab_signup:
                with st.form("form_sign_up", clear_on_submit=True):
                    st.markdown("##### Tạo tài khoản mới")
                    email_signup = st.text_input(
                        "Địa chỉ Email đăng ký",
                        placeholder="student@example.com",
                        key="signup_email_input",
                    )
                    pass_signup = st.text_input(
                        "Mật khẩu mới",
                        type="password",
                        placeholder="Tối thiểu 6 ký tự...",
                        key="signup_pass_input",
                    )
                    submit_signup = st.form_submit_button("Tạo tài khoản mới", use_container_width=True)

                    if submit_signup:
                        try:
                            create_account(email_signup, pass_signup)
                            st.success(
                                "🎉 Đăng ký tài khoản thành công! Bạn có thể chuyển sang tab 'Đăng nhập' để đăng nhập ngay."
                            )
                        except FirebaseError as fb_err:
                            st.error(f"❌ {fb_err}")


# ==============================================================================
# MÀN HÌNH 2: GIAO DIỆN CHAT RAG (CHỈ HIỂN THỊ SAU KHI SIGN-IN THÀNH CÔNG)
# ==============================================================================
else:
    current_user = st.session_state["user"]

    # --- SIDEBAR: THÔNG TIN TÀI KHOẢN & ĐIỀU KHIỂN HỆ THỐNG ---
    with st.sidebar:
        st.markdown("### 👤 Thông tin tài khoản")
        st.write(f"**Email:** `{current_user['email']}`")
        st.caption(f"Firebase UID: `{current_user['uid']}`")

        c1, c2 = st.columns(2)
        with c1:
            if st.button("🚪 Đăng xuất", use_container_width=True):
                forget_user()
                st.rerun()
        with c2:
            if st.button("🗑️ Xóa Chat", use_container_width=True):
                st.session_state["messages"] = []
                st.rerun()

        st.divider()

        st.markdown("### ⚙️ Cấu hình RAG System")
        st.markdown("- **Thành phố:** Đà Nẵng (15 mục)")
        st.markdown(f"- **Embedding:** `{EMBED_MODEL}`")
        st.markdown(f"- **Chat Model:** `{GEN_MODEL}`")
        st.markdown(f"- **Top-K Retrieval:** `{DEFAULT_TOP_K}`")
        st.markdown(f"- **Cosine Threshold:** `{SIMILARITY_THRESHOLD}`")
        st.markdown(f"- **Ollama Server:** `{OLLAMA_BASE_URL}`")

        st.divider()
        st.caption(
            "📌 **Nguyên tắc bảo vệ dữ liệu:** Lịch sử trò chuyện chỉ lưu tạm trong `st.session_state` "
            "của phiên duyệt web và bị xóa sạch vĩnh viễn khi Đăng xuất."
        )

    # --- MAIN CONTENT AREA: KHUNG TRÒ CHUYỆN RAG ---
    st.title("🏝️ Cẩm Nang Du Lịch Đà Nẵng")
    st.caption(
        "Trợ lý AI trả lời **độc quyền từ cẩm nang nội bộ** của Lumen Travel. "
        "Mọi thông tin đều có trích dẫn mã mục `[Gxx]` và cam kết kích hoạt quy tắc **'Tôi không biết'** khi câu hỏi nằm ngoài phạm vi."
    )

    # 1. Hiển thị lại toàn bộ lịch sử trò chuyện trong phiên làm việc hiện tại
    for message in st.session_state["messages"]:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
            # Nếu tin nhắn của trợ lý có kèm danh sách nguồn tài liệu, hiển thị panel mở rộng
            if message.get("sources"):
                with st.expander(
                    "📚 Nguồn cẩm nang trích dẫn & Độ tương đồng (Cosine Score)",
                    expanded=False,
                ):
                    for doc, score in message["sources"]:
                        st.markdown(
                            f"- **[{doc['id']}] {doc['title']}** — Độ tương đồng: `{score:.4f}`"
                        )
                        st.caption(
                            f"Phân loại: *{doc.get('category', 'landmark')}* | Nguồn: {doc.get('source', 'Cẩm nang')}"
                        )
                        st.text(f"Nội dung: {doc['text']}")

    # 2. Khung nhập câu hỏi của người dùng
    user_query = st.chat_input("Hỏi tôi về giờ mở cửa, giá vé, địa điểm, món ăn tại Đà Nẵng...")

    if user_query is not None:
        trimmed_query = user_query.strip()

        # Kiểm tra và xử lý trường hợp câu hỏi rỗng
        if not trimmed_query:
            st.warning("⚠️ Vui lòng nhập nội dung câu hỏi, không để trống!")
        else:
            # Lưu câu hỏi của người dùng vào lịch sử phiên và hiển thị lên giao diện
            st.session_state["messages"].append({"role": "user", "content": trimmed_query})
            with st.chat_message("user"):
                st.markdown(trimmed_query)

            # Xử lý câu trả lời từ RAG Pipeline
            with st.chat_message("assistant"):
                with st.spinner("🔍 Đang truy xuất cẩm nang & tổng hợp câu trả lời..."):
                    try:
                        # Bước truy xuất Top-k tài liệu kèm điểm tương đồng
                        top_docs, is_out_of_scope = retrieve_top_k(trimmed_query, k=DEFAULT_TOP_K)

                        # Bước sinh câu trả lời bằng LLM (hoặc từ chối nếu ngoài phạm vi)
                        assistant_response = generate_answer(trimmed_query, top_docs, is_out_of_scope)
                        st.markdown(assistant_response)

                        # Hiển thị panel mở rộng danh sách nguồn trích dẫn và điểm số cosine
                        with st.expander(
                            "📚 Nguồn cẩm nang trích dẫn & Độ tương đồng (Cosine Score)",
                            expanded=True,
                        ):
                            if is_out_of_scope:
                                st.info(
                                    f"ℹ️ Điểm tương đồng tối đa ({top_docs[0][1]:.4f} nếu có) thấp hơn ngưỡng cho phép (Threshold = {SIMILARITY_THRESHOLD}). "
                                    "Hệ thống chủ động kích hoạt quy tắc chống ảo giác 'Tôi không biết'."
                                )
                            for doc, score in top_docs:
                                st.markdown(
                                    f"- **[{doc['id']}] {doc['title']}** — Điểm Cosine: `{score:.4f}`"
                                )
                                st.caption(
                                    f"Danh mục: *{doc.get('category', 'N/A')}* | Thẻ: `{', '.join(doc.get('tags', []))}`"
                                )
                                st.caption(f"Trích yếu: {doc['text'][:150]}...")

                        # Lưu phản hồi của trợ lý kèm nguồn vào lịch sử phiên hiện tại
                        st.session_state["messages"].append({
                            "role": "assistant",
                            "content": assistant_response,
                            "sources": top_docs,
                        })

                    except OllamaError as ollama_err:
                        st.error(f"❌ Lỗi dịch vụ AI: {ollama_err}")
                        st.info(
                            "💡 Hướng dẫn kiểm tra:\n"
                            "1. Kiểm tra máy chủ Ollama hoặc đường hầm Pinggy có đang chạy không.\n"
                            "2. Đảm bảo biến `OLLAMA_BASE_URL` trong file `.env` đã được cấu hình chính xác.\n"
                            "3. Đảm bảo đã pull cả 2 model: `ollama pull embeddinggemma` và `ollama pull qwen3:4b`."
                        )
                    except Exception as unexpected_err:
                        st.error(f"❌ Đã xảy ra lỗi ngoài ý muốn: {unexpected_err}")
