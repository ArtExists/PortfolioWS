import http.server
import socketserver
import json
import os
import dotenv
import pypdf

# Load API keys from local .env
ENV_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), ".env")
dotenv.load_dotenv(ENV_PATH)

PORT = 8000
RESUME_PDF_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "ART_Resume-2.pdf")



RESUME_TEXT = ""
try:
    if os.path.exists(RESUME_PDF_PATH):
        reader = pypdf.PdfReader(RESUME_PDF_PATH)
        extracted_pages = []
        for i, page in enumerate(reader.pages):
            page_text = page.extract_text()
            if page_text:
                extracted_pages.append(f"--- PAGE {i+1} ---\n{page_text.strip()}")
        RESUME_TEXT = "\n\n".join(extracted_pages)
        print(f"[Resume Loader] Successfully extracted {len(RESUME_TEXT)} characters from ART_Resume-2.pdf")
    else:
        print(f"[Resume Loader Warning] PDF not found at {RESUME_PDF_PATH}")
except Exception as e:
    print(f"[Resume Loader Error] Could not read PDF: {e}")

# ----------------------------------------------------
# 2. INITIALIZE LANGCHAIN WITH FREE MISTRAL AI MODEL
# ----------------------------------------------------
mistral_chain = None
raw_key = os.getenv("MISTRAL_API_KEY", "")
api_key = raw_key.strip().strip('"').strip("'") if raw_key else ""

if api_key:
    try:
        from langchain_mistralai import ChatMistralAI
        from langchain_core.prompts import ChatPromptTemplate
        from langchain_core.output_parsers import StrOutputParser

        # Use free Mistral model: open-mistral-7b (Mistral 7B)
        llm = ChatMistralAI(
            model="open-mistral-7b",
            mistral_api_key=api_key,
            temperature=0.3,
            max_retries=2,
            timeout=15
        )

        system_instructions = (
            "You are 'Ask_ART', an intelligent, polite, and charismatic AI spirit guide and portfolio companion "
            "for Alok Ranjan Tripathy (a Computer Science & Engineering undergraduate at IIIT Bhubaneswar).\n\n"
            "Your mission: Answer questions from visitors, recruiters, and engineers about Alok's technical background, "
            "engineering projects, skills, education, and achievements by fetching facts strictly from his official resume below.\n\n"
            "=== ALOK'S OFFICIAL RESUME CONTEXT (ART_Resume-2.pdf) ===\n"
            f"{RESUME_TEXT}\n"
            "=========================================================\n\n"
            "PORTFOLIO HIGHLIGHTS SUMMARY:\n"
            "• TryThyEye: Real-time virtual sunglasses segmenter using SAM (Segment Anything) and YOLO with perspective warping\n"
            "• Numpy_ANN_Mnist: Pure mathematical neural network built from scratch in NumPy with SGD & backprop (85%+ accuracy)\n"
            "• PhilGTP: Philosophical conversational RAG system grounding responses in classic philosopher PDFs via LangChain\n"
            "• MNIST_Diffusion: Denoising Diffusion Probabilistic Model (DDPM) UNet for image synthesis from noise\n"
            "• HGR_Temple_Run: Real-time hand gesture recognition system interfacing OpenCV & MediaPipe for game navigation\n"
            "• Emotion_Det: Unified multimodal perception pipeline combining facial landmarks, audio features, and NLP\n"
            "• Education: B.Tech in Computer Science & Engineering at IIIT Bhubaneswar (Graduation: 2028)\n"
            "• Contact: alokrtofc@gmail.com | github.com/ArtExists | linkedin.com/in/alok-ranjan-tripathy\n\n"
            "RESPONSE GUIDELINES:\n"
            "1. Be direct, concise, and structured (2 to 4 sentences or punchy bullet points).\n"
            "2. Maintain a subtle, tasteful Japanese aesthetic spirit (e.g., occasional 'ようこそ (Welcome)', 'Konnichiwa', '⛩️', '🌸', '✨').\n"
            "3. Ground all answers accurately in Alok's resume context.\n"
            "4. If asked about downloading his resume or reaching out, mention his email (alokrtofc@gmail.com) and the 'Download Resume' button."
        )

        prompt = ChatPromptTemplate.from_messages([
            ("system", system_instructions),
            ("human", "{question}")
        ])

        mistral_chain = prompt | llm | StrOutputParser()
        print(f"[LangChain] Initialized Mistral AI with model 'open-mistral-7b' (Key: {api_key[:6]}...{api_key[-4:]})")
    except Exception as e:
        print(f"[LangChain Error] Could not initialize ChatMistralAI: {e}")
else:
    print("[LangChain Warning] No MISTRAL_API_KEY found in .env; will use built-in knowledge base.")

# ----------------------------------------------------
# 3. RULE-BASED FALLBACK KNOWLEDGE BASE (ZERO DOWNTIME)
# ----------------------------------------------------
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

# ----------------------------------------------------
# 4. CHAT QUERY DISPATCHER (LANGCHAIN MISTRAL + FALLBACK)
# ----------------------------------------------------
def generate_chat_response(user_message: str) -> str:
    user_msg = (user_message or "").strip()
    if not user_msg:
        return "ようこそ! I am Ask_ART. Ask me anything about Alok's resume, AI projects, or engineering skills! ⛩️"

    if mistral_chain is not None:
        try:
            print(f"[Mistral Query] Prompting LangChain Mistral for: '{user_msg}'")
            response = mistral_chain.invoke({"question": user_msg})
            if response and response.strip():
                return response.strip()
        except Exception as e:
            print(f"[Mistral API Error] Falling back to knowledge base: {e}")

    # Fallback to smart knowledge base if offline or API error
    return get_fallback_answer(user_msg)

# ----------------------------------------------------
# 5. HTTP SERVER & REST API HANDLER
# ----------------------------------------------------
class PortfolioRequestHandler(http.server.SimpleHTTPRequestHandler):
    def do_POST(self):
        if self.path == "/api/chat":
            content_length = int(self.headers.get("Content-Length", 0))
            post_data = self.rfile.read(content_length)
            
            try:
                data = json.loads(post_data.decode("utf-8")) if post_data else {}
                user_msg = data.get("message", "")
                
                # Fetch answer via LangChain Mistral AI + Resume Context
                bot_reply = generate_chat_response(user_msg)
                response_data = {"reply": bot_reply}
                
                self.send_response(200)
                self.send_header("Content-Type", "application/json; charset=utf-8")
                self.send_header("Access-Control-Allow-Origin", "*")
                self.end_headers()
                self.wfile.write(json.dumps(response_data, ensure_ascii=False).encode("utf-8"))
            except Exception as e:
                self.send_response(500)
                self.send_header("Content-Type", "application/json")
                self.end_headers()
                self.wfile.write(json.dumps({"error": str(e)}).encode("utf-8"))
        else:
            self.send_error(404, "Endpoint Not Found")

    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "POST, GET, OPTIONS")
# Vercel Serverless Function Entrypoint Exports
handler = PortfolioRequestHandler
app = PortfolioRequestHandler
application = PortfolioRequestHandler

if __name__ == "__main__":
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    socketserver.TCPServer.allow_reuse_address = True
    with socketserver.TCPServer(("", PORT), PortfolioRequestHandler) as httpd:
        print(f"Portfolio Server running at http://localhost:{PORT}")
        print(f"Chat API Endpoint: http://localhost:{PORT}/api/chat (LangChain Mistral Powered)")
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\nShutting down server.")
