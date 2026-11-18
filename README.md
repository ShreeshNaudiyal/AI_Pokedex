# 🧠 AI Pokédex

> An AI-powered Pokédex that identifies Pokémon from images using Deep Learning and displays detailed Pokémon information through an interactive web interface built with Spring Boot.


## 📖 Overview

AI Pokédex is a full-stack application that leverages **Deep Learning** to recognize Pokémon from uploaded images. Once a Pokémon is identified, the application retrieves comprehensive information such as its type, abilities, stats, and sprite using the **PokeAPI**.

The project combines **Machine Learning**, **Java Spring Boot**, and **modern web technologies** to provide an intelligent and interactive Pokédex experience.

---

## ✨ Features

- 🤖 AI-powered Pokémon image recognition
- 📷 Upload Pokémon images for prediction
- ⚡ Fast REST API built with Spring Boot
- 🎯 ONNX model inference using Deep Java Library (DJL)
- 🌐 Fetch real-time Pokémon data from PokeAPI
- 📱 Responsive and user-friendly frontend
- 🚀 High-performance caching support
- 🧩 Modular project architecture
- ✅ Easy deployment and scalability

---

## 🛠 Tech Stack

### Backend
- Java 21
- Spring Boot 3
- Spring Web
- Spring WebFlux
- Maven
- Caffeine Cache
- Deep Java Library (DJL)

### Frontend
- HTML5
- CSS3
- JavaScript (ES6)

### Machine Learning
- TensorFlow
- Keras
- OpenCV
- NumPy
- Pandas
- Scikit-learn
- ONNX
- ONNX Runtime

### External API
- PokeAPI

---

# 📂 Project Structure

```text
AI_Pokedex
│
├── backend/                # Spring Boot REST API
│   ├── src/
│   ├── models/
│   └── pom.xml
│
├── frontend/               # Web Interface
│   ├── css/
│   ├── js/
│   ├── images/
│   └── index.html
│
├── ml_training/            # TensorFlow Model Training
│   ├── dataset/
│   ├── train.py
│   ├── train.sh
│   └── requirements.txt
│
├── .github/
└── README.md
```

---

# 🏗 System Architecture

```text
                    User Uploads Image
                            │
                            ▼
                  Frontend (HTML/CSS/JS)
                            │
                            ▼
                 Spring Boot REST Backend
                            │
                            ▼
             AI Model (TensorFlow / ONNX)
                            │
                            ▼
               Predicted Pokémon Name
                            │
                            ▼
               Fetch Data from PokeAPI
                            │
                            ▼
           Display Pokémon Information
```

---

# 🚀 Getting Started

## Prerequisites

- Java 21
- Maven
- Python 3.10+
- Git

---

## Clone the Repository

```bash
git clone https://github.com/ShreeshNaudiyal/AI_Pokedex.git
cd AI_Pokedex
```

---

## Backend Setup

Navigate to the backend directory:

```bash
cd backend
```

Run the Spring Boot application:

```bash
mvn spring-boot:run
```

---

## Frontend Setup

The frontend is packaged into the Spring Boot backend and served automatically at:
```
http://localhost:8080/
```

Alternatively, you can open `frontend/index.html` using **VS Code Live Server** or any static file server; the client automatically connects to the backend on `http://localhost:8080/api`.

---

## Machine Learning Setup

Navigate to the ML directory:

```bash
cd ml_training
```

Install dependencies:

```bash
pip install -r requirements.txt
```

Train / export the full 721-class ONNX model:

```powershell
python src/build_full_model.py
```

---

## 🔌 REST API Endpoints

| Method | Endpoint | Description |
|---------|----------|-------------|
| POST | `/api/identify` | Predict Pokémon from uploaded image (`multipart/form-data`, key: `image`) |
| GET | `/api/health` | Health check endpoint (returns `"OK"`) |
| GET | `/` | Web interface (served directly by Spring Boot) |

---

# 🤖 Machine Learning Pipeline

1. Collect Pokémon image dataset
2. Perform image preprocessing
3. Apply data augmentation
4. Train TensorFlow/Keras model
5. Evaluate model performance
6. Export trained model to ONNX
7. Load ONNX model in Java using DJL
8. Perform inference through Spring Boot API

---

---

# 🎯 Future Enhancements

- 📱 Mobile application
- 🎥 Webcam-based Pokémon recognition
- 🎮 Pokémon battle simulator
- ❤️ Favorite Pokémon collection
- 👤 User authentication
- 📊 Prediction confidence visualization
- ☁ Cloud deployment
- 🐳 Docker support

---

# 📊 Project Highlights

- Full-stack AI application
- Java + Spring Boot backend
- TensorFlow deep learning model
- ONNX deployment
- DJL inference engine
- RESTful architecture
- Responsive frontend
- External API integration

---

# 🤝 Contributing

Contributions are welcome!

1. Fork the repository

2. Create a feature branch

```bash
git checkout -b feature-name
```

3. Commit your changes

```bash
git commit -m "Add new feature"
```

4. Push to your branch

```bash
git push origin feature-name
```

5. Open a Pull Request

---

# 🙏 Acknowledgements

- **PokeAPI** for Pokémon data
- **TensorFlow** for deep learning
- **Spring Boot** for backend development
- **Deep Java Library (DJL)** for Java inference
- **ONNX Runtime** for optimized model execution

---

---

## ⭐ If you like this project

Please consider giving it a **Star ⭐** on GitHub. It helps others discover the project and motivates further development.

---
