"""
Main interface for ivschat service.

[Documentation](https://youtype.github.io/types_aiobotocore_docs/types_aiobotocore_ivschat/)

Copyright 2025 Vlad Emelianov

Usage::

    ```python
    from aiobotocore.session import get_session
    from types_aiobotocore_ivschat import (
        Client,
        IvschatClient,
    )

    session = get_session()
    async with session.create_client("ivschat") as client:
        client: IvschatClient
        ...

    ```
"""

from .client import IvschatClient

Client = IvschatClient

__all__ = ("Client", "IvschatClient")
