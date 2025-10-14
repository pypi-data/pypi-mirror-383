# 🧠 NeuraPython — Unified AI, Science & Assembly Framework

**Author:** Ibrahim Shahid  
**Version:** 1.2.3  
**License:** MIT  

---

## 📘 Overview

**NeuraPython** is a next-generation, unified Python framework designed to bridge **Artificial Intelligence**, **Machine Learning**, **Scientific Computation**, and even **Assembly-level execution** — all inside one cohesive ecosystem.

It simplifies development for **AI engineers, data scientists, educators, physicists, and automation enthusiasts** by combining advanced computation, system control, and AI capabilities under one intuitive API.

---

## 🚀 Key Highlights

| Category | Description |
|-----------|-------------|
| 🧠 **Artificial Intelligence** | Direct integration with **Google Gemini** and **OpenAI ChatGPT** APIs for text and reasoning tasks. |
| 🤖 **Machine Learning** | Unified **Scikit-Learn** wrapper for dataset loading, preprocessing, model training, evaluation, and persistence. |
| 🧩 **Neural Networks** | Supports both **PyTorch** and **TensorFlow** backends with a shared universal interface. |
| 🧮 **Mathematics & Calculus** | Symbolic and numeric mathematics: differentiation, integration, gradients, Jacobians, Hessians, and more. |
| ⚛️ **Physics Engine** | Covers mechanics, relativity, electricity, magnetism, and quantum physics (including Heisenberg uncertainty). |
| ⚗️ **Chemistry Tools** | Built-in **periodic table**, molecular data, and atomic constants for chemical computations. |
| 🗄️ **Databases** | Simplified **SQLite** manager with auto-schema creation, insertion, and query utilities. |
| 🌐 **Web Development** | Built-in **Flask server** for APIs, websites, and JSON endpoints. Includes error handling and file upload endpoints. |
| 🔊 **Speech & Audio** | Text-to-speech and voice recognition utilities for interactive AI apps. |
| 📊 **Visualization** | Generate 2D, 3D, and polar plots using Matplotlib with minimal code. |
| 🧩 **Assembly Language Support** | Built-in **Assembly interpreter and hardware-level utilities** for advanced system control and code execution. |
| 🧾 **Converters** | Seamless conversion between PDF, DOCX, TXT, Excel, CSV, JSON, and Markdown/HTML. |
| 🧱 **Vectors & Matrices** | Advanced matrix algebra and vector calculus engine. |
| 🧮 **Advanced Maths** | Arithmetic, statistics, combinatorics, sequences, and probability utilities. |
| 🖼️ **Media Handling** | Display images, play audio/video, and process multimedia via OpenCV and Pygame. |
| 🧾 **Readers** | Universal file readers for PDF, DOCX, JSON, XML, CSV, and more. |
| 🔐 **QR Codes** | Create and decode QR codes effortlessly. |
| 🗓️ **Calendar** | Print system calendar data instantly via Python. |
**Sensors** | Contain multiple functions to sense different things like    temperature ,  motion
|
**Web Scrapping**| class **WebScrapper()** used for web scrapping
|
---

## 🧩 Installation

> Requires **Python 3.9+**

Install from PyPI:
```bash
pip install neurapython
```

Upgrade if already installed:
```bash
pip install --upgrade neurapython
```

Then import:
```python
from neurapython import *
```

---

## ⚙️ Quick Examples

### 🤖 Machine Learning
```python
ml = NeuraPython_ML()
X, y = ml.load_builtin_dataset("iris")
X_train, X_test, y_train, y_test = ml.split(X, y)

ml.create_model("random_forest")
ml.train("random_forest", X_train, y_train)
pred = ml.predict("random_forest", X_test)
print(ml.evaluate(y_test, pred))
```

### 🧠 Neural Network
```python
nn = NeuralNetwork(backend='torch')
nn.Sequential([4, 8, 3])
nn.compile()
nn.fit([[0.1, 0.2, 0.3, 0.4]], [[1, 0, 0]], epochs=3)
```

### ⚛️ Physics
```python
phy = Physics()
print(phy.mass_energy_equivalence(0.001))  # E = mc²
```

### ⚗️ Chemistry
```python
chem = Chemistry()
print(chem._elements[0])  # Hydrogen info
```

### 💾 Database
```python
db = Database()
db.create("data.db", "Users", [
    {"name": "ID", "datatype": "INTEGER"},
    {"name": "Name", "datatype": "TEXT"}
])
db.insert_data("data.db", "Users", {"ID": [1], "Name": ["Ibrahim"]})
```

### 🧮 Calculus
```python
calc = Calculus()
print(calc.derivative("x**2 + 3*x", "x"))
```

### 🧩 Assembly Support
```python
from neurapython import Assembly

asm = Assembly()
asm.load_code("""
MOV AX, 5
MOV BX, 10
ADD AX, BX
OUT AX
""")
asm.run()
```

### 🔈 Speech & Voice
```python
speak("Welcome to NeuraPython!")
text = voice_input("Say something:")
print("You said:", text)
```

### 🌐 Web Server
```python
server = WebServer()
server.simple_route("/", code="Welcome to NeuraPython Web API!")
server.run()
```

### 📊 Visualization
```python
viz = Visualizer2D(["A", "B", "C"], [5, 10, 15], title="Bar Graph Example")
viz.bar_graph()
viz.show()
```

---

## 🧱 Module Structure

```
neurapython/
│
├── AI                   # GPT / Gemini integration
├── Assembly             # Assembly language interpreter & hardware control
├── Advanced_Maths       # Algebra, statistics, probability
├── Calculus             # Derivatives, limits, Jacobians, etc.
├── Chemistry            # Periodic table and constants
├── Converter            # File conversions
├── Database             # SQLite wrapper
├── Media                # Image, audio, video
├── Matrices, Vectors    # Linear algebra utilities
├── NeuraPython_ML       # Unified ML wrapper
├── NeuralNetwork        # TensorFlow / PyTorch backend
├── Physics              # Classical, relativistic, quantum
├── Reader               # File readers
├── Visualizer2D / 3D    # Graph plotting
└── WebServer            # Flask API/web server
```

---

## 🧠 Author

**Ibrahim Shahid**  
📧 Email: *ibrahimshahid7767@gmail.com*  

---

## ⚖️ License

This project is licensed under the **MIT License**.  
You are free to use, modify, and distribute with proper credit.

---

## 💬 Credits

Developed with ❤️ by **Ibrahim Shahid**  
Powered by: TensorFlow · PyTorch · Flask · Scikit-learn · SymPy · Pandas · NumPy · OpenCV · Matplotlib · Pygame · FPDF and more.

---
