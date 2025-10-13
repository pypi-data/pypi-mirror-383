from typing import AsyncIterator

import aiofiles


async def bytes_from_file(filename: str,
                          chunk_size: int = 8192) -> AsyncIterator[int]:
    async with aiofiles.open(filename, 'rb') as f:
        while (chunk := await f.read(chunk_size)):
            for b in chunk:
                yield b
