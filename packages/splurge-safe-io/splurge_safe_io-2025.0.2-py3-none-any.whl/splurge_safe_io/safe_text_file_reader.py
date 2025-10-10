"""Safe text file reader utilities.

This module implements :class:`SafeTextFileReader`, a small helper that reads
text files in binary mode and performs deterministic newline normalization.
It intentionally decodes bytes explicitly to avoid platform newline
translation side-effects and centralizes encoding error handling into a
package-specific exception type.

Public API summary:
        - SafeTextFileReader: Read, preview, and stream text files with normalized
            newlines and optional header/footer skipping.
        - open_text: Context manager returning an in-memory text stream for
            callers that expect a file-like object.

Example:
        reader = SafeTextFileReader("data.csv", encoding="utf-8")
        lines = reader.read()

License: MIT

Copyright (c) 2025 Jim Schilling
"""

from __future__ import annotations

import codecs
import re
from collections import deque
from collections.abc import Iterator
from contextlib import contextmanager
from io import StringIO
from pathlib import Path

from splurge_safe_io.constants import (
    CANONICAL_NEWLINE,
    DEFAULT_BUFFER_SIZE,
    DEFAULT_CHUNK_SIZE,
    DEFAULT_ENCODING,
    DEFAULT_PREVIEW_LINES,
    MIN_BUFFER_SIZE,
    MIN_CHUNK_SIZE,
)
from splurge_safe_io.exceptions import (
    SplurgeSafeIoFileDecodingError,
    SplurgeSafeIoFileNotFoundError,
    SplurgeSafeIoFilePermissionError,
    SplurgeSafeIoOsError,
    SplurgeSafeIoUnknownError,
)
from splurge_safe_io.path_validator import PathValidator


