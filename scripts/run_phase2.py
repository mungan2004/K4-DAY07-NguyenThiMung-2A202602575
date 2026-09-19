import os
import sys
from pathlib import Path

# Add the project root to sys.path so we can import src
project_root = Path(__file__).parent.parent
sys.path.append(str(project_root))

from src.store import EmbeddingStore
from src.embeddings import _mock_embed
from src.models import Document
from src.chunking import RecursiveChunker
from src.agent import KnowledgeBaseAgent

# Các file tài liệu đại học
DOC_FILES = [
    "data/university/chuyen-doi-tin-chi.md",
    "data/university/dang-ky-hoc-phan.md",
    "data/university/cap-bang-diem.md",
    "data/university/ky-thi-diem.md",
    "data/university/chinh-sach-quy-dinh.md"
]

BENCHMARK_QUERIES = [
    "Sinh viên có thể chuyển tối đa bao nhiêu tín chỉ vào chương trình đại học và điểm của các môn này được tính như thế nào?",
    "Làm thế nào để xử lý khi môn học muốn đăng ký đã bị đầy và hệ thống SIS có hỗ trợ danh sách chờ không?",
    "Sinh viên cần trả bao nhiêu tiền để xin cấp bảng điểm chính thức và nếu gửi quốc tế thì ai thanh toán phí vận chuyển?",
    "VinUni sử dụng thang điểm mấy và môn học nào không được tính vào GPA?",
    "Quy định nào áp dụng cho sinh viên về việc duy trì học bổng đầu vào?"
]

def load_university_docs(file_paths: list[str]) -> list[Document]:
    documents = []
    for raw_path in file_paths:
        path = Path(project_root / raw_path)
        if not path.exists():
            continue
            
        content = path.read_text(encoding="utf-8")
        
        # Parse basic metadata from the frontmatter-like content in the files manually for the demo
        doc_id = path.stem
        audience = "student"
        
        # Just use the whole content for the demo, frontmatter and all
        documents.append(
            Document(
                id=doc_id,
                content=content,
                metadata={
                    "source_url": f"https://registrar.vinuni.edu.vn/vi/{doc_id}",
                    "audience": audience,
                    "retrieved_at": "2026-09-19",
                    "document_version": "1.0",
                    "department": "academic-affairs"
                }
            )
        )
    return documents

def run_phase2():
    print("=== Tải tài liệu ===")
    docs = load_university_docs(DOC_FILES)
    print(f"Đã tải {len(docs)} tài liệu.")
    
    # 1. Khởi tạo Recursive Chunker với Markdown headings
    markdown_separators = ["\n# ", "\n## ", "\n### ", "\n\n", "\n", ". ", " "]
    chunker = RecursiveChunker(separators=markdown_separators, chunk_size=500)
    
    # Chunking
    chunked_docs = []
    for doc in docs:
        chunks = chunker.chunk(doc.content)
        for i, c in enumerate(chunks):
            chunked_docs.append(
                Document(
                    id=f"{doc.id}_chunk{i}",
                    content=c,
                    metadata=doc.metadata
                )
            )
            
    print(f"Tổng số chunks tạo ra bằng RecursiveChunker: {len(chunked_docs)}")
    
    # 2. Khởi tạo store
    store = EmbeddingStore(collection_name="phase2_store", embedding_fn=_mock_embed)
    store.add_documents(chunked_docs)
    
    # Thêm Mock LLM và KnowledgeBaseAgent
    def demo_llm(prompt: str) -> str:
        # Mock đơn giản: Lấy một phần context trong prompt để cho thấy LLM có đọc được
        return f"[AGENT ANSWER] Dựa vào tài liệu cung cấp: {prompt[-100:].replace(chr(10), ' ')}... => [Đã sinh ra câu trả lời dựa trên context]"

    agent = KnowledgeBaseAgent(store=store, llm_fn=demo_llm)
    
    # 3. Chạy Benchmark Queries
    print("\n=== ĐÁNH GIÁ 5 CÂU HỎI BENCHMARK ===")
    for idx, query in enumerate(BENCHMARK_QUERIES):
        print(f"\nQ{idx+1}: {query}")
        
        # Nếu là câu 5, thêm metadata filter
        filter_dict = None
        if idx == 4:
            filter_dict = {"audience": "student"}
            print(f"  [Áp dụng metadata filter: {filter_dict}]")
            
        if filter_dict:
            results = store.search_with_filter(query, top_k=2, metadata_filter=filter_dict)
        else:
            results = store.search(query, top_k=2)
            
        print("  --- Kết quả truy xuất (Retrieval) ---")
        for r_idx, r in enumerate(results):
            preview = r['content'].replace("\n", " ")[:150]
            print(f"  KQ {r_idx+1}: ID={r['id']} | Điểm={r['score']:.3f} | Nguồn={r['metadata'].get('source_url')}")
            print(f"  Trích xuất: {preview}...")
            
        print("  --- LLM Trả lời (Agent Answer) ---")
        # Agent.answer gọi store.search bên dưới, nhưng vì agent.answer không nhận filter_dict 
        # nên kết quả ở đây chỉ để demo LLM generation
        answer = agent.answer(query, top_k=2)
        print(f"  {answer}")

if __name__ == "__main__":
    run_phase2()
