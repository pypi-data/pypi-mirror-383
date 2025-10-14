from pathlib import Path


def mock_process(geom, model):
  module_dir = Path(__file__).parent
  zip_path = module_dir / 'mock.zip'
  with open(zip_path, 'rb') as f:
    data = f.read()

  return data
