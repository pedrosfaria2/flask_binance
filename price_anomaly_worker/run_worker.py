from .worker import PriceAnomalyWorker


def main():
    worker = PriceAnomalyWorker()
    worker.run()


if __name__ == "__main__":
    main()
