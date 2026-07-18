from __future__ import annotations

from pyrogram import Client


def main() -> None:
    print("API_ID و API_HASH را از my.telegram.org دریافت کنید.")
    api_id = int(input("API_ID: ").strip())
    api_hash = input("API_HASH: ").strip()
    with Client("session_generator", api_id=api_id, api_hash=api_hash, in_memory=True) as app:
        print("\nSESSION_STRING:\n")
        print(app.export_session_string())
        print("\nاین مقدار محرمانه است و فقط داخل .env قرار می‌گیرد.")


if __name__ == "__main__":
    main()
