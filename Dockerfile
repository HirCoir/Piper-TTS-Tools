# Utiliza una imagen base de Alpine Linux con Python 3.12
FROM python:3.12-alpine

# Define la token de Hugging Face como un argumento de compilación
ARG TOKEN_HUGGINGFACE={$REPO_HUGGINGFACE}

ARG REPO_HUGGINGFACE={REPO_HUGGINGFACE}

# Define la URL base de descarga
ENV DOWNLOAD_URL_BASE=https://github.com/rhasspy/piper/releases/download/2023.11.14-2/

# Instala el cliente de Hugging Face y las dependencias necesarias
RUN apk add --no-cache --virtual .build-deps gcc musl-dev curl && \
    pip install --upgrade pip && \
    pip install flask -U "huggingface_hub[cli]" && \
    apk del .build-deps

# Comprueba si TOKEN_HUGGINGFACE tiene un valor antes de ejecutar la línea RUN
RUN if [ -z "$TOKEN_HUGGINGFACE" ]; then \
        echo "No hubo TOKEN_HUGGINGFACE, no se guarda."; \
    else \
        echo "Se ha guardado el TOKEN."; \
        mkdir -p /root/.cache/huggingface/; \
        echo $TOKEN_HUGGINGFACE > /root/.cache/huggingface/token; \
    fi

# Crea el usuario de la aplicación y establece el espacio de trabajo
RUN adduser -D -u 1000 app

WORKDIR /home/app

RUN mkdir temp_audio

# Descarga y extrae los binarios de Piper
RUN case "$(uname -m)" in \
        x86_64) DOWNLOAD_URL=${DOWNLOAD_URL_BASE}piper_linux_x86_64.tar.gz ;; \
        armv7l) DOWNLOAD_URL=${DOWNLOAD_URL_BASE}piper_linux_armv7l.tar.gz ;; \
        aarch64) DOWNLOAD_URL=${DOWNLOAD_URL_BASE}piper_linux_aarch64.tar.gz ;; \
        *) echo "Arquitectura no compatible: $(uname -m)"; exit 1 ;; \
    esac && \
    curl -SL ${DOWNLOAD_URL} | tar -xzC ./ 

# Copia el código de la aplicación
COPY --chown=app:app . .

# Comprueba si REPO_HUGGINGFACE tiene un valor antes de ejecutar la línea RUN
RUN if [ -z "$REPO_HUGGINGFACE" ]; then \
        echo "No hubo REPO_HUGGINGFACE, no se realiza la descarga."; \
    else \
        mkdir -p /home/app/models && \
        cd /home/app/models && \
        huggingface-cli download $REPO_HUGGINGFACE --local-dir /home/app/models; \
    fi

# Expone el puerto y cambia de nuevo al usuario de la aplicación
EXPOSE 7860

USER app

# Comando para iniciar la aplicación
CMD ["python3", "app.py"]
