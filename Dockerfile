FROM python:3.12-alpine AS base
FROM base AS builder
RUN pip install py-cord[speed] python-dotenv pytz tortoise-orm --no-cache-dir


FROM base
# copy only the dependencies installation from the 1st stage image
COPY --from=builder /root/.local /root/.local
COPY . /app
WORKDIR /app

# update PATH environment variable
ENV PATH=/home/app/.local/bin:$PATH

CMD ["python", "-u", "main.py"]