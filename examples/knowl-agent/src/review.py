#!/usr/bin/env python3
"""交互式知识库评审工具"""

import sys
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(BASE_DIR.parent))

from src.review import main

if __name__ == "__main__":
    main()
