"""
Azure Functions initialization module
"""

import logging
import sys
import os
from pathlib import Path

# Add services directory to path for imports
sys.path.insert(0, str(Path(__file__).parent / "services"))

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

logger.info("ZipCode Population Density Azure Functions initialized")