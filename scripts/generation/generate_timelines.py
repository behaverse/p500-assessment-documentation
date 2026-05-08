#!/usr/bin/env python3
"""
Timeline Generation Script - Run from scripts/generation directory
Direct runner for the enhanced timeline page generator
"""

import os
import sys
from pathlib import Path

# Ensure we're in the project root (go up two levels from scripts/generation/)
project_root = Path(__file__).parent.parent.parent
os.chdir(project_root)

# Import and run the generation script directly from same directory
from generate_enhanced_timeline_pages import main

if __name__ == "__main__":
    print("🚀 Generating enhanced timeline pages...")
    main()
    print("✅ Timeline generation complete!")