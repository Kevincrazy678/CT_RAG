# HƯỚNG DẪN QUAY VIDEO DEMO & KỊCH BẢN THUYẾT TRÌNH (DƯỚI 5 PHÚT)
## Dự án: Lumen Travel Assistant — Trợ lý Du lịch Đà Nẵng
**Môn học:** Tư duy Tính toán (Computational Thinking — CSC10014)  
**Trường:** Đại học Khoa học Tự nhiên — ĐHQG-HCM  

---

> ⚠️ **CẢNH BÁO QUAN TRỌNG TỪ GIẢNG VIÊN:**  
> **Thời lượng video tối đa là 5 phút (05:00). Nội dung sau giây thứ 5:00 sẽ KHÔNG được chấm điểm!**  
> Do đó, kịch bản dưới đây được căn chỉnh thời gian chuẩn xác ở mức **4 phút 50 giây** (dư 10 giây an toàn).

---

## 1. Chuẩn Bị Trước Khi Bấm Quay (Pre-recording Checklist)

1. **Khởi động server & ứng dụng:**
   - Đảm bảo máy chủ Ollama (hoặc đường hầm Pinggy) đang hoạt động bình thường.
   - Chạy lệnh khởi động ứng dụng:
     ```bash
     streamlit run app.py
     ```
   - Mở trình duyệt web tại `http://localhost:8501`.
   - **Mẹo quay hình:** Nhấn `Ctrl` + `+` (hoặc `Cmd` + `+`) để phóng to trình duyệt lên **110% – 125%** giúp mã trích dẫn `[Gxx]`, nội dung và điểm Cosine hiển thị rõ nét trên video.

2. **Chuẩn bị tài khoản & file câu hỏi mẫu:**
   - Dùng 1 tài khoản đã tạo trước trên Firebase (ví dụ: `student@example.com` / `123456`) để đăng nhập nhanh chóng.
   - Mở sẵn 1 file Notepad để copy-paste nhanh các câu hỏi (tránh mất thời gian gõ phím làm lố thời gian):
     - **Câu 1 (Có trong cẩm nang):** `Cầu Rồng Đà Nẵng phun lửa và phun nước vào những ngày nào trong tuần và lúc mấy giờ?`
     - **Câu 2 (Ngoài cẩm nang):** `Giá phòng một đêm tại khách sạn 5 sao Novotel Danang Premier là bao nhiêu?`
     - **Câu 3 (Ca thất bại để thuyết trình):** `Hầm rượu Debay tại Bà Nà Hills được người Pháp xây dựng vào năm nào?`

3. **Chuẩn bị tab trình chiếu:**
   - **Tab 1:** Giao diện ứng dụng Streamlit (`http://localhost:8501`).
   - **Tab 2:** File `README.md` (hoặc slide) chiếu Sơ đồ 6 khối và Bảng kiểm thử 7 câu hỏi.

---

## 2. Bảng Phân Bổ Thời Gian Chuẩn (Tổng Thời Lượng: 4 phút 50 giây)

| Phân đoạn | Mốc thời gian | Thời lượng | Trọng tâm nội dung | Thao tác trên màn hình |
|:---:|:---:|:---:|:---|:---|
| **Phần 1** | `0:00 - 0:20` | 20 giây | Mở đầu, giới thiệu họ tên, MSSV, đề tài | Quay trang đăng nhập ứng dụng Streamlit |
| **Phần 2** | `0:20 - 0:50` | 30 giây | Demo Đăng nhập & Hỏi câu có trong cẩm nang | Nhập tài khoản $\rightarrow$ gửi câu hỏi Cầu Rồng $\rightarrow$ mở expander xem `[G01]` |
| **Phần 3** | `0:50 - 1:15` | 25 giây | Demo Câu hỏi ngoài cẩm nang (Quy tắc "Tôi không biết") | Gửi câu hỏi Novotel $\rightarrow$ bot từ chối ngay lập tức $\rightarrow$ chỉ điểm Cosine $< 0.45$ |
| **Phần 4** | `1:15 - 1:30` | 15 giây | Demo Đăng xuất & Xóa sạch session state | Bấm "Đăng xuất" $\rightarrow$ quay lại màn hình khóa, chứng minh session đã được xóa |
| **Phần 5** | `1:30 - 4:00` | 2 phút 30 giây | Báo cáo 4 trụ cột Tư duy tính toán (CT Analysis) | Chuyển sang Tab 2 (README/Slide): Lần lượt nói Abstraction, Decomposition, Pattern, Algorithm |
| **Phần 6** | `4:00 - 4:45` | 45 giây | Báo cáo kết quả Test (1 thành công, 1 thất bại) | Chiếu Bảng Test Table: phân tích ca Mỹ Khê và ca thất bại Missing Data ở Bà Nà Hills |
| **Phần 7** | `4:45 - 4:55` | 10 giây | Lời cảm ơn và kết thúc an toàn | Lời chào kết thúc video trước mốc 5:00 |

