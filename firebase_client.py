"""
Module xác thực người dùng qua Firebase Authentication REST API (Google Identity Toolkit).
Kế thừa kiến trúc bảo mật từ Lab 3, đáp ứng nghiêm ngặt các quy định của Bài thực hành 03:
- Hỗ trợ Đăng ký (Sign-up), Đăng nhập (Sign-in), Đăng xuất (Sign-out).
- Không sử dụng Firestore hay bất kỳ cơ sở dữ liệu nào để lưu chat history.
- Thông báo lỗi thân thiện, bảo mật, không làm lộ URL hay API Key ra giao diện.
"""

import os
from pathlib import Path
import time
from typing import Any, Dict
from dotenv import load_dotenv
import requests

# Tải biến môi trường từ file .env cùng thư mục
ENV_FILE = Path(__file__).resolve().parent / ".env"
load_dotenv(ENV_FILE, override=False)

REQUEST_TIMEOUT = 15  # Thời gian chờ tối đa cho mỗi request mạng


class FirebaseError(Exception):
    """Lớp ngoại lệ an toàn hiển thị trên giao diện Streamlit, không làm lộ URL hay API Key."""

    def __init__(self, message: str, sign_in_again: bool = False):
        super().__init__(message)
        self.sign_in_again = sign_in_again


def get_firebase_config() -> tuple[str, str]:
    """Lấy API Key và Project ID hiện tại từ biến môi trường."""
    api_key = os.getenv("FIREBASE_API_KEY", "").strip()
    project_id = os.getenv("FIREBASE_PROJECT_ID", "").strip()
    return api_key, project_id


def validate_config() -> None:
    """Kiểm tra cấu hình biến môi trường cục bộ; không gửi request mạng."""
    api_key, project_id = get_firebase_config()
    if (
        not project_id
        or not api_key
        or "your_firebase" in api_key.lower()
        or "your_firebase" in project_id.lower()
    ):
        raise FirebaseError(
            "Bạn chưa điền API Key thật vào file .env!\n"
            "Vui lòng mở file .env và thay thế giá trị mẫu 'your_firebase_api_key_here' "
            "bằng Web API Key và Project ID thật từ Firebase Console."
        )
    if any(c in project_id for c in "/ ?#"):
        raise FirebaseError(
            "FIREBASE_PROJECT_ID không hợp lệ. Vui lòng lấy đúng Project ID từ Firebase Console, không phải URL."
        )


def _authenticate(action: str, email: str, password: str) -> Dict[str, Any]:
    """Gửi yêu cầu xác thực tới Google Identity Toolkit REST API."""
    validate_config()
    api_key, _ = get_firebase_config()

    email = email.strip()
    if not email or not password:
        raise FirebaseError("Vui lòng nhập đầy đủ địa chỉ Email và Mật khẩu.")

    url = f"https://identitytoolkit.googleapis.com/v1/accounts:{action}"
    try:
        response = requests.post(
            url,
            params={"key": api_key},
            json={
                "email": email,
                "password": password,
                "returnSecureToken": True,
            },
            timeout=REQUEST_TIMEOUT,
        )
    except requests.RequestException:
        raise FirebaseError(
            "Không thể kết nối đến máy chủ Firebase. Vui lòng kiểm tra lại kết nối mạng."
        ) from None

    try:
        data = response.json()
    except Exception:
        raise FirebaseError(
            "Máy chủ Firebase phản hồi dữ liệu không hợp lệ. Vui lòng thử lại sau."
        ) from None

    if response.ok:
        return data

    # Phân tích mã lỗi từ Firebase Identity Toolkit để hiển thị thông báo thân thiện
    error = data.get("error", {})
    code = str(error.get("message", "")) if isinstance(error, dict) else ""

    if (
        any(item in code for item in ("TOKEN_EXPIRED", "INVALID_ID_TOKEN", "USER_DISABLED"))
        or response.status_code == 401
    ):
        raise FirebaseError(
            "Phiên đăng nhập đã hết hạn. Vui lòng đăng nhập lại.",
            sign_in_again=True,
        )
    if "EMAIL_EXISTS" in code:
        raise FirebaseError(
            "Email này đã được đăng ký tài khoản. Vui lòng chọn tab Đăng nhập."
        )
    if "OPERATION_NOT_ALLOWED" in code:
        raise FirebaseError(
            "Tính năng Email/Password chưa được kích hoạt trong Firebase Console > Authentication > Sign-in method."
        )
    if "WEAK_PASSWORD" in code or "PASSWORD_DOES_NOT_MEET_REQUIREMENTS" in code:
        raise FirebaseError(
            "Mật khẩu quá yếu. Vui lòng nhập mật khẩu có tối thiểu 6 ký tự."
        )
    if "INVALID_EMAIL" in code:
        raise FirebaseError("Định dạng địa chỉ email không hợp lệ.")
    if any(
        item in code
        for item in (
            "INVALID_LOGIN_CREDENTIALS",
            "INVALID_PASSWORD",
            "EMAIL_NOT_FOUND",
        )
    ):
        raise FirebaseError("Đăng nhập thất bại. Sai email hoặc mật khẩu.")
    if "TOO_MANY_ATTEMPTS" in code or response.status_code == 429:
        raise FirebaseError(
            "Quá nhiều lần thử không thành công. Vui lòng đợi một lát rồi thử lại."
        )
    if response.status_code == 403:
        raise FirebaseError(
            "Truy cập bị từ chối (403). Vui lòng kiểm tra lại quyền và Web API Key trong file .env."
        )
    if "API_KEY" in code or "PROJECT_NOT_FOUND" in code or response.status_code == 404:
        raise FirebaseError(
            "Khóa API hoặc Project ID không hợp lệ. Vui lòng kiểm tra lại file .env."
        )

    raise FirebaseError(f"Xác thực Firebase không thành công: {code if code else 'Lỗi không xác định'}.")


def create_account(email: str, password: str) -> Dict[str, Any]:
    """Đăng ký tài khoản người dùng mới trên Firebase Authentication."""
    return _authenticate("signUp", email, password)


def sign_in(email: str, password: str) -> Dict[str, Any]:
    """Đăng nhập và trả về từ điển thông tin phiên an toàn (không chứa mật khẩu)."""
    data = _authenticate("signInWithPassword", email, password)
    try:
        user = {
            "uid": data["localId"],
            "email": data["email"],
            "id_token": data["idToken"],
            "expires_at": time.time() + int(data.get("expiresIn", 3600)),
        }
        if not all(isinstance(user[k], str) and user[k] for k in ("uid", "email", "id_token")):
            raise ValueError
        return user
    except (KeyError, TypeError, ValueError):
        raise FirebaseError(
            "Quá trình đăng nhập trả về dữ liệu không đầy đủ. Vui lòng thử lại."
        ) from None
