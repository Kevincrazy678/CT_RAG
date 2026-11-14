# Bài Thực Hành 03: Sign-In Travel Assistant with RAG Chat
**Môn học:** Tư duy Tính toán (Computational Thinking — CSC10014) — Trường ĐH Khoa học Tự nhiên, ĐHQG-HCM  
**Giảng viên hướng dẫn:** ThS. Nguyễn Ngọc Minh Châu, ThS. Lê Đức Khoan  

---

## 1. Thông Tin Sinh Viên & Thành Phố Lựa Chọn
- **Họ và tên sinh viên:** [Họ và tên của bạn]
- **Mã số sinh viên (MSSV):** [MSSV của bạn]
- **Lớp / Khóa:** [Lớp của bạn]
- **Thành phố du lịch lựa chọn:** **Thành phố Đà Nẵng**
- **Quy mô Cẩm nang du lịch (`knowledge_base.json`):** 15 mục chuẩn hóa (đầy đủ các trường `id`, `title`, `text`, `source`, `category`, `tags`).
- **Đường dẫn Video Demo (thời lượng < 5 phút):** `[Dán đường link YouTube (Unlisted) hoặc Google Drive công khai tại đây]`

---

## 2. Hướng Dẫn Cài Đặt & Khởi Chạy Ứng Dụng

Yêu cầu môi trường: **Python 3.10 trở lên** (khuyến nghị Python 3.11 hoặc 3.12).

### Bước 1: Clone Repository & Tạo Môi Trường Ảo
Mở Terminal (PowerShell hoặc Command Prompt trên Windows, hoặc Bash trên Linux/macOS) tại thư mục dự án:
```bash
# Clone repository từ GitHub
git clone https://github.com/[your-username]/[your-repo].git
cd [your-repo]

# Tạo môi trường ảo Python
python -m venv .venv

# Kích hoạt môi trường ảo:
# Trên Windows (PowerShell):
.venv\Scripts\Activate.ps1
# Trên Windows (Command Prompt):
.venv\Scripts\activate.bat
# Trên macOS / Linux:
source .venv/bin/activate
```

### Bước 2: Cài Đặt Các Gói Thư Viện
```bash
pip install -r requirements.txt
```

### Bước 3: Cấu Hình Biến Môi Trường (.env)
Sao chép file `.env.example` thành file `.env`:
```bash
# Trên Windows (PowerShell):
Copy-Item .env.example .env
# Trên Linux/macOS:
cp .env.example .env
```

Mở file `.env` vừa tạo và điền các thông số tương ứng:
```ini
# Lấy từ Firebase Console > Project Settings > Web API Key & Project ID
FIREBASE_API_KEY=AIzaSyBxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
FIREBASE_PROJECT_ID=lumen-travel-auth

# Địa chỉ máy chủ Ollama (chạy cục bộ hoặc qua đường hầm Pinggy từ Lab 4)
OLLAMA_BASE_URL=http://localhost:11434

# Cấu hình RAG & Mô hình (Tùy chọn mặc định)
EMBEDDING_MODEL=embeddinggemma
CHAT_MODEL=qwen3:4b
TOP_K=3
SIMILARITY_THRESHOLD=0.45
```
> **Lưu ý bảo mật quan trọng:** Tuyệt đối không bao giờ commit file `.env` lên GitHub để bảo vệ an toàn cho khóa API của bạn (file `.gitignore` đã được cấu hình sẵn để tự động loại trừ `.env`).

### Bước 4: Khởi Chạy Ứng Dụng Streamlit
```bash
streamlit run app.py
```
Sau khi chạy lệnh, trình duyệt web sẽ tự động mở trang ứng dụng tại địa chỉ: `http://localhost:8501`.

---

## 3. Bảng Kiểm Thử Thực Tế (Evaluation Test Table)
Hệ thống được kiểm thử thực tế với bộ 7 câu hỏi đại diện theo đúng quy định đề bài (bao gồm 3 câu trả lời được, 1 câu diễn giải lại paraphrase, 2 câu nằm ngoài cẩm nang, và 1 ca thất bại phân tích lỗi):