---

## 3. Kịch Bản Lời Thoại Chuẩn Từng Giây (Video Script)

### ⏱️ [0:00 - 0:20] Mở đầu & Giới thiệu
> *"Kính chào Thầy Cô. Em tên là **[Họ và tên của bạn]**, Mã số sinh viên: **[MSSV của bạn]**, học lớp **[Lớp của bạn]**. Hôm nay em xin trình bày video báo cáo Bài thực hành số 03 môn Tư duy Tính toán: Xây dựng Trợ lý du lịch Lumen Travel cho Thành phố Đà Nẵng kết hợp Firebase Authentication và RAG Chat."*

---

### ⏱️ [0:20 - 0:50] Demo Đăng nhập & Hỏi câu có trong cẩm nang
*(Hành động: Nhập email, mật khẩu rồi bấm Đăng nhập. Trang chat mở ra. Dán câu hỏi Cầu Rồng và gửi).*
> *"Đầu tiên là tính năng bảo vệ truy cập bằng Firebase Sign-in. Khi chưa đăng nhập, trang chat hoàn toàn bị khóa. Em tiến hành đăng nhập với tài khoản sinh viên đã tạo.*  
> *Ngay khi đăng nhập thành công, giao diện chat hiển thị thông tin email và UID của em. Bây giờ, em gửi câu hỏi đầu tiên có trong cẩm nang: 'Cầu Rồng Đà Nẵng phun lửa và phun nước vào những ngày nào trong tuần và lúc mấy giờ?'.*  
> *Hệ thống xử lý và phản hồi chính xác: Cầu Rồng phun lửa và nước vào 21:00 thứ Bảy và Chủ Nhật, có trích dẫn mã mục `[G01]`. Mở panel expander bên dưới, Thầy Cô có thể thấy mục `[G01]` được trích xuất với điểm tương đồng Cosine rất cao là `0.824`."*

---

### ⏱️ [0:50 - 1:15] Demo Câu hỏi ngoài cẩm nang & Quy tắc "Tôi không biết"
*(Hành động: Dán câu hỏi giá phòng khách sạn Novotel và bấm gửi).*
> *"Tiếp theo, em gửi một câu hỏi hoàn toàn không có trong cẩm nang du lịch: 'Giá phòng một đêm tại khách sạn 5 sao Novotel Danang Premier là bao nhiêu?'.*  
> *Hệ thống phát hiện điểm tương đồng Cosine tối đa chỉ đạt `0.36`, thấp hơn ngưỡng `0.45` nên lập tức phản hồi chuẩn mực: 'Tôi không biết. Cẩm nang du lịch hiện tại không có thông tin này', hoàn toàn ngăn chặn được hiện tượng mô hình tự bịa đặt thông tin."*

---

### ⏱️ [1:15 - 1:30] Demo Đăng xuất & Xóa sạch Session State
*(Hành động: Bấm nút "Đăng xuất" trên sidebar hoặc header).*
> *"Cuối cùng trong phần demo, em bấm nút 'Đăng xuất'. Hệ thống gọi hàm forget_user, xóa sạch toàn bộ thông tin tài khoản và lịch sử trò chuyện trong st.session_state theo đúng yêu cầu của đề bài, tuyệt đối không lưu trữ vào bất kỳ cơ sở dữ liệu nào khác."*

---

### ⏱️ [1:30 - 2:05] Phân tích CT — Trụ cột 1: Abstraction (Trừu tượng hóa)
*(Hành động: Chuyển màn hình sang file README.md hoặc slide chiếu mục 4.1).*
> *"Bước sang phần phân tích 4 trụ cột Tư duy tính toán:  
> Về **Abstraction**, đầu vào của trợ lý là câu hỏi tự nhiên của người dùng, đầu ra là câu trả lời có trích dẫn mã mục và danh sách tài liệu trích xuất kèm điểm số.  
> Trong cẩm nang du lịch, em giữ lại đúng 6 thuộc tính cốt lõi: id để trích dẫn ngắn gọn; title và text để nhúng vector ngữ nghĩa; source để bảo chứng độ tin cậy; category và tags để chuẩn bị cho Bài 4 lọc theo sở thích du khách. Em chủ động loại bỏ hình ảnh, giá phòng biến động và tọa độ GPS phức tạp để tối ưu context window của mô hình."*

---

