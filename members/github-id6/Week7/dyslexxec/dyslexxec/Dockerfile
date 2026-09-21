# DownUnderCTF 2022 - dyslexxec
FROM python:3.9-slim

WORKDIR /code
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . /code
RUN mkdir -p /code/uploads

ENV FLAG_B64=RkxBR3tUMzRNX1JPT0tJRV9EWVNMRVhYRUN9

# Original challenge stores the flag as an /etc/passwd username for XXE disclosure.
RUN FLAG="$(printf '%s' "$FLAG_B64" | base64 -d)" && \
    printf '%s:x:1001:1001::/tmp:/bin/false\n' "$FLAG" >> /etc/passwd

EXPOSE 1337
CMD ["python", "-m", "flask", "--app", "app", "run", "--host=0.0.0.0", "--port=1337"]
