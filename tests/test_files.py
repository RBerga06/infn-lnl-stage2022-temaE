"""Make sure the shipped data is not corrupted."""
from hashlib import sha256
from pathlib import Path


DIR = Path(__file__).parent/"src"


def test_data_root():
    assert sha256((DIR/"data.root").read_bytes()).hexdigest() == "0ec9c47b0264622f1bda62b67e3b9c111a2c0436c52335c0d17599615b9a611a"


def test_fondo_root():
    assert sha256((DIR/"fondo.root").read_bytes()).hexdigest() == "0c4ea828562f7f4d1096a1a47363d9d3ae60fd13318724f3ed7086a2f55224b7"
