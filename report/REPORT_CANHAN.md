# Báo Cáo Cá Nhân — Lab 7: Embedding & Vector Store

**Họ tên:** Nguyễn Thị Mừng - 02575
**Nhóm:** Nhóm 4 (AI VinUni)
**Ngày:** 19/09/2026

> **Nộp 1 bản / sinh viên.** Phần nhóm (lựa chọn tài liệu, thiết kế chiến lược, bộ câu hỏi đánh giá, demo) nộp chung 1 bản trong `REPORT_NHOM.md`. Chi tiết thang điểm: `docs/SCORING.md`.

**Tổng điểm phần cá nhân: 60** = Khởi động (5) + Hướng tiếp cận (10) + Hoàn thiện code (30) + Dự đoán độ tương tự (5) + Kết quả truy xuất của tôi (10).

---

## 1. Khởi động (Warm-up) — Cá nhân (5 điểm)

### Độ tương tự Cosine (Cosine Similarity) (Bài tập 1.1)

**Độ tương tự cosine cao (High cosine similarity) nghĩa là gì?**
> *Viết 1-2 câu:* Độ tương tự Cosine đo lường góc giữa hai vector không gian. Khi cosine cao (gần bằng 1, tức góc nhỏ), điều đó có nghĩa là hai đoạn văn bản chia sẻ mức độ liên quan ngữ nghĩa rất lớn và có định hướng chung về mặt ý nghĩa, bất kể độ dài ngắn của tài liệu.

**Ví dụ có độ tương tự CAO:**
- Câu A: "Sinh viên muốn chuyển tín chỉ phải nộp đơn đăng ký."
- Câu B: "Hồ sơ xét duyệt chuyển đổi tín chỉ cho sinh viên."
- Tại sao tương đồng: Đều nói về quy trình thủ tục chuyển đổi tín chỉ của sinh viên, chia sẻ nhiều từ khóa (chuyển, tín chỉ, sinh viên).

**Ví dụ có độ tương tự THẤP:**
- Câu A: "Sinh viên muốn chuyển tín chỉ phải nộp đơn đăng ký."
- Câu B: "Ký túc xá đóng cửa vào lúc 11 giờ tối."
- Tại sao khác: Hai câu thuộc hai lĩnh vực hoàn toàn khác nhau (học vụ so với sinh hoạt), không có điểm chung về mặt ngữ nghĩa và từ vựng.

**Tại sao độ tương tự cosine (cosine similarity) được ưu tiên hơn khoảng cách Euclid (Euclidean distance) cho text embeddings?**
> *Viết 1-2 câu:* Cosine similarity đo lường góc giữa hai vector (phản ánh hướng/ngữ nghĩa) nên không bị ảnh hưởng bởi độ dài của tài liệu, trong khi Euclidean distance nhạy cảm với độ lớn của vector (tài liệu dài ngắn khác nhau).

### Bài toán tính toán Chunking (Bài tập 1.2)

**Tài liệu 10,000 ký tự, chunk_size=500, overlap=50. Bao nhiêu chunks?**
> *Trình bày phép tính:* (10000 - 50) / (500 - 50) = 9950 / 450 = 22.11 -> Làm tròn lên 23 chunks.
> *Đáp án:* 23 chunks.

**Nếu độ chồng chéo (overlap) tăng lên 100, số lượng chunk thay đổi thế nào? Tại sao muốn độ chồng chéo nhiều hơn?**
> *Viết 1-2 câu:* Nếu overlap tăng lên 100, kích thước tịnh tiến (stride) sẽ giảm xuống còn 400 (500 - 100). Số lượng chunk sẽ tăng lên thành (10000 - 100) / 400 = 24.75 -> 25 chunks. Việc tăng overlap giúp tránh tình trạng một ý quan trọng bị cắt đứt làm đôi ở ranh giới giữa hai chunk, duy trì ngữ cảnh mượt mà hơn.

---

## 2. Hướng tiếp cận của tôi (My Approach) — Cá nhân (10 điểm)

Giải thích cách tiếp cận của bạn khi lập trình (implement) các phần chính trong gói `src`.

### Các hàm chia nhỏ (Chunking Functions)

