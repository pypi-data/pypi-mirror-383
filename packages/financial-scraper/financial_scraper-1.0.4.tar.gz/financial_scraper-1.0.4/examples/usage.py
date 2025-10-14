# Examples of using the market_scraper library
from financial_scraper import StatusInvestProvider, FundamentusProvider, InvestorTenProvider
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))


def status_invest_example():
    # Initialize the service with Status Invest provider
    service = StatusInvestProvider(
        download_path=BASE_DIR,
        filename="status_invest_stocks.csv",
        show_browser=True
    )

    # Fetch and save data
    service.run(sector=StatusInvestProvider.Sector.FINANCIAL_AND_OTHERS)


def fundamentus_example():
    # Initialize the service with Fundamentus provider
    service = FundamentusProvider(
        download_path=BASE_DIR,
    )

    # Fetch and save data
    service.run()


def investor_ten_example():
    # Initialize the service with Investor10 provider
    service = InvestorTenProvider(
        download_path=BASE_DIR,
        show_browser=True
    )

    # Fetch and save data
    service.run("2024")


if __name__ == "__main__":
    status_invest_example()
    fundamentus_example()
    investor_ten_example()
