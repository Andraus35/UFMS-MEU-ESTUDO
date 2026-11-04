"""CLI operacional: provisionar calendário e testar configuração sem imprimir segredos."""
import argparse
import os

from .google_calendar import GoogleCalendar


def main():
    parser = argparse.ArgumentParser(description="Configuração Oracle/UFMS")
    parser.add_argument("operation", choices=["provision-calendar"])
    args = parser.parse_args()
    if args.operation == "provision-calendar":
        keys = ["UFMS_GOOGLE_CLIENT_ID", "UFMS_GOOGLE_CLIENT_SECRET",
                "UFMS_GOOGLE_REFRESH_TOKEN"]
        if not all(os.getenv(k) for k in keys):
            parser.error("OAuth offline ainda não configurado na Oracle")
        client = GoogleCalendar(*(os.environ[k] for k in keys))
        print("Calendário criado. Salve este ID no segredo UFMS_GOOGLE_CALENDAR_ID:")
        print(client.create_study_calendar())


if __name__ == "__main__":
    main()