class SafeTextFileReader:
    """Read text files with deterministic newline normalization.

    This helper reads raw bytes from disk and decodes them using the
    provided `encoding`. Newline sequences are normalized to ``\n`` and
    the class exposes convenience methods for full reads, previews, and
    streaming reads that yield lists of normalized lines.

    Args:
        file_path (str | pathlib.Path): Path to the text file to read. Will
            be validated and resolved by :class:`PathValidator`.
        encoding (str): Text encoding used to decode the file. Defaults to
            :data:`splurge_safe_io.constants.DEFAULT_ENCODING` ("utf-8").
        strip (bool): If True, strip leading/trailing whitespace from each
            returned line. Defaults to False.
        skip_header_lines (int): Number of lines to skip from the start of
            the file.
        skip_footer_lines (int): Number of lines to skip from the end of
            the file.
        chunk_size (int): Logical chunk size (maximum number of lines
            yielded by :meth:`read_as_stream`). Defaults to
            :data:`splurge_safe_io.constants.DEFAULT_CHUNK_SIZE`.
        buffer_size (int | None): Raw byte read size used when streaming.
            If None, :data:`splurge_safe_io.constants.DEFAULT_BUFFER_SIZE`
            is used. The implementation enforces a minimum buffer size of
            :data:`splurge_safe_io.constants.MIN_BUFFER_SIZE`.

    Attributes:
        file_path (pathlib.Path): Resolved path to the file.
        encoding (str): Encoding used for decoding.
        strip (bool): Whether whitespace stripping is enabled.
        chunk_size (int): Maximum lines per yielded chunk.
        buffer_size (int): Raw byte-read size used during streaming.

    Examples:

        Typical usage and tuning guidance::

            # Default: sensible for many files (buffer_size=8192, chunk_size=500)
            r = SafeTextFileReader('large.txt')

            # Low-latency consumer: smaller logical chunks but default byte buffer
            r = SafeTextFileReader('large.txt', chunk_size=10)
            for chunk in r.read_as_stream():
                process(chunk)

            # High-throughput: larger byte buffer to reduce syscalls and large chunks
            r = SafeTextFileReader('large.txt', buffer_size=65536, chunk_size=2000)
            for chunk in r.read_as_stream():
                bulk_process(chunk)

            # Small files or memory constrained: reduce buffer_size (MIN_BUFFER_SIZE enforced)
            r = SafeTextFileReader('small.txt', buffer_size=4096, chunk_size=50)

    Raises:
        SplurgeSafeIoFileNotFoundError: If the file does not exist.
        SplurgeSafeIoFilePermissionError: If the file cannot be read due to permission issues.
        SplurgeSafeIoPathValidationError: If the provided path fails validation checks.
    """

    def __init__(
        self,
        file_path: Path | str,
        *,
        encoding: str = DEFAULT_ENCODING,
        strip: bool = False,
        skip_header_lines: int = 0,
        skip_footer_lines: int = 0,
        chunk_size: int = DEFAULT_CHUNK_SIZE,
        buffer_size: int = DEFAULT_BUFFER_SIZE,
    ) -> None:
        self._file_path = PathValidator.validate_path(
            file_path, must_exist=True, must_be_file=True, must_be_readable=True
        )
        self._encoding = encoding or DEFAULT_ENCODING
        self._strip = strip
        self._skip_header_lines = max(skip_header_lines, 0)
        self._skip_footer_lines = max(skip_footer_lines, 0)
        self._chunk_size = max(chunk_size, MIN_CHUNK_SIZE)
        # buffer_size controls the raw byte-read size when streaming.
        self._buffer_size = max(buffer_size, MIN_BUFFER_SIZE)

    @property
    def file_path(self) -> Path:
        """Path to the file being read."""
        return Path(self._file_path)

    @property
    def encoding(self) -> str:
        """Text encoding used to decode the file."""
        return str(self._encoding)

    @property
    def strip(self) -> bool:
        """Whether to strip whitespace from each line."""
        return bool(self._strip)

    @property
    def skip_header_lines(self) -> int:
        """Number of header lines to skip."""
        return int(self._skip_header_lines)

    @property
    def skip_footer_lines(self) -> int:
        """Number of footer lines to skip."""
        return int(self._skip_footer_lines)

    @property
    def chunk_size(self) -> int:
        """Chunk size for streaming reads."""
        return int(self._chunk_size)

    @property
    def buffer_size(self) -> int:
        """Raw byte buffer size used when reading from disk during streaming."""
        return int(self._buffer_size)

    def _read(self) -> str:
        """Read the file bytes and return decoded text with no newline normalization applied.

        Returns:
            Decoded text (str).

        Raises:
            SplurgeSafeIoFileDecodingError: If decoding fails.
            SplurgeSafeIoFileNotFoundError: If the file does not exist.
            SplurgeSafeIoFilePermissionError: If the file cannot be read due to permission issues.
            SplurgeSafeIoFileOperationError: If an unexpected I/O error occurs.
            SplurgeSafeIoOsError: If a general OS error occurs.
            SplurgeSafeIoUnknownError: If an unexpected error occurs.
        """
        try:
            # Read raw bytes and decode explicitly to avoid the platform's
            # text-mode newline translations which can alter mixed line endings.
            with self.file_path.open("rb") as fh:
                raw = fh.read()
            return raw.decode(self.encoding)

        except FileNotFoundError as e:
            raise SplurgeSafeIoFileNotFoundError(
                f"File not found: {self.file_path}", details=str(e), original_exception=e
            ) from e
        except PermissionError as e:
            raise SplurgeSafeIoFilePermissionError(
                f"Permission denied reading file: {self.file_path}", details=str(e), original_exception=e
            ) from e
        except UnicodeError as e:
            raise SplurgeSafeIoFileDecodingError(
                f"Encoding error reading file: {self.file_path}", details=str(e), original_exception=e
            ) from e
        except OSError as e:
            raise SplurgeSafeIoOsError(
                f"OS error reading file: {self.file_path}", details=str(e), original_exception=e
            ) from e
        except Exception as e:
            raise SplurgeSafeIoUnknownError(
                f"Unexpected error reading file: {self.file_path}", details=str(e), original_exception=e
            ) from e

    def read(self) -> list[str]:
        """Read the entire file and return a list of normalized lines.

        The returned lines have newline sequences normalized to ``\n``.

        Returns:
            list[str]: Normalized lines from the file.

        Raises:
            SplurgeSafeIoFileDecodingError: If decoding fails.
            SplurgeSafeIoFileNotFoundError: If the file does not exist.
            SplurgeSafeIoFilePermissionError: If the file cannot be read due to permission issues.
            SplurgeSafeIoOsError: For unexpected OS-level errors.
            SplurgeSafeIoUnknownError: For other unexpected errors.
        """
        text = self._read()

        # Normalize newlines to LF
        normalized_text = text.replace("\r\n", CANONICAL_NEWLINE).replace("\r", CANONICAL_NEWLINE)
        lines = normalized_text.splitlines()

        if self.skip_header_lines:
            lines = lines[self.skip_header_lines :]

        if self.skip_footer_lines:
            if self.skip_footer_lines >= len(lines):
                return []
            lines = lines[: -self.skip_footer_lines]

        if self.strip:
            return [ln.strip() for ln in lines]
        return list(lines)

    def preview(self, max_lines: int = DEFAULT_PREVIEW_LINES) -> list[str]:
        """Return the first ``max_lines`` lines of the file after normalization.

        Args:
            max_lines (int): Maximum number of lines to return.

        Returns:
            list[str]: The first ``max_lines`` normalized lines.

        Raises:
            SplurgeSafeIoFileDecodingError: If decoding fails.
            SplurgeSafeIoFileNotFoundError: If the file does not exist.
            SplurgeSafeIoFilePermissionError: If the file cannot be read due to permission issues.
            SplurgeSafeIoOsError: For unexpected OS-level errors.
            SplurgeSafeIoUnknownError: For other unexpected errors.
        """
        text = self._read()

        normalized_text = text.replace("\r\n", CANONICAL_NEWLINE).replace("\r", CANONICAL_NEWLINE)
        lines = normalized_text.splitlines()
        if self.skip_header_lines:
            lines = lines[self.skip_header_lines :]
        if max_lines < 1:
            return []
        result = lines[:max_lines]
        return [ln.strip() for ln in result] if self.strip else list(result)

    def read_as_stream(self) -> Iterator[list[str]]:
        """Yield chunks of normalized lines from the file.

        The method decodes bytes incrementally using an incremental
        decoder. For encodings that cannot be handled incrementally the
        implementation falls back to a full read and yields chunked lists
        from the already-decoded lines.

        The streaming reader honors `skip_header_lines` and
        `skip_footer_lines`. Footer skipping is implemented by buffering
        the last N lines and only emitting lines once they can no longer
        be part of the footer.

        Yields:
            Iterator[list[str]]: Lists of normalized lines. Each yielded
            list has length <= ``chunk_size``.

        Raises:
            SplurgeSafeIoFileDecodingError: If decoding fails.
            SplurgeSafeIoFileNotFoundError: If the file does not exist.
            SplurgeSafeIoFilePermissionError: If the file cannot be read due to permission issues.
            SplurgeSafeIoOsError: For unexpected OS-level errors.
            SplurgeSafeIoUnknownError: For other unexpected errors.
        """
        decoder = codecs.getincrementaldecoder(self.encoding)()
        footer_buf: deque[str] = deque(maxlen=self.skip_footer_lines or 0)
        header_to_skip = self.skip_header_lines
        effective_chunk_size = self.chunk_size
        byte_read_size = self.buffer_size

        chunk: list[str] = []
        carry = ""

        # Regexes to detect newline characters similar to str.splitlines()
        _newline_trail_re = re.compile(r"(?:\r\n|\r|\n|\x0b|\x0c|\x1c|\x1d|\x1e|\x85|\u2028|\u2029)+$")

        # Read file in binary chunks and decode incrementally. If the
        # incremental decoder raises a UnicodeError (common for encodings
        # like UTF-16 when there's no BOM), fall back to a full read and
        # chunk the already-decoded lines. This preserves streaming for
        # well-behaved encodings while remaining robust.
        try:
            with self.file_path.open("rb") as fh:
                while True:
                    # Read raw bytes using the configured byte buffer size.
                    raw = fh.read(byte_read_size)
                    if not raw:
                        break
                    text = decoder.decode(raw)

                    # Use splitlines(True) to preserve newline characters and
                    # detect whether a part is a complete line (ends with any
                    # recognized newline). This matches the semantics of
                    # str.splitlines() used by read().
                    working = carry + text
                    parts = working.splitlines(True)
                    # Determine new carry: if last part ends with a newline
                    # sequence there is no carry. However, treat a lone
                    # carriage-return ("\r") at the end as an *incomplete*
                    # newline that should be carried into the next read. This
                    # avoids the case where a CRLF sequence is split across
                    # raw read boundaries and the leading LF becomes a
                    # separate empty line in the next chunk.
                    if parts:
                        last_part = parts[-1]
                        # If last_part ends with a single '\r' (not '\r\n')
                        # consider it a partial line and keep it as carry.
                        if last_part.endswith("\r") and not last_part.endswith("\r\n"):
                            carry = parts.pop()
                        elif _newline_trail_re.search(last_part):
                            carry = ""
                        else:
                            carry = parts.pop()
                    else:
                        carry = ""

                    for part in parts:
                        # strip trailing newline sequences for consistency with read()
                        line = _newline_trail_re.sub("", part)
                        if self.strip:
                            line = line.strip()

                        # Handle header skipping
                        if header_to_skip > 0:
                            header_to_skip -= 1
                            continue

                        # If we have footer lines to skip, buffer them
                        if self.skip_footer_lines:
                            footer_buf.append(line)
                            # If buffer is full, the leftmost item is safe to emit
                            if len(footer_buf) == footer_buf.maxlen:
                                emit_line = footer_buf.popleft()
                                chunk.append(emit_line)
                        else:
                            chunk.append(line)

                        if len(chunk) >= effective_chunk_size:
                            yield chunk
                            chunk = []

                # Finalize decoding to get any remaining text
                remaining = decoder.decode(b"", final=True)
                final_working = carry + remaining
                final_parts = final_working.splitlines(True) if final_working else []
                # Final carry detection mirrors the main-loop logic: prefer
                # to treat a lone trailing '\r' as an incomplete newline
                # that should be preserved rather than consumed.
                if final_parts:
                    last_part = final_parts[-1]
                    if last_part.endswith("\r") and not last_part.endswith("\r\n"):
                        final_carry = final_parts.pop()
                    elif _newline_trail_re.search(last_part):
                        final_carry = ""
                    else:
                        final_carry = final_parts.pop()
                else:
                    final_carry = ""

                for part in final_parts:
                    part = _newline_trail_re.sub("", part)
                    if self.strip:
                        part = part.strip()
                    if header_to_skip > 0:
                        header_to_skip -= 1
                        continue
                    if self.skip_footer_lines:
                        footer_buf.append(part)
                        if len(footer_buf) == footer_buf.maxlen:
                            chunk.append(footer_buf.popleft())
                    else:
                        chunk.append(part)

                # Emit the final carry as a line if present
                if final_carry:
                    part = _newline_trail_re.sub("", final_carry)
                    if self.strip:
                        part = part.strip()
                    if header_to_skip <= 0:
                        if self.skip_footer_lines:
                            footer_buf.append(part)
                        else:
                            chunk.append(part)

                # After EOF, footer_buf contains the footer lines (or fewer if file smaller)
                # Do not emit footer lines — they are intentionally skipped.
                # Flush any remaining chunked content (excluding footer buffer)
                if chunk:
                    yield chunk
        except UnicodeError:
            # Fallback: incremental decoder couldn't handle the encoding
            # (for example, UTF-16 without BOM). Use the full-read API and
            # yield chunked lists from the already-decoded lines. This
            # sacrifices streaming for correctness for these corner-case
            # encodings.
            lines = self.read()
            for i in range(0, len(lines), effective_chunk_size):
                yield lines[i : i + effective_chunk_size]

        except FileNotFoundError as e:
            raise SplurgeSafeIoFileNotFoundError(
                f"File not found: {self.file_path}", details=str(e), original_exception=e
            ) from e
        except PermissionError as e:
            raise SplurgeSafeIoFilePermissionError(
                f"Permission denied reading file: {self.file_path}", details=str(e), original_exception=e
            ) from e
        except OSError as e:
            raise SplurgeSafeIoOsError(
                f"OS error reading file: {self.file_path}", details=str(e), original_exception=e
            ) from e
        except Exception as e:
            raise SplurgeSafeIoUnknownError(
                f"Unexpected error reading file: {self.file_path}", details=str(e), original_exception=e
            ) from e


