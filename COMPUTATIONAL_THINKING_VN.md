# BÁO CÁO PHÂN TÍCH 4 TRỤ CỘT TƯ DUY TÍNH TOÁN (COMPUTATIONAL THINKING)
## Đề tài: Lumen Travel Assistant — Trợ lý Du lịch Thành phố Đà Nẵng với RAG Chat & Firebase Authentication
**Môn học:** Tư duy Tính toán (Computational Thinking — CSC10014)  
**Trường:** Đại học Khoa học Tự nhiên — ĐHQG-HCM  

---

> **Lưu ý cốt lõi từ giảng viên:** *"Explain your own solution, not general definitions"* — Tài liệu này phân tích giải pháp kỹ thuật cụ thể đã hiện thực trong bài tập của bạn, không trích dẫn lý thuyết suông.

---

### 1. Trụ Cột 1: Abstraction (Trừu tượng hóa)

Trừu tượng hóa là quá trình chắt lọc các thuộc tính cốt lõi cần thiết để giải quyết bài toán và chủ động loại bỏ các chi tiết phức tạp, biến động không liên quan.

* **Đầu vào của hệ thống (System Inputs):**
  - Câu hỏi bằng ngôn ngữ tự nhiên từ người dùng đã đăng nhập thành công qua Firebase Authentication (ví dụ: *"Cầu Rồng Đà Nẵng phun lửa lúc mấy giờ?"*, *"Giá vé cáp treo Bà Nà Hills bao nhiêu tiền?"*).
* **Đầu ra của hệ thống (System Outputs):**
  - Câu trả lời tự nhiên bằng tiếng Việt được kiểm chứng thực tế (grounded response), bắt buộc trích dẫn mã mục nguồn trong ngoặc vuông (ví dụ: `[G01]`, `[G02]`).
  - Danh sách Top-k tài liệu trích xuất kèm điểm số tương đồng Cosine Similarity hiển thị minh bạch trong panel mở rộng (`st.expander`).
* **Mô hình hóa dữ liệu cẩm nang (`knowledge_base.json`):**
  - Cẩm nang gồm **15 mục** đại diện cho các danh thắng, bãi biển, di tích lịch sử và ẩm thực đặc trưng nhất của Đà Nẵng. Mỗi mục được chuẩn hóa với **6 trường dữ liệu**:
    1. `id`: Mã định danh ngắn gọn (ví dụ: `G01`, `G02`), giúp mô hình dễ dàng trích dẫn mà không chiếm dụng nhiều token trong context window.
    2. `title`: Tên danh thắng/món ăn, đóng vai trò định danh chính khi hiển thị cho người dùng và tính vector nhúng.
    3. `text`: Nội dung chắt lọc các thông tin thực tế quan trọng nhất: địa chỉ, giờ mở cửa, giá vé, trải nghiệm đặc trưng bằng văn phong súc tích.
    4. `source`: Nguồn thông tin uy tín (Cổng Danang FantastiCity, Ban quản lý...), đảm bảo tính minh bạch và độ tin cậy.
    5. `category`: Phân loại địa điểm (`landmark`, `beach`, `market`, `museum`, `mountain`, `entertainment`, `food`) phục vụ lọc nhanh theo nhu cầu.
    6. `tags`: Mảng các từ khóa phục vụ tính điểm phù hợp ngữ nghĩa sâu hơn và làm nền tảng trực tiếp cho Bài thực hành số 04 (RAG-Rec).
  - **Các chi tiết chủ động lược bỏ (Abstracted away):**
    - Tệp hình ảnh độ phân giải cao và video tư liệu (tránh làm quá tải băng thông và bộ nhớ RAM).
    - Tọa độ GPS kinh độ/vĩ độ chi tiết hàng chục chữ số thập phân (không cần thiết cho bài toán trả lời văn bản).
    - Bảng giá phòng biến động theo mùa cao điểm/thấp điểm (tránh gây sai lệch thông tin kiểm chứng).
    - Lịch sử hàng trăm năm quá dài dòng (tránh làm tràn context window của mô hình nhỏ `qwen3:4b`).

---

### 2. Trụ Cột 2: Decomposition (Phân rã bài toán)

