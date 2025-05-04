FROM python:3.12-slim

# Instala dependências do sistema
RUN apt-get update && apt-get install -y \
    chromium \
    chromium-driver \
    xvfb \
    libnss3 \
    libgbm1 \
    python3-pip \
    nginx \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Cria diretório para screenshots
RUN mkdir -p /app/debug_screenshots && \
    chmod 777 /app/debug_screenshots

# Configura nginx para servir os screenshots com uma página mais bonita
RUN echo '<!DOCTYPE html>\n\
<html>\n\
<head>\n\
    <title>Debug Screenshots</title>\n\
    <style>\n\
        body { font-family: Arial, sans-serif; margin: 20px; }\n\
        .file { margin: 10px 0; padding: 10px; border: 1px solid #ddd; }\n\
        .screenshot { max-width: 100%; margin: 10px 0; }\n\
        .html-content { max-height: 300px; overflow: auto; }\n\
    </style>\n\
</head>\n\
<body>\n\
    <h1>Debug Screenshots e HTML</h1>\n\
    <div id="files"></div>\n\
    <script>\n\
        fetch("/")\n\
            .then(response => response.text())\n\
            .then(html => {\n\
                const parser = new DOMParser();\n\
                const doc = parser.parseFromString(html, "text/html");\n\
                const files = Array.from(doc.querySelectorAll("a"))\n\
                    .map(a => a.href)\n\
                    .filter(href => href.endsWith(".png") || href.endsWith(".html"));\n\
                \n\
                const container = document.getElementById("files");\n\
                const groups = {};\n\
                \n\
                files.forEach(file => {\n\
                    const name = file.split("/").pop().split(".")[0];\n\
                    if (!groups[name]) groups[name] = {};\n\
                    if (file.endsWith(".png")) groups[name].png = file;\n\
                    if (file.endsWith(".html")) groups[name].html = file;\n\
                });\n\
                \n\
                Object.entries(groups).forEach(([name, files]) => {\n\
                    const div = document.createElement("div");\n\
                    div.className = "file";\n\
                    div.innerHTML = `\n\
                        <h2>${name}</h2>\n\
                        ${files.png ? `<img src="${files.png}" class="screenshot"/>` : ""}\n\
                        ${files.html ? `<iframe src="${files.html}" class="html-content"></iframe>` : ""}\n\
                    `;\n\
                    container.appendChild(div);\n\
                });\n\
            });\n\
    </script>\n\
</body>\n\
</html>' > /app/debug_screenshots/index.html

# Configura nginx
RUN echo 'server { \
    listen 8080; \
    root /app/debug_screenshots; \
    index index.html; \
    location / { \
        autoindex on; \
        try_files $uri $uri/ =404; \
    } \
}' > /etc/nginx/sites-available/default

# Copia os arquivos
COPY . .

# Atualiza pip e instala setuptools primeiro
RUN pip install --no-cache-dir --upgrade pip setuptools

# Instala dependências Python
RUN pip install --no-cache-dir -r requirements.txt

# Configura variáveis de ambiente
ENV DISPLAY=:99
ENV PYTHONUNBUFFERED=1

# Expõe as portas
EXPOSE 3090
EXPOSE 8080

# Comando para iniciar
CMD ["bash", "-c", "service nginx start && Xvfb :99 -screen 0 1920x1080x24 & sleep 2 && python api.py"]