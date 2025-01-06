# fastapi-web Project

This project is a web application built using FastAPI. It serves dynamic HTML pages and static files, providing a responsive and interactive user experience.

## Project Structure

```
fastapi-web
├── src
│   ├── static
│   │   ├── css
│   │   │   └── style.css
│   │   └── js
│   │       └── main.js
│   ├── templates
│   │   ├── base.html
│   │   └── index.html
│   └── main.py
├── requirements.txt
└── README.md
```

## Setup Instructions

1. **Clone the repository:**
   ```bash
   git clone <repository-url>
   cd fastapi-web
   ```

2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Run the application:**
   ```bash
   uvicorn src.main:app --reload
   ```

4. **Access the application:**
   Open your browser and go to `http://127.0.0.1:8000`.

## Features

- Dynamic HTML rendering using FastAPI.
- Responsive design with CSS.
- Interactive elements powered by JavaScript.

## License

This project is licensed under the MIT License.