FROM python:3.10

# Define the Hugging Face token as a build argument
#ARG TOKEN_HUGGINGFACE=${TOKEN_HUGGINGFACE}
ARG TOKEN_HUGGINGFACE={$REPO_HUGGINGFACE}
ARG REPO_HUGGINGFACE={REPO_HUGGINGFACE}
# Define the base download URL
ENV DOWNLOAD_URL_BASE=https://github.com/rhasspy/piper/releases/download/2023.11.14-2/

# Instala el cliente de Hugging Face
RUN pip install --upgrade pip \
    && pip install flask -U "huggingface_hub[cli]"

# Comprueba si TOKEN_HUGGINGFACE tiene un valor antes de ejecutar la línea RUN
RUN if [ -z "$TOKEN_HUGGINGFACE" ]; then \
    echo "No hubo TOKEN_HUGGINGFACE, no se guarda."; \
else \
    echo "Se ha guardado el TOKEN."; \
    mkdir /root/.cache; mkdir /root/.cache/huggingface/; \
    echo $TOKEN_HUGGINGFACE > /root/.cache/huggingface/token; \
fi

# Create the application user and set the workspace
RUN useradd -m -u 1000 app
WORKDIR /home/app
RUN mkdir temp_audio
# Download and extract Piper binaries
RUN dpkgArch="$(dpkg --print-architecture)" && \
    case "${dpkgArch##*-}" in \
        amd64) DOWNLOAD_URL=${DOWNLOAD_URL_BASE}piper_linux_x86_64.tar.gz ;; \
        armhf) DOWNLOAD_URL=${DOWNLOAD_URL_BASE}piper_linux_armv7l.tar.gz ;; \
        arm64) DOWNLOAD_URL=${DOWNLOAD_URL_BASE}piper_linux_aarch64.tar.gz ;; \
        *) echo "Unsupported architecture: ${dpkgArch}"; exit 1 ;; \
    esac && \
    curl -SL ${DOWNLOAD_URL} | tar -xzC ./

# Copy the app code
COPY --chown=app:app . .

# Define the Hugging Face repo
#ARG REPO_HUGGINGFACE=${REPO_HUGGINGFACE}

# Comprueba si REPO_HUGGINGFACE tiene un valor antes de ejecutar la línea RUN
RUN if [ -z "$REPO_HUGGINGFACE" ]; then \
    echo "No hubo REPO_HUGGINGFACE, no se realiza la descarga."; \
else \
    mkdir /home/app/models && cd /home/app/models; huggingface-cli download $REPO_HUGGINGFACE --local-dir /home/app/models; \
fi
RUN mkdir /home/app/models; cd /home/app/models; wget https://huggingface.co/spaces/HirCoir/Piper-TTS-Spanish/resolve/main/es_MX-claude-14947-epoch-high.onnx; wget https://huggingface.co/spaces/HirCoir/Piper-TTS-Spanish/resolve/main/es_MX-claude-14947-epoch-high.onnx.json
# Expose the port and switch back to the application user
EXPOSE 7860
USER root
CMD ["python3", "app.py"]