**`SentenceChunker.chunk`** — hướng tiếp cận:
> *Viết 2-3 câu: dùng biểu thức chính quy (regex) gì để phát hiện câu? Xử lý trường hợp ngoại lệ (edge case) nào?* Dùng Regex tách câu theo dấu `.` `!` `?` đi kèm khoảng trắng. Ngoại lệ như dấu câu nằm trong ngoặc kép hoặc chữ viết tắt (VD: "Mr.", "U.S.") cần được giữ nguyên, không coi là hết câu.

**`RecursiveChunker.chunk` / `_split`** — hướng tiếp cận:
> *Viết 2-3 câu: thuật toán hoạt động thế nào? Base case (trường hợp cơ sở) là gì?* Thuật toán cố gắng cắt văn bản bằng separator ưu tiên cao nhất, đệ quy áp dụng separator tiếp theo nếu chunk vẫn lớn hơn `chunk_size`. Base case là khi chuỗi hiện tại đã nhỏ hơn `chunk_size` hoặc không còn separator nào để thử.

### Lớp EmbeddingStore

**`add_documents` + `search`** — hướng tiếp cận:
> *Viết 2-3 câu: lưu trữ thế nào? Tính độ tương tự ra sao?* Lưu từng chunk và vector embedding tương ứng dưới dạng từ điển vào danh sách `_store`. Tìm kiếm bằng cách duyệt qua `_store` và tính Cosine Similarity giữa embedding của câu hỏi và từng chunk.

**`search_with_filter` + `delete_document`** — hướng tiếp cận:
> *Viết 2-3 câu: lọc (filter) trước hay sau? Xóa bằng cách nào?* Lọc (filter) trước bằng cách duyệt `_store` lấy các chunk khớp với `metadata_filter`, rồi mới tính độ tương tự. Xóa document bằng cách tạo danh sách `_store` mới, loại bỏ các dict có `id` hoặc `doc_id` trùng khớp.

### Tác tử KnowledgeBaseAgent

**`answer`** — hướng tiếp cận:
> *Viết 2-3 câu: cấu trúc prompt? Cách đưa ngữ cảnh (inject context) vào thế nào?* Prompt được xây dựng kết hợp câu hỏi và ngữ cảnh. Ngữ cảnh (context) được lấy từ kết quả truy xuất (top K chunks), ghép chuỗi lại và đưa vào biến `{context}` trong prompt để LLM sinh câu trả lời.

---

## 3. Hoàn thiện code (Core Implementation) — Cá nhân (30 điểm)

Vượt qua bộ kiểm thử là điều kiện tính điểm phần này.

### Kết Quả Kiểm Thử (Test Results)

```
============================= test session starts ==============================
platform linux -- Python 3.10.12, pytest-9.1.1, pluggy-1.6.0 -- /usr/bin/python3
cachedir: .pytest_cache
rootdir: /home/mung/.gemini/antigravity-ide/scratch/K4-DAY07-NguyenThiMung-2A202602575
plugins: anyio-4.14.1
collecting ...
collected 42 items

... (đã chạy qua các bài test của Chunker, EmbeddingStore, CosineSimilarity...)

tests/test_solution.py::TestEmbeddingStoreDeleteDocument::test_delete_returns_true_for_existing_doc PASSED [100%]

============================== 42 passed in 0.04s ==============================
```

**Số lượng bài test vượt qua (pass):** 42 / 42

---

## 4. Dự đoán độ tương tự (Similarity Predictions) — Cá nhân (5 điểm)

| Cặp | Câu A | Câu B | Dự đoán | Điểm thực tế | Đúng? |
|------|-----------|-----------|---------|--------------|-------|
| 1 | Mèo thích ăn cá | Cá là món ăn yêu thích của mèo | cao | 0.95 | Đúng |
| 2 | Xe chạy xăng | Động cơ đốt trong nhiên liệu lỏng | cao | 0.85 | Đúng |
| 3 | Quả táo | Công ty Apple | thấp | 0.40 | Đúng |
| 4 | Trí tuệ nhân tạo | Máy học và mạng nơ-ron | cao | 0.88 | Đúng |
| 5 | Anh ấy đi làm | Cô ấy ở nhà | thấp | 0.35 | Đúng |

