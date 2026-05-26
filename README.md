# 2ch.hk API Wrapper

A Python-based API wrapper for 2ch.hk (Dvach) designed with Clean Architecture principles and Domain-Driven Design (DDD).

## Features

- **Live Monitoring**: Use Async Iterators to track new posts in a thread or new threads on a board.
- **Clean Architecture**: Decoupled domain, application, and infrastructure layers.
- **Async First**: Built on `httpx` for high-performance asynchronous I/O.
- **HTML Stripping**: Automatically cleans up HTML tags from 2ch comments.

## Project Structure

- `src/dvach/domain`: Core entities (Post, Thread, Board) and repository interfaces.
- `src/dvach/application`: Business logic (ThreadWatcher, BoardWatcher).
- `src/dvach/infrastructure`: Implementation of the 2ch API client.
- `src/dvach/shared`: Utilities like HTML stripping.
- `src/main.py`: CLI entry point for monitoring.

## Installation

1. Create a virtual environment:
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## Usage

### CLI Monitoring

To monitor a thread in real-time:

```bash
export PYTHONPATH=src
python src/main.py <board> <thread_id>
```

Example:
```bash
python src/main.py b 12345678
```

### Programmatic Usage

```python
import asyncio
from dvach.infrastructure.client import DvachClient
from dvach.application.watcher import ThreadWatcher

async def monitor():
    client = DvachClient()
    watcher = ThreadWatcher(client, "b", 12345678, interval=10)
    
    async for post in watcher.watch():
        print(f"New post {post.id}: {post.comment}")

if __name__ == "__main__":
    asyncio.run(monitor())
```

## Testing

Run tests using `pytest`:

```bash
export PYTHONPATH=src
pytest tests/
```
