cd "$(dirname "$0")"
cd ../examples/daphne
uv run --with daphne daphne main:app -b 127.0.0.1 -p 8002