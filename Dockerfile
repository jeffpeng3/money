# Alpine base: small attack surface and musllinux wheels for every pinned dependency.
FROM python:3.13-alpine

# Keep the base image packages patched
RUN apk upgrade --no-cache \
    && apk add --no-cache su-exec

# Set the working directory in the container
WORKDIR /app

# Install pinned dependencies
COPY requirements.lock requirements.lock
RUN python -m pip install --no-cache-dir --upgrade pip \
    && python -m pip install --no-cache-dir -r requirements.lock \
    && rm -f /usr/local/lib/python3.*/site-packages/pip/_vendor/bom.cdx.json \
             /usr/local/lib/python3.*/site-packages/pip/_vendor/vendor.txt

# Copy the application code
COPY main.py orm.py ./

# Entrypoint fixes db ownership on mounted volumes, then drops to the app user.
COPY docker-entrypoint.sh /usr/local/bin/docker-entrypoint.sh
RUN chmod +x /usr/local/bin/docker-entrypoint.sh \
    && adduser -D -u 1000 app \
    && chown -R app:app /app

ENTRYPOINT ["docker-entrypoint.sh"]
CMD ["python", "-u", "main.py"]
