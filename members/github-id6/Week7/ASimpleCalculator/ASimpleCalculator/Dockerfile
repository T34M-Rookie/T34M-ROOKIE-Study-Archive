# UMDCTF 2022 - A Simple Calculator
FROM python:3.9-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . /app

ENV FLAG_B64=RkxBR3tUMzRNX1JPT0tJRV9TSU1QTEVfQ0FMQ1VMQVRPUn0=

# Replace only the challenge flag while preserving the original filter/eval logic.
RUN python - <<'PY'
import base64, os, pathlib, re
p = pathlib.Path("/app/secrets.py")
s = p.read_text()
flag = base64.b64decode(os.environ["FLAG_B64"]).decode()
s = re.sub(r"^FLAG\s*=.*$", f"FLAG = {flag!r}", s, flags=re.M)
p.write_text(s)
PY

EXPOSE 5000
CMD ["python", "app.py"]