Phân rã là kỹ thuật chia nhỏ hệ thống thành hai quy trình độc lập: **Khởi tạo nạp dữ liệu một lần (One-Time Indexing)** và **Pipeline xử lý truy vấn thời gian thực (Runtime Query Pipeline)** gồm 6 khối tuần tự.

```
[Khởi Tạo 1 Lần: One-Time Indexing (@st.cache_resource)]
knowledge_base.json (15 mục Đà Nẵng) ──→ Vector hóa bằng embeddinggemma ──→ Lưu vào RAM Cache

[Pipeline Xử Lý Truy Vấn: Runtime Query Flow]
[Khối 1: Firebase Sign-in]
      ↓ (User Session: UID, Email, Token)
[Khối 2: Vector hóa Query]
      ↓ (Vector câu hỏi 768 chiều)
[Khối 3: Retrieve Top-k & Score]
      ↓ (Top-k tài liệu + Cosine Similarity Scores)
[Khối 4: Filter & Build Context] ──(Max Cosine < 0.45)──→ Trả lời ngay "Tôi không biết..."
      ↓ (Grounded Prompt ép trích dẫn [Gxx])
[Khối 5: LLM Generate (qwen3:4b)]
      ↓ (Câu trả lời có kiểm chứng + Lọc sạch thẻ <think>)
[Khối 6: Display & Session History]
```

#### Bảng Định Nghĩa Chi Tiết 6 Khối Chức Năng:

| Khối xử lý | Tên bước | Dữ liệu đầu vào (Input) | Dữ liệu đầu ra (Output) | Module đảm nhiệm |
|:---:|:---|:---|:---|:---|
| **Khối 1** | **Xác thực người dùng (Sign-in)** | Email và Mật khẩu từ form Streamlit | Firebase User Session (`uid`, `email`, `id_token`) | `firebase_client.py` (Identity REST API) |
| **Khối 2** | **Vector hóa câu hỏi (Embed Query)** | Chuỗi câu hỏi tự nhiên của khách | Vector số thực 768 chiều (đã chuẩn hóa $L_2$) | `rag.py` (`embeddinggemma`) |
| **Khối 3** | **Truy xuất tương đồng (Retrieve Top-k)** | Vector câu hỏi + Ma trận vector cẩm nang đã cache | Top-k ($k=3$) tài liệu có điểm Cosine cao nhất | `rag.py` (NumPy Cosine Similarity) |
| **Khối 4** | **Kiểm soát ngưỡng & Tạo Prompt** | Top-k tài liệu + Điểm số tương đồng cao nhất | Grounded System Prompt (hoặc ngắt sớm từ chối) | `rag.py` (Threshold & Prompt Builder) |
| **Khối 5** | **Sinh câu trả lời (LLM Generate)** | System Prompt + Câu hỏi của khách | Văn bản trả lời trích dẫn `[Gxx]` (lọc `<think>`) | `rag.py` (`qwen3:4b` via Ollama) |
| **Khối 6** | **Hiển thị & Lưu phiên (Display & History)** | Phản hồi của trợ lý + Danh sách Top-k nguồn | UI Chat Message + Expander; lưu `session_state` | `app.py` (Streamlit Chat UI) |

---

### 3. Trụ Cột 3: Pattern Recognition (Nhận diện mẫu)

Nhận diện mẫu giúp tái sử dụng các giải pháp đã được chứng minh hiệu quả từ các lab trước và xây dựng nền tảng tiếp nối cho các bài tập tương lai.

#### 1. Kế thừa mẫu từ Lab 3 và Lab 4:
- **Từ Lab 3 (Firebase Authentication & Streamlit State):**
  - Kế thừa mẫu gọi REST API trực tiếp đến Google Identity Toolkit (`identitytoolkit.googleapis.com`) mà không cần cài đặt Firebase Admin SDK nặng nề.
  - Kế thừa mẫu bảo vệ truy cập giao diện qua điều kiện kiểm tra `if "user" not in st.session_state`.
  - Kế thừa mẫu giải phóng phiên làm việc: hàm `forget_user()` dọn sạch toàn bộ `st.session_state` khi đăng xuất, đảm bảo không có rò rỉ dữ liệu giữa các phiên.
