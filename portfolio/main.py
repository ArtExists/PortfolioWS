import http.server
import socketserver
import json
import os
import urllib.request

# Load dotenv if running locally
try:
    import dotenv
    dotenv.load_dotenv(os.path.join(os.path.dirname(__file__), ".env"))
except Exception:
    pass

PORT = 8000
RESUME_PDF_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "ART_Resume-2.pdf")

# Extract resume text if PDF exists, otherwise fallback to built-in resume context
RESUME_TEXT = """
ALOK RANJAN TRIPATHY
B.Tech in Computer Science and Engineering, IIIT Bhubaneswar (Expected: 2028)
Email: alokrtofc@gmail.com | Phone: +91 7978631653
GitHub: github.com/ArtExists | LinkedIn: linkedin.com/in/alok-ranjan-tripathy

Skills:
- Python, C, C++, Git, Jupyter, Streamlit, Flask
- PyTorch, TensorFlow, scikit-learn, pure NumPy
- OpenCV, MediaPipe, YOLO, Segment Anything (SAM)
- LangChain, LangGraph, RAG, DDPM Diffusion

Featured Projects:
1. TryThyEye: Real-time virtual sunglasses try-on system leveraging SAM & YOLO with perspective warping.
2. Numpy_ANN_Mnist: Built a fully connected Neural Network from scratch in pure mathematical NumPy with SGD & backprop (85%+ accuracy).
3. PhilGTP: Philosophical conversational RAG system grounding responses in classic philosopher PDFs via LangChain & Mistral.
4. MNIST_Diffusion: Denoising Diffusion Probabilistic Model (DDPM) built with a custom UNet for image synthesis from noise.
5. HGR_Temple_Run: Real-time hand gesture recognition system interfacing OpenCV & MediaPipe for game navigation.
6. Emotion_Det: Unified multimodal perception pipeline combining facial landmarks, audio features, and NLP.
"""

try:
    if os.path.exists(RESUME_PDF_PATH):
        import pypdf
        reader = pypdf.PdfReader(RESUME_PDF_PATH)
        pages = [p.extract_text() for p in reader.pages if p.extract_text()]
        if pages:
            RESUME_TEXT = "\n\n".join(pages)
except Exception:
    pass

def query_mistral_api(user_message: str) -> str:
    raw_key = os.environ.get("MISTRAL_API_KEY", "")
    api_key = raw_key.strip().strip('"').strip("'")
    
    if not api_key:
        return get_fallback_answer(user_message)
    
    system_prompt = (
        "You are 'Ask_ART', an intelligent, polite, and charismatic AI spirit guide and portfolio companion "
        "for Alok Ranjan Tripathy (Computer Science undergraduate at IIIT Bhubaneswar).\n"
        "Answer questions from visitors, recruiters, and engineers accurately based on Alok's resume below.\n\n"
        f"{RESUME_TEXT}\n\n"
        "GUIDELINES:\n"
        "1. Be direct, concise, and structured (2-4 sentences or clean bullet points).\n"
        "2. Add a tasteful subtle Japanese aesthetic spirit (e.g., 'ようこそ', 'Konnichiwa', '⛩️', '🌸', '✨').\n"
        "3. Ground all answers accurately in Alok's skills, projects (TryThyEye, NumPy ANN, PhilGTP, Diffusion, HGR), and IIIT Bhubaneswar education.\n"
        "4. Mention his email alokrtofc@gmail.com and the 'Download Resume' button if asked."
    )
    
    payload = {
        "model": "open-mistral-7b",
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_message}
        ],
        "temperature": 0.3,
        "max_tokens": 400
    }
    
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
        "Accept": "application/json"
    }
    
    try:
        req = urllib.request.Request(
            "https://api.mistral.ai/v1/chat/completions",
            data=json.dumps(payload).encode("utf-8"),
            headers=headers,
            method="POST"
        )
        with urllib.request.urlopen(req, timeout=9) as resp:
            if resp.status == 200:
                body = json.loads(resp.read().decode("utf-8"))
                reply = body["choices"][0]["message"]["content"]
                if reply and reply.strip():
                    return reply.strip()
    except Exception:
        pass
        
    return get_fallback_answer(user_message)


