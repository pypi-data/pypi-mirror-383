"""
Enhanced demo wrapper for V2 functionality.
"""

import sys
from pathlib import Path

# Add V2 directory to path
v2_path = Path(__file__).parent.parent.parent.parent.parent / "V2"
if str(v2_path) not in sys.path:
    sys.path.insert(0, str(v2_path))

def main():
    """Main entry point for enhanced demo."""
    try:
        from scripts.enhanced_demo import main as v2_demo
        v2_demo()
    except ImportError as e:
        print(f"❌ Error: V2 enhanced demo not available: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == '__main__':
    main()