### ⏱️ [2:05 - 2:40] Phân tích CT — Trụ cột 2: Decomposition (Phân rã bài toán)
*(Hành động: Cuộn chuột đến Sơ đồ 6 khối xử lý tuần tự).*
> *"Về **Decomposition**, hệ thống được phân rã thành quy trình nhúng cẩm nang 1 lần duy nhất bằng @st.cache_resource và pipeline truy vấn 6 khối tuần tự:  
> Khối 1 xác thực Firebase nhận email/pass trả về User Session Token;  
> Khối 2 nhúng câu hỏi bằng embeddinggemma trả về vector 768 chiều;  
> Khối 3 tính Cosine Similarity trích xuất Top-3 tài liệu phù hợp;  
> Khối 4 kiểm tra ngưỡng 0.45 và thiết lập Grounded System Prompt;  
> Khối 5 gọi mô hình qwen3:4b sinh câu trả lời và lọc sạch thẻ suy luận think;  
> Khối 6 hiển thị kết quả lên giao diện Streamlit kèm panel expander và lưu vào session_state."*

---

### ⏱️ [2:40 - 3:15] Phân tích CT — Trụ cột 3: Pattern Recognition (Nhận diện mẫu)
*(Hành động: Cuộn chuột đến phần Pattern Recognition).*
> *"Về **Pattern Recognition**, em tái sử dụng mẫu gọi REST API xác thực từ Lab 3 và mẫu suy luận LLM qua Pinggy từ Lab 4.  
> Đặc biệt, mẫu kiến trúc cốt lõi **'Filter $\rightarrow$ Score $\rightarrow$ Top-k'** được thể hiện rõ ràng: Filter trong 15 mục cẩm nang và lọc ngưỡng 0.45 $\rightarrow$ Score bằng công thức Cosine Similarity $\rightarrow$ và Top-k trích xuất 3 mục tốt nhất.  
> Mẫu kiến trúc này sẽ tái xuất hiện hoàn hảo trong Bài 4 (RAG-Rec): Tiền lọc địa điểm theo Category sở thích $\rightarrow$ Chấm điểm phù hợp dựa trên Tags $\rightarrow$ và trích xuất Top-k địa điểm lý tưởng để gợi ý lịch trình cho du khách."*

---

### ⏱️ [3:15 - 4:00] Phân tích CT — Trụ cột 4: Algorithm Design & Quyết định thiết kế
*(Hành động: Chiếu đoạn Mã giả và 2 quyết định thiết kế).*
> *"Về **Algorithm Design**, thuật toán chạy tuần tự: Kiểm tra câu hỏi rỗng $\rightarrow$ Vector hóa $\rightarrow$ Tính Cosine với cẩm nang đã cache $\rightarrow$ Sắp xếp lấy Top-3 $\rightarrow$ Kiểm tra ngưỡng $\rightarrow$ Gọi LLM.  
> Quyết định thiết kế then chốt của em là xây dựng **Cơ chế chống ảo giác 2 tầng với Ngưỡng Cosine Threshold = 0.45**: Thực nghiệm cho thấy các câu hỏi đúng chủ đề Đà Nẵng luôn đạt điểm từ 0.65 đến 0.85, còn các câu ngoài luồng chỉ đạt dưới 0.38. Ngưỡng 0.45 giúp ngắt luồng sớm ở bước Retrieval, kích hoạt câu 'Tôi không biết' mà không cần gọi LLM, giúp tiết kiệm thời gian và triệt tiêu 100% ảo giác."*

---

### ⏱️ [4:00 - 4:45] Báo cáo Kết Quả Kiểm Thử (Test Results)
*(Hành động: Cuộn chuột đến Bảng Test Table 7 câu hỏi trong README).*
> *"Về kết quả kiểm thử:  
> Một ca thành công nổi bật là câu hỏi diễn giải (paraphrase) về 'Bãi tắm cát trắng mịn để ngắm bình minh sáng sớm', mô hình embedding vẫn hiểu chính xác ngữ nghĩa và trích xuất đúng `[G03]` Biển Mỹ Khê với điểm Cosine cao `0.753`.  
> Em cũng đưa vào một ca thất bại để phân tích lỗi: Khi hỏi 'Hầm rượu Debay tại Bà Nà Hills được người Pháp xây dựng vào năm nào?'. Hệ thống đã trích xuất đúng mục `[G02]` ở bước Retrieval, nhưng cẩm nang chỉ có thông tin trải nghiệm mà thiếu năm xây dựng. Mô hình tuân thủ quy tắc từ chối thay vì đoán mò. Đây là lỗi thuộc bước **Missing Data (Dữ liệu bị thiếu)**, chứ không phải lỗi của thuật toán trích xuất hay mô hình sinh."*

---

### ⏱️ [4:45 - 4:55] Kết thúc an toàn
> *"Em đã hoàn thành đầy đủ toàn bộ yêu cầu của Bài thực hành số 03. Em xin chân thành cảm ơn Thầy Cô đã theo dõi video báo cáo của em!"*
*(Hành động: Dừng quay video ở mốc khoảng 4 phút 50 giây).*