- **Từ Lab 4 (Ollama Chat & RAG):**
  - Tái sử dụng mẫu tích hợp máy chủ suy luận Ollama thông qua đường hầm Pinggy URL.
  - Tái sử dụng mẫu cấu hình nhiệt độ sinh văn bản cực thấp (`temperature = 0.1`) để kiểm soát hiện tượng mô hình tự sáng tác thông tin.

#### 2. Mẫu thiết kế cốt lõi: "Filter $\rightarrow$ Score $\rightarrow$ Top-k":
- **Trong Bài 3 (RAG hiện tại):**
  - *Filter (Lọc):* Giới hạn không gian tìm kiếm trong phạm vi 15 mục cẩm nang Đà Nẵng đã kiểm chứng; kết hợp bộ lọc ngưỡng hậu kỳ ($\max(\text{score}) \ge 0.45$) để loại bỏ câu hỏi ngoài ngành.
  - *Score (Chấm điểm):* Tính toán khoảng cách ngữ nghĩa giữa vector truy vấn $\mathbf{q}$ và từng vector tài liệu $\mathbf{d}_i$ theo công thức Cosine Similarity:
    $$\text{Cosine}(\mathbf{q}, \mathbf{d}_i) = \frac{\mathbf{q} \cdot \mathbf{d}_i}{\|\mathbf{q}\|_2 \|\mathbf{d}_i\|_2}$$
  - *Top-k (Xếp hạng):* Sắp xếp giảm dần và cắt lấy đúng $K = 3$ tài liệu có điểm số cao nhất đưa vào ngữ cảnh cẩm nang.
- **Mối liên hệ tiếp nối trong Bài 4 (RAG-Rec: Recommendation System):**
  - Mẫu kiến trúc này sẽ tái xuất hiện ở cấp độ gợi ý cá nhân hóa:
    1. *Filter:* Tiền lọc danh sách các địa điểm phù hợp theo danh mục sở thích (`category` = `"beach"`, `"food"`, `"mountain"`).
    2. *Score:* Chấm điểm mức độ phù hợp đa chiều kết hợp giữa độ tương đồng ngữ nghĩa của câu hỏi với tỷ lệ trùng khớp từ khóa `tags` và lịch sử người dùng.
    3. *Top-k:* Chọn lọc Top-3 địa điểm tối ưu nhất để mô hình LLM lập lịch trình gợi ý du lịch riêng biệt cho từng du khách.

---

### 4. Trụ Cột 4: Algorithm Design (Thiết kế thuật toán)

#### Mã Giả (Pseudocode) Chi Tiết Của Thuật Toán:
```text
Thuật toán: AnswerTravelQuery(UserQuery, CachedKB, k = 3, threshold = 0.45)
Đầu vào: 
    - UserQuery: Chuỗi câu hỏi văn bản của người dùng
    - CachedKB: Danh sách cẩm nang đã nhúng vector [(doc_1, vec_1), ..., (doc_n, vec_n)]
    - k: Số lượng tài liệu trích xuất (mặc định k = 3)
    - threshold: Ngưỡng tương đồng cosine tối thiểu (mặc định 0.45)
Đầu ra: 
    - FinalAnswer: Câu trả lời kiểm chứng hoặc câu từ chối chuẩn
    - TopEntries: Danh sách tài liệu được chọn kèm điểm số tương đồng

1. IF Trim(UserQuery) IS EMPTY THEN:
       RETURN "Vui lòng nhập câu hỏi!", []
   END IF

2. q_vec <- GetEmbedding(UserQuery, model="embeddinggemma")
3. scored_list <- []

4. FOR EACH (doc_i, vec_i) IN CachedKB DO:
       score_i <- DotProduct(q_vec, vec_i) / (Norm(q_vec) * Norm(vec_i))
       Append (doc_i, score_i) TO scored_list
   END FOR

5. SortDescendingByScore(scored_list)
6. TopEntries <- scored_list[0 : k]
7. max_score <- TopEntries[0].score

8. // QUYẾT ĐỊNH THIẾT KẾ: Cơ chế chống ảo giác Tầng 1 (Quantitative Threshold)
   IF max_score < threshold THEN:
       FinalAnswer <- "Tôi không biết. Cẩm nang du lịch hiện tại không có thông tin để trả lời câu hỏi này của bạn."
       RETURN FinalAnswer, TopEntries
   END IF

9. context_text <- BuildContextString(TopEntries)
10. prompt <- ConstructStrictSystemPrompt(context_text, UserQuery)

11. // QUYẾT ĐỊNH THIẾT KẾ: Cơ chế chống ảo giác Tầng 2 (Prompt Constraint & Low Temp)
    raw_answer <- CallOllama(model="qwen3:4b", prompt=prompt, temperature=0.1)
    FinalAnswer <- StripThinkBlocks(raw_answer)

12. RETURN FinalAnswer, TopEntries
```

