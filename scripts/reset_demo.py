from pathlib import Path


DB_PATH = Path("support_chatbot.db")


def main() -> None:
    if DB_PATH.exists():
        DB_PATH.unlink()
        print("Removed support_chatbot.db")
    else:
        print("No demo database found")


if __name__ == "__main__":
    main()