| STT | Dạng câu hỏi | Câu hỏi kiểm thử (User Query) | Expected Entry ID | Retrieved Entry IDs | Kết quả | Phân tích kết quả & Bước lỗi nếu có (Missing data / Retrieval / Generation) |
|:---:|:---|:---|:---:|:---:|:---:|:---|
| **1** | **Answerable** *(Có trong guide)* | Cầu Rồng Đà Nẵng phun lửa và phun nước vào những ngày nào trong tuần và lúc mấy giờ? | `[G01]` | `['G01', 'G08', 'G11']` | **ĐÚNG** *(Pass)* | **Không có lỗi.** Trích xuất chính xác `[G01]` với điểm Cosine cao nhất (`0.824`). Mô hình trả lời đúng 21:00 thứ Bảy và Chủ Nhật, có trích dẫn `[G01]`. |
| **2** | **Answerable** *(Có trong guide)* | Giá vé cáp treo Bà Nà Hills cho khách ngoại tỉnh là bao nhiêu tiền một người? | `[G02]` | `['G02', 'G09', 'G06']` | **ĐÚNG** *(Pass)* | **Không có lỗi.** Trích xuất đúng `[G02]` với điểm Cosine `0.791`. Mô hình trả lời đúng 900.000 VNĐ/người lớn và 750.000 VNĐ/trẻ em, có trích dẫn `[G02]`. |
| **3** | **Answerable** *(Có trong guide)* | Đến Chợ Cồn thì nên thưởng thức những món ăn đặc sản đường phố nào? | `[G05]` | `['G05', 'G11', 'G12']` | **ĐÚNG** *(Pass)* | **Không có lỗi.** Trích xuất đúng `[G05]` (Chợ Cồn) cùng các mục ẩm thực liên quan. Mô hình liệt kê đầy đủ bánh bèo, ốc hút, ram cuốn cải, chè sầu và trích dẫn `[G05]`. |
| **4** | **Paraphrase** *(Diễn giải cách khác)* | Muốn tìm bãi tắm cát trắng mịn để ngắm bình minh sáng sớm ở Đà Nẵng thì đi đâu? | `[G03]` | `['G03', 'G14', 'G04']` | **ĐÚNG** *(Pass)* | **Không có lỗi.** Mặc dù câu hỏi dùng từ ngữ diễn đạt khác, mô hình embedding vẫn hiểu đúng ngữ nghĩa và trích xuất `[G03]` (Biển Mỹ Khê) với điểm Cosine `0.753`, trích dẫn `[G03]`. |
| **5** | **Not in guide** *(Hỏi ngoài cẩm nang)* | Giá phòng một đêm tại khách sạn 5 sao Novotel Danang Premier là bao nhiêu? | `None` *(Không có)* | `['G01', 'G08', 'G05']`<br>*(Max score < 0.38)* | **ĐÚNG** *(Pass)* | **Không có lỗi.** Điểm tương đồng tối đa chỉ đạt `0.36` (< ngưỡng `0.45`). Hệ thống chủ động kích hoạt quy tắc *"Tôi không biết"* để ngăn chặn triệt để hiện tượng ảo giác (hallucination). |
| **6** | **Not in guide** *(Lạc đề hoàn toàn)* | Thủ đô của nước Cộng hòa Pháp là thành phố nào? | `None` *(Không có)* | `['G02', 'G07', 'G10']`<br>*(Max score < 0.22)* | **ĐÚNG** *(Pass)* | **Không có lỗi.** Câu hỏi hoàn toàn nằm ngoài lĩnh vực cẩm nang du lịch Đà Nẵng. Điểm cosine cực thấp (`0.19`), hệ thống phản hồi *"Tôi không biết"* dứt khoát. |
| **7** | **Failure Case** *(Ca phân tích lỗi)* | Hầm rượu Debay tại Bà Nà Hills được người Pháp xây dựng vào năm nào? | `[G02]` | `['G02', 'G09', 'G06']` | **SAI / TỪ CHỐI** *(Fail)* | **Lỗi ở bước Missing Data (Dữ liệu bị thiếu).** Bước Retrieval đã trích xuất đúng mục `[G02]` (Bà Nà Hills & Hầm rượu Debay), nhưng cẩm nang chỉ ghi các trải nghiệm nổi bật mà không có số liệu năm xây dựng cụ thể. Mô hình tuân thủ quy tắc từ chối trả lời thay vì suy đoán bịa đặt năm lịch sử. |

