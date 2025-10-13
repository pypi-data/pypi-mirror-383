import os
from typing import List, Optional

from scenographer._shared.core._default_storage import DEFAULT_STORAGE


def use_web_extensions(args: Optional[List[str]] = None,
                       source_directory: Optional[str] = None) -> List[str]:
    """
    Configures the context to include WebExtensions.

    Parameters
    ----------
    args : Optional[List[str]]
        Additional arguments to pass to the browser instance.
    source_directory : Optional[str]
        The source directory.

    Returns
    -------
    List[str]
        Additional arguments to pass to the browser instance.
    """

    SEPARATOR = ","

    if source_directory is None:
        source_directory = DEFAULT_STORAGE.get_extensions_directory()

    if args is None:
        args = []

    if os.path.exists(source_directory):
        extensions = filter(
            lambda path: not os.path.isfile(
                os.path.join(source_directory, path)),
            os.listdir(source_directory)
        )

        extensions_path = map(
            lambda path: os.path.join(source_directory, path),
            extensions
        )

        extensions_list = SEPARATOR.join(extensions_path)

        args.append(f"--load-extension={extensions_list}")
        args.append(f"--disable-extensions-except={extensions_list}")

    return args
