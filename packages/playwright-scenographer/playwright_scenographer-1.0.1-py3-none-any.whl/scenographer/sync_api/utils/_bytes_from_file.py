from typing import Iterator


def bytes_from_file(filename: str, chunk_size: int = 8192) -> Iterator[int]:
    with open(filename, "rb") as f:
        while (chunk := f.read(chunk_size)):
            for b in chunk:
                yield b
