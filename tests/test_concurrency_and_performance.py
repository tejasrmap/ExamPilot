import concurrent.futures
from fastapi.testclient import TestClient
from backend.app.main import app

client = TestClient(app)

def test_concurrent_api_traffic():
    """
    Simulates concurrent requests across multiple sessions to verify database connection pooling.
    """
    def make_request(i):
        # Health check
        h = client.get("/")
        assert h.status_code == 200
        # Parse question via OCR status
        s = client.get("/api/ocr/status")
        assert s.status_code == 200
        return True

    with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
        futures = [executor.submit(make_request, i) for i in range(25)]
        results = [f.result() for f in concurrent.futures.as_completed(futures)]

    assert len(results) == 25
    assert all(r is True for r in results)

def test_oversized_payload_handling():
    """
    Verifies that the server gracefully rejects or handles massive uploads.
    """
    # 5MB synthetic buffer
    large_buf = b"0" * (5 * 1024 * 1024)
    res = client.post(
        "/api/documents/upload",
        files={"file": ("large_text.txt", large_buf, "text/plain")}
    )
    # Without auth, must reject with 401 Unauthorized before loading into memory
    assert res.status_code == 401