---

#### 2 Quyết Định Thiết Kế Then Chốt Kèm Ví Dụ Thực Tế:

#### Quyết Định 1: Lựa chọn số lượng tài liệu trích xuất $K = 3$
- **Lý do kỹ thuật:**
  - Nếu chọn $K = 1$: Ngữ cảnh cung cấp quá hẹp. Khi người dùng hỏi các câu hỏi so sánh hoặc câu hỏi liên đới giữa hai địa điểm liền kề, mô hình sẽ không đủ thông tin để trả lời đầy đủ.
  - Nếu chọn $K \ge 10$: Lượng token đưa vào ngữ cảnh quá lớn, làm loãng sự chú ý (attention dilution) của mô hình nhỏ `qwen3:4b` và làm tăng đáng kể độ trễ phản hồi qua mạng.
  - Chọn $K = 3$ là điểm cân bằng tối ưu giữa độ phủ thông tin và độ chính xác của ngữ cảnh.
- **Ví dụ thực tế minh họa:**
  - Khi người dùng hỏi: *"Cầu Rồng Đà Nẵng phun lửa vào ngày nào trong tuần?"*.
  - Hệ thống trích xuất $K = 3$ gồm: `[G01]` (Cầu Rồng), `[G08]` (Cầu Quay Sông Hàn) và `[G11]` (Chợ đêm Sơn Trà).
  - Nhờ có đầy đủ cả 3 mục, mô hình trả lời chính xác giờ phun lửa của Cầu Rồng (21:00 thứ Bảy và Chủ Nhật), phân biệt rõ ràng không bị nhầm lẫn với giờ quay của Cầu Sông Hàn (23:00 cuối tuần), đồng thời gợi ý thêm du khách có thể đi dạo Chợ đêm Sơn Trà ngay chân cầu.

#### Quyết Định 2: Thiết lập Cơ chế kiểm soát ảo giác 2 tầng với Ngưỡng Cosine Threshold = 0.45
- **Lý do kỹ thuật:**
  - Mô hình ngôn ngữ lớn bản chất là máy sinh xác suất từ tiếp theo, nên khi gặp câu hỏi ngoài cẩm nang, chúng thường có xu hướng "bịa đặt" (hallucination) thông tin một cách rất tự tin.
  - Để giải quyết triệt để, chúng em thiết kế cơ chế bảo vệ 2 tầng:
    - **Tầng 1 (Định lượng ở bước Retrieval):** Thực nghiệm đo đạc cho thấy: các câu hỏi đúng chủ đề du lịch Đà Nẵng luôn đạt điểm Cosine từ `0.65` đến `0.85`. Các câu hỏi ngoài luồng hoàn toàn (như *"Giá phòng Novotel"* đạt `0.36`, *"Thủ đô nước Pháp"* đạt `0.19`) đều có điểm $< 0.45$. Đặt ngưỡng `0.45` giúp ngắt luồng xử lý ngay lập tức, trả về *"Tôi không biết"* mà không tốn chi phí gọi LLM.
    - **Tầng 2 (Ràng buộc ở bước Generation):** Đối với các câu hỏi đạt điểm Cosine $> 0.45$ nhưng chi tiết con không có trong cẩm nang (ví dụ hỏi sâu về năm xây dựng hầm rượu ở Bà Nà Hills `[G02]`), System Prompt nghiêm ngặt kết hợp `temperature = 0.1` sẽ kích hoạt điều khoản từ chối ở tầng sinh ngôn ngữ, không để mô hình suy đoán.
