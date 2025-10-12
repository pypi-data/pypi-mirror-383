cd "$(dirname "$0")"
cd ../examples/uvicorn
uv run --with uvicorn uvicorn main:app --host 127.0.0.1 --port 8001