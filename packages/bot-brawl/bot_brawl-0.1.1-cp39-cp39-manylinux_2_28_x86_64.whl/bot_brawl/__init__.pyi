from typing import Protocol, List, Optional
from abc import ABC, abstractmethod

class BaseClient:
    async def connect(self, url: str) -> None: ...


class PyTicTacToeState:
    @property
    def board(self) -> List[Optional[str]]: ...
    def __repr__(self) -> str: ...

class TicTacToeClient(BaseClient):
    def __init__(self) -> None: ...
    @abstractmethod
    async def handle_turn(self, state: PyTicTacToeState) -> int:
        """Must be implemented by subclasses"""