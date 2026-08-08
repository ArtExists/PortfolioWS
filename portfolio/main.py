import http.server
import socketserver
import json
import os

PORT = 8000

def get_pretrained_bot_answer(user_message: str) -> str:
    """
    Intelligent chatbot engine for Ask_ART with knowledge of Alok Ranjan Tripathy's
    projects, skills, background, and vision/GenAI experience.
    """
    msg = (user_message or "").lower().strip()
    if not msg:
        return "ようこそ! I am Ask_ART, your spirit guide to Alok's portfolio. Ask me about projects, skills, CV models, or education! ⛩️"
    
    if any(k in msg for k in ["hi", "hello", "hey", "konnichiwa", "greetings", "who are you"]):
        return "Konnichiwa! ⛩️ I'm Ask_ART — Alok's portfolio assistant. I can tell you all about his Computer Vision systems, Deep Learning models, RAG chatbots, and research at IIIT Bhubaneswar!"
    
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
        return "🌸 Alok has built 6 standout AI/ML projects: **TryThyEye** (SAM+YOLO virtual try-on), **Numpy_ANN_Mnist** (from-scratch neural net), **PhilGTP** (LangChain RAG), **MNIST_Diffusion** (DDPM UNet), **HGR_Temple_Run** (Gesture Control), and **Emotion_Det** (Multimodal AI). Which one would you like to explore?"
        
    if any(k in msg for k in ["skill", "stack", "tech", "languages", "python", "pytorch", "cv", "vision"]):
        return "⚔️ **Alok's Tech Arsenal**:\n• **Languages**: Python, C, C++\n• **Computer Vision**: SAM, YOLO, MediaPipe, OpenCV\n• **Deep Learning**: PyTorch, TensorFlow, scikit-learn, NumPy\n• **GenAI & RAG**: LangChain, LangGraph, Vector Stores\n• **Tools**: Git, Jupyter, Streamlit, Flask"

    if any(k in msg for k in ["study", "college", "iiit", "education", "bhubaneswar", "degree", "undergrad"]):
        return "🎓 Alok is pursuing his B.Tech in **Computer Science & Engineering at IIIT Bhubaneswar** (Expected 2028). He also completed Tata iQ's virtual AI & Data Analytics program via Forage in 2025!"

    if any(k in msg for k in ["contact", "email", "hire", "github", "linkedin", "reach"]):
        return "✉️ You can reach Alok via:\n• **Email**: alokrtofc@gmail.com\n• **GitHub**: github.com/ArtExists\n• **LinkedIn**: linkedin.com/in/alok-ranjan-tripathy\nHe's open to collaborations, research, and internship opportunities!"

    if any(k in msg for k in ["resume", "cv", "pdf"]):
        return "📄 You can view and download Alok's official resume (`ART_Resume-2.pdf`) directly using the 'Download Resume' button in the navigation bar!"

    return f"✨ Ask_ART received: '{user_message}'. Alok specializes in Computer Vision (SAM, YOLO), Generative AI (Diffusion, RAG), and Deep Learning at IIIT Bhubaneswar. Feel free to ask about his projects, skills, or contact info!"

class PortfolioRequestHandler(http.server.SimpleHTTPRequestHandler):
    def do_POST(self):
        if self.path == "/api/chat":
            content_length = int(self.headers.get("Content-Length", 0))
            post_data = self.rfile.read(content_length)
            
            try:
                data = json.loads(post_data.decode("utf-8")) if post_data else {}
                user_msg = data.get("message", "")
                
                # Call the pretrained bot handler function
                bot_reply = get_pretrained_bot_answer(user_msg)
                response_data = {"reply": bot_reply}
                
                self.send_response(200)
                self.send_header("Content-Type", "application/json")
                self.send_header("Access-Control-Allow-Origin", "*")
                self.end_headers()
                self.wfile.write(json.dumps(response_data).encode("utf-8"))
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
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.end_headers()

if __name__ == "__main__":
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    socketserver.TCPServer.allow_reuse_address = True
    with socketserver.TCPServer(("", PORT), PortfolioRequestHandler) as httpd:
        print(f"Portfolio Server running at http://localhost:{PORT}")
        print(f"Chat API Endpoint: http://localhost:{PORT}/api/chat")
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\nShutting down server.")