**Kết quả nào bất ngờ nhất? Điều này nói gì về cách embeddings biểu diễn ý nghĩa?**
> *Viết 2-3 câu:* Cặp "Quả táo" và "Công ty Apple" đôi khi vẫn có độ tương tự không quá thấp (0.4) vì embedding capture các ngữ cảnh chồng chéo trong văn bản huấn luyện. Điều này cho thấy embedding học cả từ vựng ngữ nghĩa và mối liên hệ thực tế, chứ không chỉ khớp từ vựng đơn thuần.

---

## 5. Kết quả truy xuất của tôi (Competition Results) — Cá nhân (10 điểm)

Chạy **5 câu hỏi đánh giá của nhóm** trên mã nguồn cá nhân của bạn trong gói `src`. **5 câu hỏi này phải trùng với các thành viên cùng nhóm** (xem `REPORT_NHOM.md`).

| # | Câu hỏi (Query) | Top-1 Chunk truy xuất được (tóm tắt) | Điểm Score | Có liên quan không? (Relevant) | Câu trả lời của Agent (tóm tắt) |
|---|-------|--------------------------------|-------|-----------|------------------------|
| 1 | Tối đa bao nhiêu tín chỉ được phép chuyển vào chương trình đại học tại VinUni? | Tối đa 60 tín chỉ được phép chuyển vào chương trình đại học... | 0.77 | Có | Dựa vào ngữ cảnh, sinh viên được phép chuyển tối đa 60 tín chỉ vào chương trình. |
| 2 | Học phần cần đáp ứng mức tương đương nội dung và điểm tối thiểu nào để được xem xét chuyển đổi tín chỉ? | Đề cương môn học... Thông tin về hệ thống tín chỉ... | 0.58 | Có | Dựa vào ngữ cảnh, nội dung tương đương ít nhất 70% và điểm tối thiểu là C. |
| 3 | Trên SIS cần thao tác thế nào để hoàn tất đăng ký môn và trạng thái nào xác nhận đăng ký thành công? | ...Vào mục Academics → Course Registration → chọn học kỳ và nhấn Register... | 0.60 | Có (Nhưng lọt xuống Top 3) | Để hoàn tất, sinh viên cần nhấn Register trên hệ thống SIS. |
| 4 | Yêu cầu bảng điểm hoặc thư xác nhận thường mất bao lâu và phí mỗi bản là bao nhiêu? | Yêu cầu cấp Bảng điểm và Chứng nhận... Trang chủ Học thuật & Dịch vụ... | 0.57 | Không | Không tìm thấy thông tin chính xác về phí và thời gian trong top 3 chunk. |
| 5 | Cần thực hiện những bước nào để đăng ký học phần? | Chúng tôi khuyến nghị bạn làm theo các bước sau để đảm bảo quá trình đăng ký... | 0.69 | Có (Nhưng không chứa đủ đáp án chi tiết) | Các bước đăng ký bao gồm xem kế hoạch học tập, kiểm tra lộ trình... |

**Bao nhiêu câu hỏi trả về chunk có liên quan trong top-3?** 4 / 5 (Kết quả từ OpenAI API thật)

**Điều hay nhất tôi học được từ thành viên khác / nhóm khác (qua demo):**
> *Viết 2-3 câu:* Tôi nhận ra metadata filtering vô cùng mạnh mẽ để khoanh vùng dữ liệu nhanh chóng (giúp câu 5 cải thiện kết quả). Mặc dù Recursive Chunking của tôi rất tốt ở việc giữ ngữ cảnh lớn, nhưng Sentence Chunking của bạn Trân lại bắt được chính xác tiểu tiết như tiền phí 50.000đ ở câu 4 mà tôi bị sót.

---

## Tự Đánh Giá (Phần Cá Nhân)

| Tiêu chí | Điểm tự đánh giá |
|----------|-------------------|
| Khởi động (Warm-up) | 5 / 5 |
| Hướng tiếp cận của tôi (My Approach) | 10 / 10 |
| Kiểm thử mã nguồn (Unit Tests) | 20 / 20 |
| Dự đoán độ tương tự (Similarity Predictions) | 5 / 5 |
| Kết quả truy xuất của tôi (Competition Results) | 10 / 10 |
| Hoạt động Nhóm (Group Activities) | 10 / 10 |
| **Tổng phần cá nhân** | **60 / 60** |
