from __future__ import annotations
from typing import Any, Optional, Mapping, Final

__all__: Final[list[str]] = ["PyTera"]


class PyTera:

    def __init__(self, glob: str) -> None:
        """Load and parse templates based on the given file glob pattern.

        Args:
            glob (``str``): Glob pattern for template files (e.g., "templates/**/*.html").
                Supports recursive wildcards; paths should be accessible from the current working directory. The wildcard rules are the same as the operating system's
                file system matcher, common wildcards include *, ?, **, etc.

        Returns:
            None: Constructor has no return value.

        Raises:
            ``ValueError``: When the glob is invalid or template/macro/JSON related configurations are illegal (e.g., invalid glob pattern,
                invalid macro definitions, JSON errors, etc.).
            ``RuntimeError``: When template parsing fails, there are circular inheritance, missing parent templates, or other rendering system
                runtime errors (e.g., parsing errors, inheritance chain exceptions, etc.).
            ``UnicodeDecodeError``: UTF-8 decoding error occurred while reading template files.
            ``OSError``: I/O error occurred while reading template files (file not found, insufficient permissions, etc.).
            ``Exception``: Other uncategorized or unknown Tera errors.
        """
        ...

    def render_template(self, template: str, kwargs: Optional[Mapping[str, Any]] = ...) -> str:
        """Render the specified template and return the string result.

        Args:
            template (``str``): Template name (i.e., the key of the loaded template during construction), e.g., "hello.html".
            kwargs (``Optional[Mapping[str, Any]]``): Rendering context dictionary. Keys must be str;
                values can be basic types (int/float/bool/str/bytes, etc.), lists/tuples, dictionaries
                (dictionary keys must also be str), etc., which will be converted to JSON values and injected into the rendering context.
                If None, use empty context.

        Returns:
            str: The rendered string result.

        Raises:
            ``ValueError``: When the top-level kwargs keys cannot be converted to str, or template/macro/JSON related configurations are illegal
                (e.g., invalid macro definitions, JSON errors, etc.).
            ``TypeError``: When nested dictionaries have non-str keys, causing context conversion failure.
            ``RuntimeError``: Template missing, filter/function/test call failure, template parsing error, circular inheritance,
                missing parent template, etc., rendering-time errors.
            ``UnicodeDecodeError``: UTF-8 decoding error occurred while reading resources during rendering.
            ``OSError``: I/O error occurred during rendering.
            ``Exception``: Other unknown or uncategorized Tera errors.

        Examples:
            >>> from pytera import PyTera
            >>> t = PyTera("templates/*.html")
            >>> t.render_template("hello.html", {"name": "Alice"})
            '...'
        """
        ...

    def templates(self) -> list[str]:
        """Return the list of currently loaded template names.

        Returns:
            ``list[str]``: List of template names (keys).

        Examples:
            >>> from pytera import PyTera
            >>> t = PyTera("templates/*.html")
            >>> sorted(t.templates())  # doctest: +ELLIPSIS
            ['base.html', 'hello.html', ...]
        """
        ...