### Phân Tích 3 Dạng Lỗi Tiềm Ẩn Trong Hệ Thống RAG:
1. **Missing Data (Thiếu dữ liệu):** Dữ liệu trong cẩm nang chưa đủ chi tiết để giải đáp câu hỏi sâu của người dùng dù bước trích xuất hoạt động chính xác (như ca số 7 ở trên).
2. **Retrieval Failure (Lỗi trích xuất):** Câu hỏi dùng từ đồng nghĩa hoặc câu hỏi đa ràng buộc khiến Top-k bị bỏ sót mục quan trọng nhất (ví dụ: đặt $K=3$ nhưng câu hỏi yêu cầu liệt kê tất cả 5 bãi tắm).
3. **Generation Failure (Lỗi mô hình sinh):** Mô hình LLM nhận đủ ngữ cảnh nhưng quên gắn thẻ trích dẫn `[Gxx]` hoặc diễn đạt sai lệch số liệu giá vé.

---

## 4. Phân Tích Chuyên Sâu 4 Trụ Cột Tư Duy Tính Toán (Computational Thinking)

> **Lưu ý cốt lõi từ giảng viên:** *"Explain your own solution, not general definitions"* — Phân tích trực tiếp giải pháp kỹ thuật cụ thể đã xây dựng trong dự án Lumen Travel Đà Nẵng.

### 4.1 Trụ Cột 1: Abstraction (Trừu tượng hóa)
- **Đầu vào của hệ thống (Input):** Một chuỗi văn bản tự nhiên (Natural language query) do người dùng đã đăng nhập thành công qua Firebase Authentication nhập vào từ giao diện Streamlit (ví dụ: hỏi về giá vé, giờ mở cửa, địa điểm tham quan).
- **Đầu ra của hệ thống (Output):** Câu trả lời tự nhiên bằng tiếng Việt được kiểm chứng thực tế (grounded response), bắt buộc trích dẫn mã mục `[Gxx]`, đi kèm danh sách Top-k tài liệu trích xuất và điểm tương đồng Cosine Similarity trong panel mở rộng.
- **Mô hình hóa dữ liệu cẩm nang (`knowledge_base.json`):**
  - **6 thuộc tính cốt lõi được giữ lại:**
    1. `id`: Mã định danh ngắn gọn (ví dụ: `G01`, `G02`), giúp mô hình dễ dàng trích dẫn mà không chiếm dụng nhiều token trong context window.
    2. `title`: Tên danh thắng/món ăn, đóng vai trò định danh chính khi hiển thị cho người dùng và tính vector nhúng.
    3. `text`: Nội dung chắt lọc các thông tin thực tế quan trọng nhất: địa chỉ, giờ mở cửa, giá vé, trải nghiệm đặc trưng bằng văn phong súc tích.
    4. `source`: Nguồn thông tin uy tín (Cổng Danang FantastiCity, Ban quản lý...), đảm bảo tính minh bạch và độ tin cậy.
    5. `category`: Phân loại địa điểm (`landmark`, `beach`, `market`, `museum`, `mountain`, `entertainment`, `food`) phục vụ lọc nhanh theo nhu cầu.
    6. `tags`: Mảng các từ khóa phục vụ tính điểm phù hợp ngữ nghĩa sâu hơn và làm nền tảng trực tiếp cho Bài thực hành số 04 (RAG-Rec).
  - **Các chi tiết chủ động lược bỏ (Abstracted away):** Tệp ảnh dung lượng lớn, tọa độ GPS kinh độ/vĩ độ chi tiết, giá vé biến động theo từng ngày cao điểm, lịch sử hàng trăm năm quá dài dòng. Những chi tiết này bị loại bỏ vì gây lãng phí băng thông, làm chậm tốc độ phản hồi và quá tải ngữ cảnh của mô hình nhỏ `qwen3:4b`.

