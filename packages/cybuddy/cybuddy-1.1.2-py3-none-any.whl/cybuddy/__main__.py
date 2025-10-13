import asyncio
from .tui import SimpleTUI

def run():
    """Entry point for the cybuddy command."""
    try:
        asyncio.run(SimpleTUI().run())
    except KeyboardInterrupt:
        print("\nGood luck! Document your steps and be safe.")

if __name__ == "__main__":
    run()

