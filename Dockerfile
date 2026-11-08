# Alpine base: small attack surface and musllinux wheels for every pinned dependency.
FROM python:3.13-alpine

# Keep the base image packages patched
RUN apk upgrade --no-cache

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

# Run as a non-root user; /app must stay writable for db.sqlite3
RUN adduser -D -u 1000 app \
    && chown -R app:app /app
USER app

CMD ["python", "-u", "main.py"]