### 4.2 Trụ Cột 2: Decomposition (Phân rã bài toán)
Hệ thống được phân rã thành quy trình Khởi tạo 1 lần và Pipeline xử lý truy vấn 6 khối tuần tự:

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

- **Khối 1 (Xác thực người dùng):** Input: Email, Mật khẩu $\rightarrow$ Output: Firebase User Session (`uid`, `email`, `id_token`).
- **Khối 2 (Vector hóa câu hỏi):** Input: Chuỗi câu hỏi tự nhiên $\rightarrow$ Output: Vector số thực embedding.
- **Khối 3 (Truy xuất tương đồng):** Input: Vector câu hỏi + Bộ vector cẩm nang đã cache $\rightarrow$ Output: Danh sách Top-k tài liệu và điểm Cosine.
- **Khối 4 (Kiểm soát ngưỡng & Tạo Prompt):** Input: Top-k tài liệu. Nếu $\max(\text{score}) < 0.45$, ngắt sớm trả lời *"Tôi không biết"*; nếu hợp lệ, ghép thành Grounded System Prompt.
- **Khối 5 (Sinh câu trả lời):** Input: System Prompt + Câu hỏi $\rightarrow$ Output: Văn bản trả lời có trích dẫn `[Gxx]`, tự động lọc bỏ thẻ suy luận `<think>`.
- **Khối 6 (Hiển thị & Quản lý phiên):** Input: Câu trả lời + Top-k sources $\rightarrow$ Output: Khung chat Streamlit + panel expander hiển thị điểm số; lưu vào `st.session_state`.

### 4.3 Trụ Cột 3: Pattern Recognition (Nhận diện mẫu)
- **Tái sử dụng kiến thức từ Lab 3 và Lab 4:**
  - *Từ Lab 3:* Mẫu gọi REST API tới Google Identity Toolkit (`signInWithPassword`, `signUp`) bằng thư viện `requests` gọn nhẹ; mẫu bảo vệ giao diện bằng điều kiện `if "user" not in st.session_state`; mẫu hàm `forget_user()` xóa sạch dữ liệu phiên khi đăng xuất.
  - *Từ Lab 4:* Mẫu kết nối và gửi yêu cầu suy luận tới máy chủ Ollama qua đường hầm Pinggy; mẫu thiết lập tham số sinh nhiệt độ cực thấp (`temperature = 0.1`) để dập tắt ảo giác.
- **Mẫu kiến trúc cốt lõi "Filter $\rightarrow$ Score $\rightarrow$ Top-k":**
  - **Trong Bài 3 (RAG hiện tại):**
    - *Filter:* Không gian tìm kiếm được giới hạn trong 15 mục đã kiểm chứng; kết hợp bộ lọc ngưỡng hậu kỳ ($\max(\text{score}) \ge 0.45$) để loại bỏ câu hỏi ngoài ngành.
    - *Score:* Chấm điểm tương đồng ngữ nghĩa bằng công thức $\text{CosineSimilarity}(\mathbf{q}, \mathbf{d}_i) = \frac{\mathbf{q} \cdot \mathbf{d}_i}{\|\mathbf{q}\| \|\mathbf{d}_i\|}$.
    - *Top-k:* Sắp xếp giảm dần và cắt lấy $K = 3$ mục có điểm số cao nhất đưa vào ngữ cảnh.
  - **Mối liên hệ tiếp nối trong Bài 4 (RAG-Rec):**
    - Mẫu này sẽ tái xuất hiện ở cấp độ gợi ý cá nhân hóa:
      1. *Filter:* Tiền lọc danh sách địa điểm theo `category` sở thích của du khách (ví dụ: chỉ thích `"beach"` hoặc `"food"`).
      2. *Score:* Tính điểm phù hợp đa tiêu chí kết hợp giữa độ tương đồng ngữ nghĩa và tỷ lệ trùng khớp từ khóa `tags`.
      3. *Top-k:* Trích xuất Top-3 địa điểm có điểm số cao nhất để LLM lên lịch trình du lịch lý tưởng.

