cd "$(dirname "$0")"
cd ../examples/granian
uv run --with granian granian main:app --interface asgi --host 127.0.0.1 --port 8003