@contextmanager
def open_safe_text_reader(
    file_path: Path | str,
    *,
    encoding: str = DEFAULT_ENCODING,
    strip: bool = False,
    skip_header_lines: int = 0,
    skip_footer_lines: int = 0,
) -> Iterator[StringIO]:
    """Context manager returning an in-memory text stream with normalized newlines.

    This helper is useful when an API expects a file-like object. The
    context yields an :class:`io.StringIO` containing the normalized
    text (LF newlines). On successful exit the buffer is closed
    automatically. If an exception occurs inside the context the
    exception is propagated and no file-writing is performed.

    Args:
        file_path (str | pathlib.Path): Path to the file to open.
        encoding (str): Encoding to decode the file with.
        strip (bool): Whether to strip whitespace from each returned line.

    Yields:
        io.StringIO: In-memory text buffer with normalized newlines.

    Raises:
        SplurgeSafeIoFileDecodingError: If decoding fails.
        SplurgeSafeIoFileNotFoundError: If the file does not exist.
        SplurgeSafeIoFilePermissionError: If the file cannot be read due to permission issues.
        SplurgeSafeIoOsError: For unexpected OS-level errors.
        SplurgeSafeIoUnknownError: For other unexpected errors.
    """
    safe_reader = SafeTextFileReader(
        file_path,
        encoding=encoding,
        strip=strip,
        skip_header_lines=skip_header_lines,
        skip_footer_lines=skip_footer_lines,
    )
    text_lines = safe_reader.read()
    text = "\n".join(text_lines)
    sio = StringIO(text)
    try:
        yield sio
    finally:
        sio.close()
