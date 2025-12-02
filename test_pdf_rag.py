import requests
import io
from pypdf import PdfWriter

API_URL = "http://localhost:8001/api/v1"

def create_sample_pdf(text: str) -> bytes:
    from reportlab.pdfgen import canvas
    buffer = io.BytesIO()
    p = canvas.Canvas(buffer)
    p.drawString(100, 750, text)
    p.save()
    return buffer.getvalue()

def verify_pdf_rag():
    # 1. Login
    email = "test@example.com"
    password = "password123"
    
    print(f"Logging in as {email}...")
    response = requests.post(f"{API_URL}/auth/login/access-token", data={"username": email, "password": password})
    if response.status_code != 200:
        print(f"Login failed: {response.text}")
        return
    token = response.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    
    # 2. Upload PDF
    print("Uploading PDF...")
    pdf_content = create_sample_pdf("The secret code is BLUE-OMEGA-99.")
    files = {'file': ('secret.pdf', pdf_content, 'application/pdf')}
    
    response = requests.post(f"{API_URL}/documents/upload/pdf", headers=headers, files=files)
    if response.status_code != 200:
        print(f"Upload failed: {response.text}")
        return
    print(f"Upload success: {response.json()}")
    
    # 3. Query
    print("Querying for secret code...")
    query = "What is the secret code?"
    response = requests.post(f"{API_URL}/chat/", json={"query": query}, headers=headers)
    
    if response.status_code != 200:
        print(f"Chat failed: {response.text}")
        return
        
    answer = response.json()["answer"]
    print(f"Answer: {answer}")
    
    if "BLUE-OMEGA-99" in answer:
        print("SUCCESS: RAG retrieved the correct information.")
    else:
        print("FAILURE: RAG did not retrieve the information.")

if __name__ == "__main__":
    # Install reportlab for PDF generation if needed
    try:
        import reportlab
    except ImportError:
        print("Please install reportlab: pip install reportlab")
        exit(1)
        
    verify_pdf_rag()
