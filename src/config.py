from pathlib import Path
import os

from dotenv import load_dotenv

load_dotenv()

PROJECT_ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = PROJECT_ROOT / "data"
OUTPUT_DIR = PROJECT_ROOT / "outputs"
DEFAULT_DATASET = DATA_DIR / "bond_portfolio_data.csv"
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
