import logging

from .gui import DataProphetApp


def main():
    logging.basicConfig(
        level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
    )
    app = DataProphetApp()
    app.run()


if __name__ == "__main__":
    main()
