"""
Crypto Buy Bot — Entry Point
Run with: python main.py
"""

from bot import build_app
import logging

logger = logging.getLogger(__name__)


def main():
    app = build_app()
    logger.info("Bot starting — polling for updates...")
    app.run_polling(drop_pending_updates=True)


if __name__ == "__main__":
    main()
