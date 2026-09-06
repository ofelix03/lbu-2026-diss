from pathlib import Path

def load_dirs(base_dir):
  BASE_DIR = Path(base_dir)

  DATA = BASE_DIR / 'data'
  MODELS = BASE_DIR / 'models'
  PROCESSED_DIR = DATA / 'processed'
  OUTPUT_DIR = DATA / 'outputs'
  OUTPUT_EDA_DIR = DATA / 'eda'
  OUTPUT_GEOSPAT_DIR = DATA / 'geospatial'
  OUTPUT_ML_DIR = DATA / 'ml'
  AUDIT_DIR = PROCESSED_DIR / 'audit'

  REQUIRED_DIRS = [BASE_DIR, MODELS, PROCESSED_DIR, AUDIT_DIR, OUTPUT_DIR, OUTPUT_EDA_DIR, OUTPUT_GEOSPAT_DIR, OUTPUT_ML_DIR]

  for dir in REQUIRED_DIRS:
    dir.mkdir(exist_ok=True)
    
  return REQUIRED_DIRS

# if __name__ == "__main__":
#     print('loading')
#     dirs = load_dirs()
