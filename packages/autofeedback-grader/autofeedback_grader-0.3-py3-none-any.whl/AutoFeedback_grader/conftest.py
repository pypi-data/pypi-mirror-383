# conftest.py

def pytest_addoption(parser):
    parser.addoption("--fname", action="store", default="main.ipynb")