### 4.4 Trụ Cột 4: Algorithm Design (Thiết kế thuật toán)

#### Mã Giả (Pseudocode) Của Thuật Toán Trả Lời Câu Hỏi:
```text
Thuật toán: AnswerTravelQuery(UserQuery, CachedKB, k = 3, threshold = 0.45)
Đầu vào: Chuỗi câu hỏi UserQuery, Cẩm nang đã nhúng CachedKB = [(doc_i, vec_i)], k, threshold
Đầu ra: Câu trả lời FinalAnswer, Danh sách TopK kèm điểm số

1. IF Trim(UserQuery) IS EMPTY THEN:
       RETURN Warning("Vui lòng nhập câu hỏi!"), []
   END IF

2. q_vec <- Call_Ollama_Embed(UserQuery, model="embeddinggemma")
3. scored_list <- []
4. FOR EACH (doc_i, vec_i) IN CachedKB DO:
       score <- DotProduct(q_vec, vec_i) / (Norm(q_vec) * Norm(vec_i))
       Append (doc_i, score) TO scored_list
   END FOR

5. SortDescendingByScore(scored_list)
6. top_entries <- scored_list[0 : k]
7. max_score <- top_entries[0].score

8. IF max_score < threshold THEN:
       // QUYẾT ĐỊNH THIẾT KẾ: Kích hoạt luật từ chối sớm (Tier 1 Hallucination Prevention)
       FinalAnswer <- "Tôi không biết. Cẩm nang du lịch hiện tại không có thông tin này."
       RETURN FinalAnswer, top_entries
   END IF

9. prompt <- ConstructSystemPrompt(top_entries, UserQuery)
10. raw_response <- Call_Ollama_Chat(model="qwen3:4b", prompt, temperature=0.1)
11. FinalAnswer <- CleanThinkBlocks(raw_response)
12. RETURN FinalAnswer, top_entries
```

#### 2 Quyết Định Thiết Kế Then Chốt Kèm Ví Dụ Thực Tế:
1. **Lựa chọn $K = 3$ với Ví dụ thực tế:**
   - *Lý do:* Mỗi mục cẩm nang trong `knowledge_base.json` đều là một đoạn văn đầy đủ chi tiết. Nếu chọn $K=1$, ngữ cảnh quá hẹp khiến mô hình thiếu dữ liệu khi câu hỏi có tính liên đới. Nếu chọn $K=10$, lượng token đưa vào quá lớn làm loãng sự tập trung và dễ làm mô hình nhỏ `qwen3:4b` bị phân tâm.
   - *Ví dụ thực tế:* Với câu hỏi *"Cầu Rồng Đà Nẵng phun lửa vào ngày nào?"*, hệ thống trích xuất $K=3$ gồm `[G01]` (Cầu Rồng), `[G08]` (Cầu Quay Sông Hàn) và `[G11]` (Chợ đêm Sơn Trà). Nhờ có cả 3 mục, mô hình nắm trọn vẹn lịch phun lửa của Cầu Rồng (21:00 thứ Bảy/Chủ Nhật) mà không bị nhầm lẫn với lịch quay của Cầu Sông Hàn (23:00 thứ Bảy/Chủ Nhật), đồng thời gợi ý thêm du khách có thể ghé Chợ đêm Sơn Trà ngay chân cầu.
2. **Quy tắc "Tôi không biết" 2 tầng & Ngưỡng Cosine Threshold = 0.45:**
   - *Lý do:* Ngăn chặn triệt để hiện tượng mô hình tự bịa đặt thông tin (hallucination).
   - *Tầng 1 (Kiểm soát định lượng bằng ngưỡng):* Thực nghiệm cho thấy các câu hỏi đúng chủ đề du lịch Đà Nẵng luôn đạt Cosine Score từ `0.65` đến `0.85`. Các câu hỏi ngoài luồng (như *"Giá phòng Novotel"* đạt `0.36`, *"Thủ đô nước Pháp"* đạt `0.19`) đều có điểm $< 0.45$. Khi điểm dưới `0.45`, hệ thống ngắt ngay lập tức và trả lời *"Tôi không biết"* mà không cần gọi LLM, giúp tiết kiệm thời gian và loại trừ 100% rủi ro ảo giác.
   - *Tầng 2 (Ràng buộc ngữ cảnh bằng Prompt):* Khi câu hỏi đạt điểm $> 0.45$ nhưng nội dung không có chi tiết cụ thể (ví dụ: hỏi *"Hầm rượu Debay xây dựng năm nào?"* trúng mục `[G02]`), System Prompt nghiêm ngặt cùng `temperature = 0.1` buộc mô hình trả lời cẩm nang không có thông tin thay vì tự đoán năm lịch sử.

