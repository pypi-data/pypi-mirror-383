import asyncio
from python_client import TicTacToeClient

class MyBot(TicTacToeClient): 
    async def handle_turn(self, state):
        print(state.__repr__())
        for i, cell in enumerate(state.board):
            if cell is None:
                return i
        raise "Something is wrong, board is full"

async def main():
    client = MyBot()
    await client.connect("ws://127.0.0.1:9001")

asyncio.run(main())