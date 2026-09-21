# angstromCTF 2021 - Jar
FROM python:3.11-slim

WORKDIR /srv
RUN pip install --no-cache-dir Flask==2.3.3

COPY jar.py pickle.jpg ./

# FLAG is kept non-plaintext in the distributed Dockerfile.
ENV FLAG_B64=RkxBR3tUMzRNX1JPT0tJRV9KQVJfUElDS0xFfQ==

EXPOSE 5000
USER nobody

CMD ["sh", "-c", "export FLAG=$(python -c 'import base64,os;print(base64.b64decode(os.environ[\"FLAG_B64\"]).decode())'); exec python jar.py"]