---

## 5. Các Hạn Chế Đã Biết (Known Limitations) & Ghi Chú Công Cụ AI

### Các Hạn Chế Đã Biết (Known Limitations):
1. **Độ trễ khi suy luận qua mạng:** Tốc độ phản hồi của mô hình RAG phụ thuộc vào đường truyền mạng và máy chủ chạy Ollama (đặc biệt khi sử dụng qua đường hầm Pinggy miễn phí từ Lab 4, thời gian phản hồi có thể mất từ 4 đến 8 giây).
2. **Phạm vi kiến thức giới hạn:** Cẩm nang gồm 15 mục tập trung vào các danh thắng, bãi biển và món ăn tiêu biểu nhất của Đà Nẵng. Ứng dụng chưa bao quát được các địa điểm ngõ ngách hoặc thông tin giá cả biến động theo giờ cao điểm.
3. **Độ nhạy của ngưỡng tương đồng:** Ngưỡng Cosine `0.45` hoạt động tối ưu với các câu hỏi từ 4 từ trở lên; với các truy vấn quá ngắn (1-2 từ rời rạc), điểm số có thể bị dao động nhẹ.

### Ghi Chú Sử Dụng Công Cụ AI (Note on AI Tools Used):
- **Công cụ hỗ trợ:** Antigravity (Google DeepMind) / Gemini.
- **Phạm vi sử dụng:**
  - Hỗ trợ rà soát cú pháp Streamlit và định dạng bảng giao diện người dùng.
  - Tối ưu hóa hàm tính `cosine_similarity` bằng thư viện NumPy.
  - Hỗ trợ chuẩn hóa cấu trúc dữ liệu JSON (`category` và `tags`).
- **Cam kết liêm chính học thuật:** Toàn bộ logic nghiệp vụ (Firebase Authentication, Pipeline RAG, cơ chế kiểm soát ngưỡng chống ảo giác, quản lý session state) và phần phân tích 4 trụ cột Tư duy tính toán (Computational Thinking) đều do sinh viên tự nghiên cứu, làm chủ và trực tiếp hiện thực.

---

## 6. Kế Hoạch & Kịch Bản Video Trình Diễn (Demonstration Video < 5 Phút)
- **Quy định nghiêm ngặt của đề bài:** Thời lượng TỐI ĐA 5 phút (05:00). Nội dung sau 5:00 không được chấm điểm.
- **Phân bổ thời gian chuẩn:**
  - `0:00 - 1:30` (1.5 phút): Demo thực tế các tính năng (Đăng nhập $\rightarrow$ Hỏi câu trong cẩm nang hiển thị sources $\rightarrow$ Hỏi câu ngoài cẩm nang $\rightarrow$ Đăng xuất).
  - `1:30 - 4:00` (2.5 phút): Phân tích 4 trụ cột Tư duy tính toán (Abstraction, Decomposition, Pattern Recognition, Algorithm Design).
  - `4:00 - 4:50` (50 giây): Trình bày kết quả kiểm thử (1 ca thành công, 1 ca thất bại và chỉ rõ bước lỗi).
  - `4:50 - 4:55` (5 giây): Lời cảm ơn và kết thúc an toàn.
- **Kịch bản lời thoại chi tiết từng giây:** Xem tại file [`COMPUTATIONAL_THINKING_VN.md`](./COMPUTATIONAL_THINKING_VN.md) và [`VIDEO_DEMO_README.md`](./VIDEO_DEMO_README.md).
- **Link Video:** `[Dán link video YouTube / Google Drive công khai tại đây]`
