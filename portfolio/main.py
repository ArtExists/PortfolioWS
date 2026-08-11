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
        "You are the AI portfolio assistant representing Alok Ranjan Tripathy, a Computer Science undergraduate at IIIT Bhubaneswar.\n"
        "Your role is to answer questions from recruiters, engineers, and visitors accurately and professionally based on Alok's resume below.\n\n"
        f"{RESUME_TEXT}\n\n"
        "CRITICAL INSTRUCTIONS:\n"
        "1. Perspective & Persona: Always refer to Alok in the third person ('Alok', 'he', 'his'). Never pretend to be Alok or speak in the first person ('I', 'me') as him.\n"
        "2. Tone: Professional, polite, articulate, and objective.\n"
        "3. No Emojis: Do NOT use any emojis or decorative symbols anywhere in your response.\n"
        "4. No Highlight Words or Bolding: Do NOT use markdown bolding (e.g. **words**) or highlight formatting. Keep the text clean, natural, and standard.\n"
        "5. Structure: Keep responses concise and well-structured (2-4 sentences or clean plain bullet points using '-' or '•').\n"
        "6. Accuracy: Ground all statements in Alok's actual skills, projects (TryThyEye, Numpy_ANN_Mnist, PhilGTP, MNIST_Diffusion, HGR_Temple_Run, Emotion_Det), and education.\n"
        "7. Contact & Resume: If asked about contacting Alok or viewing his resume, provide his email alokrtofc@gmail.com, GitHub, LinkedIn, or mention the resume link on the page."
    )
    
    payload = {
        "model": "open-mistral-7b",
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_message}
        ],
        "temperature": 0.2,
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
                    cleaned_reply = reply.replace("**", "").replace("⛩️", "").replace("🌸", "").replace("✨", "").strip()
                    return cleaned_reply
    except Exception:
        pass
        
    return get_fallback_answer(user_message)


def get_fallback_answer(user_message: str) -> str:
    msg = (user_message or "").lower().strip()
    if not msg:
        return "Hello. I am the portfolio assistant for Alok Ranjan Tripathy. How can I help you regarding his projects, technical skills, or background?"
    
    if any(k in msg for k in ["hi", "hello", "hey", "greetings", "who are you"]):
        return "Hello. I am Alok's portfolio assistant. I can provide details regarding his Computer Vision systems, Deep Learning models, Generative AI projects, and background at IIIT Bhubaneswar."
    
    if any(k in msg for k in ["project", "build", "trythyeye", "numpy", "philgtp", "diffusion", "temple run", "emotion"]):
        if "trythyeye" in msg or "sunglasses" in msg:
            return "TryThyEye is a real-time computer vision system built by Alok. It uses SAM (Segment Anything Model), YOLO, and MediaPipe to detect facial landmarks and segment sunglasses, allowing users to virtually try them on with realistic perspective warping and occlusion handling."
        if "numpy" in msg or "mnist" in msg or "scratch" in msg:
            return "Numpy_ANN_Mnist is a handwritten digit classification network Alok built from mathematical first principles in pure NumPy. It implements forward propagation, backpropagation, and stochastic gradient descent without using PyTorch or TensorFlow, achieving over 85% test accuracy on MNIST."
        if "philgtp" in msg or "rag" in msg or "philosophy" in msg:
            return "PhilGTP is a conversational dialogue engine Alok developed using LangChain and Mistral. It uses Retrieval-Augmented Generation (RAG) to ground answers directly in canonical philosophical texts, preventing hallucinations."
        if "diffusion" in msg or "ddpm" in msg:
            return "MNIST_Diffusion is a Denoising Diffusion Probabilistic Model (DDPM) Alok developed with a custom UNet architecture in PyTorch to synthesize handwritten digits iteratively from Gaussian noise."
        if "gesture" in msg or "temple run" in msg or "hgr" in msg:
            return "HGR_Temple_Run is a real-time hand gesture recognition system Alok created using OpenCV and MediaPipe to control game navigation purely through hand movements."
        if "emotion" in msg or "multimodal" in msg:
            return "Emotion_Det is a multimodal emotion perception pipeline Alok developed that combines facial landmark analysis, acoustic voice feature extraction, and NLP for nuanced social cue understanding."
        return "Alok has built several featured AI and machine learning projects, including TryThyEye (SAM and YOLO virtual try-on), Numpy_ANN_Mnist (from-scratch neural network), PhilGTP (RAG philosophical engine), MNIST_Diffusion (DDPM UNet), HGR_Temple_Run (gesture control), and Emotion_Det (multimodal AI)."
        
    if any(k in msg for k in ["skill", "stack", "tech", "languages", "python", "pytorch", "cv", "vision"]):
        return "Alok's technical stack includes:\n- Languages: Python, C, C++\n- Computer Vision: SAM (Segment Anything), YOLO, MediaPipe, OpenCV\n- Deep Learning: PyTorch, TensorFlow, scikit-learn, pure NumPy\n- GenAI and RAG: LangChain, LangGraph, Vector Stores\n- Tools: Git, Jupyter Notebook, Streamlit, Flask"

    if any(k in msg for k in ["study", "college", "iiit", "education", "bhubaneswar", "degree", "undergrad"]):
        return "Alok is pursuing his B.Tech in Computer Science and Engineering at IIIT Bhubaneswar (Expected Graduation: 2028). He also completed Tata iQ's virtual AI and Data Analytics job simulation via Forage in 2025."

    if any(k in msg for k in ["contact", "email", "hire", "github", "linkedin", "reach"]):
        return "You can reach Alok through:\n- Email: alokrtofc@gmail.com\n- GitHub: github.com/ArtExists\n- LinkedIn: linkedin.com/in/alok-ranjan-tripathy\nHe is open to engineering internships, research opportunities, and technical collaborations."

    if any(k in msg for k in ["resume", "cv", "pdf"]):
        return "You can view and download Alok's resume directly via the 'Resume' button in the navigation bar."

    return f"Regarding '{user_message}': Alok specializes in Computer Vision (SAM, YOLO), Generative AI (Diffusion, RAG), and Deep Learning at IIIT Bhubaneswar. Feel free to ask for specific details about his projects, skills, or contact information."