def get_fallback_answer(user_message: str) -> str:
    msg = (user_message or "").lower().strip()
    if not msg:
        return "ようこそ! I am Ask_ART, your spirit guide to Alok's portfolio. Ask me about his projects, skills, CV models, or education! ⛩️"
    
    if any(k in msg for k in ["hi", "hello", "hey", "konnichiwa", "greetings", "who are you"]):
        return "Konnichiwa! ⛩️ I'm Ask_ART — Alok's portfolio assistant powered by Mistral AI. I can tell you all about his Computer Vision systems, Deep Learning models, RAG chatbots, and research at IIIT Bhubaneswar!"
    
    if any(k in msg for k in ["project", "build", "trythyeye", "numpy", "philgtp", "diffusion", "temple run", "emotion"]):
        if "trythyeye" in msg or "sunglasses" in msg:
            return "🕶️ **TryThyEye**: A real-time computer vision system using SAM (Segment Anything), YOLO, and MediaPipe to detect facial landmarks, segment sunglasses, and virtually try them on with accurate occlusion and perspective mapping!"
        if "numpy" in msg or "mnist" in msg or "scratch" in msg:
            return "🧠 **Numpy_ANN_Mnist**: A handwritten digit classifier built from pure mathematical first principles in NumPy without PyTorch/TensorFlow — featuring forward propagation, backpropagation, and SGD achieving 85%+ test accuracy!"
        if "philgtp" in msg or "rag" in msg or "philosophy" in msg:
            return "📜 **PhilGTP**: An LLM-driven philosophical dialogue engine grounded in classic philosopher texts via Retrieval-Augmented Generation (RAG) and LangChain to prevent hallucinations!"
        if "diffusion" in msg or "ddpm" in msg:
            return "✨ **MNIST_Diffusion**: A Denoising Diffusion Probabilistic Model (DDPM) powered by a custom UNet to synthesize realistic handwritten digits from pure Gaussian noise!"
        if "gesture" in msg or "temple run" in msg or "hgr" in msg:
            return "🎮 **HGR_Temple_Run**: Real-time hand gesture recognition system interfacing OpenCV and MediaPipe to control game navigation purely through hand movements!"
        if "emotion" in msg or "multimodal" in msg:
            return "🎭 **Emotion_Det**: A unified multimodal perception pipeline fusing facial landmark analysis, audio voice feature maps, and NLP for holistic human social cue understanding!"
        return "🌸 Alok has built 6 standout AI/ML projects: **TryThyEye** (SAM+YOLO virtual try-on), **Numpy_ANN_Mnist** (from-scratch neural net), **PhilGTP** (LangChain RAG), **MNIST_Diffusion** (DDPM UNet), **HGR_Temple_Run** (Gesture Control), and **Emotion_Det** (Multimodal AI)."
        
    if any(k in msg for k in ["skill", "stack", "tech", "languages", "python", "pytorch", "cv", "vision"]):
        return "⚔️ **Alok's Tech Arsenal** (from Resume):\n• **Languages**: Python, C, C++\n• **Computer Vision**: SAM (Segment Anything), YOLO, MediaPipe, OpenCV\n• **Deep Learning**: PyTorch, TensorFlow, scikit-learn, NumPy\n• **GenAI & RAG**: LangChain, LangGraph, Vector Stores\n• **Tools**: Git, Jupyter, Streamlit, Flask"

    if any(k in msg for k in ["study", "college", "iiit", "education", "bhubaneswar", "degree", "undergrad"]):
        return "🎓 Alok is pursuing his B.Tech in **Computer Science & Engineering at IIIT Bhubaneswar** (Expected 2028). He also completed Tata iQ's virtual AI & Data Analytics simulation via Forage in 2025!"

    if any(k in msg for k in ["contact", "email", "hire", "github", "linkedin", "reach"]):
        return "✉️ You can reach Alok via:\n• **Email**: alokrtofc@gmail.com\n• **GitHub**: github.com/ArtExists\n• **LinkedIn**: linkedin.com/in/alok-ranjan-tripathy\nHe's open to collaborations, research, and internship opportunities!"

    if any(k in msg for k in ["resume", "cv", "pdf"]):
        return "📄 You can view and download Alok's official resume (`ART_Resume-2.pdf`) directly using the 'Download Resume' button in the navigation bar!"

    return f"✨ Ask_ART received: '{user_message}'. Alok specializes in Computer Vision (SAM, YOLO), Generative AI (Diffusion, RAG), and Deep Learning at IIIT Bhubaneswar. Feel free to ask about his projects, skills, or contact info!"


class PortfolioRequestHandler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        if self.path == "/api/chat":
            self.send_response(200)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.send_header("Access-Control-Allow-Origin", "*")
            self.end_headers()
            self.wfile.write(json.dumps({"status": "healthy", "service": "Ask_ART Chatbot API"}).encode("utf-8"))
        else:
            super().do_GET()

    def do_POST(self):
        if self.path == "/api/chat":
            try:
                content_length = int(self.headers.get("Content-Length", 0))
                post_data = self.rfile.read(content_length) if content_length > 0 else b"{}"
                data = json.loads(post_data.decode("utf-8")) if post_data else {}
                user_msg = data.get("message", "")
                
                bot_reply = query_mistral_api(user_msg)
                response_data = {"reply": bot_reply}
                
                self.send_response(200)
                self.send_header("Content-Type", "application/json; charset=utf-8")
                self.send_header("Access-Control-Allow-Origin", "*")
                self.end_headers()
                self.wfile.write(json.dumps(response_data, ensure_ascii=False).encode("utf-8"))
            except Exception as e:
                self.send_response(200)
                self.send_header("Content-Type", "application/json; charset=utf-8")
                self.send_header("Access-Control-Allow-Origin", "*")
                self.end_headers()
                self.wfile.write(json.dumps({"reply": get_fallback_answer(""), "error": str(e)}).encode("utf-8"))
        else:
            self.send_error(404, "Endpoint Not Found")

    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "POST, GET, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.end_headers()

# Vercel entrypoint exports
handler = PortfolioRequestHandler
app = PortfolioRequestHandler
application = PortfolioRequestHandler

if __name__ == "__main__":
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    socketserver.TCPServer.allow_reuse_address = True
    with socketserver.TCPServer(("", PORT), PortfolioRequestHandler) as httpd:
        print(f"Portfolio Server running at http://localhost:{PORT}")
        print(f"Chat API Endpoint: http://localhost:{PORT}/api/chat (Mistral Powered)")
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\nShutting down server.")