def query_neko_quip(context_type: str = "joke") -> str:
    raw_key = os.environ.get("MISTRAL_API_KEY", "")
    api_key = raw_key.strip().strip('"').strip("'")
    
    if not api_key:
        return get_neko_fallback(context_type)
        
    system_prompt = (
        "You are 'Neko', a witty, slightly sarcastic yet charming Japanese cyber-cat spirit roaming Alok Ranjan Tripathy's engineering portfolio.\n"
        "Keep your reply strictly to 1 or 2 short, humorous sentences with a light comedic tone.\n"
        "Make clever jokes about coding, AI, machine learning, or playfully comment on Alok's projects (TryThyEye sunglasses try-on, pure NumPy neural nets from scratch, PhilGTP RAG, DDPM diffusion, gesture control).\n"
        "Do NOT use emojis. Do NOT use markdown bold (**word**)."
    )
    
    user_prompt = f"Give a quick, witty, light comedic cat-spirit observation or one-liner about: {context_type}."
    
    payload = {
        "model": "open-mistral-7b",
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ],
        "temperature": 0.7,
        "max_tokens": 80
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
        with urllib.request.urlopen(req, timeout=5) as resp:
            if resp.status == 200:
                body = json.loads(resp.read().decode("utf-8"))
                reply = body["choices"][0]["message"]["content"]
                if reply and reply.strip():
                    cleaned = reply.replace("**", "").replace("⛩️", "").replace("🌸", "").replace("✨", "").strip().strip('"')
                    return cleaned
    except Exception:
        pass
        
    return get_neko_fallback(context_type)


def get_neko_fallback(context_type: str = "joke") -> str:
    import random
    ctx = (context_type or "").lower()
    
    if "trythyeye" in ctx or "sunglass" in ctx:
        return "TryThyEye lets you test sunglasses virtually. I tried it, but they still don't make aviators fitted for cat ears."
    if "numpy" in ctx or "math" in ctx or "scratch" in ctx:
        return "Alok built a neural net in pure NumPy with zero frameworks. My brain hurts just watching someone do manual matrix calculus."
    if "philgtp" in ctx or "rag" in ctx or "philosophy" in ctx:
        return "PhilGTP discusses philosophy using RAG. Finally, an AI that can debate whether the glass on the table was meant to be knocked over."
    if "diffusion" in ctx or "ddpm" in ctx:
        return "MNIST_Diffusion turns static noise into handwritten numbers. Pretty impressive, but can it generate a warm sunny spot on the floor?"
    if "gesture" in ctx or "temple" in ctx or "hgr" in ctx:
        return "HGR_Temple_Run translates hand gestures into game controls. Next feature request: translating tail flicks into keyboard shortcuts."
    if "chat" in ctx or "art" in ctx or "assistant" in ctx:
        return "If you need serious answers about Alok's resume, ask the portfolio assistant. I'm primarily here for the GPU warmth."
        
    jokes = [
        "Why do neural networks love cats? Because we both excel at purr-ceptron learning.",
        "There are 10 types of people in the world: those who understand binary, and cats who knock the bits off the table.",
        "Debugging is like playing with a laser pointer—you chase the red dot until your stack overflows.",
        "I tried backpropagation once. It just brought me back to my food bowl.",
        "Alok spends hours training models to reduce loss. Personally, I never lose.",
        "A GPU is just an expensive heating pad that occasionally renders tensors."
    ]
    return random.choice(jokes)


class PortfolioRequestHandler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        if self.path == "/api/chat":
            self.send_response(200)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.send_header("Access-Control-Allow-Origin", "*")
            self.end_headers()
            self.wfile.write(json.dumps({"status": "healthy", "service": "Portfolio Assistant & Neko API"}).encode("utf-8"))
        else:
            super().do_GET()

    def do_POST(self):
        if self.path == "/api/chat":
            try:
                content_length = int(self.headers.get("Content-Length", 0))
                post_data = self.rfile.read(content_length) if content_length > 0 else b"{}"
                data = json.loads(post_data.decode("utf-8")) if post_data else {}
                mode = data.get("mode", "chat")
                
                if mode == "neko":
                    topic = data.get("topic", "joke")
                    quip = query_neko_quip(topic)
                    response_data = {"reply": quip, "mode": "neko"}
                else:
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
