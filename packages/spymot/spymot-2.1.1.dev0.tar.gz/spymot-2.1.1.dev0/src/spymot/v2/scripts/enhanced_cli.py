"""
Enhanced CLI wrapper for V2 functionality.
"""

import sys
from pathlib import Path

# Add V2 directory to path
v2_path = Path(__file__).parent.parent.parent.parent.parent / "V2"
if str(v2_path) not in sys.path:
    sys.path.insert(0, str(v2_path))

def main():
    """Main entry point for enhanced CLI."""
    try:
        from scripts.enhanced_cli import main as v2_main
        v2_main()
    except ImportError as e:
        print(f"❌ Error: V2 enhanced CLI not available: {e}", file=sys.stderr)
        sys.exit(1)

def analyze(input_file, uniprot_id=None, output=None, output_format='json', 
           motif_db_type='all', cancer_only=False, min_confidence=0.0, verbose=False):
    """Analyze protein sequence using V2 enhanced functionality."""
    try:
        from scripts.enhanced_cli import analyze as v2_analyze
        v2_analyze(input_file, uniprot_id, output, output_format, motif_db_type,
                  cancer_only, min_confidence, verbose)
    except ImportError as e:
        print(f"❌ Error: V2 enhanced analysis not available: {e}", file=sys.stderr)
        sys.exit(1)

def databases(output_format='txt', verbose=False):
    """Show database information."""
    try:
        from scripts.enhanced_cli import databases as v2_databases
        v2_databases(output_format, verbose)
    except ImportError as e:
        print(f"❌ Error: V2 database info not available: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == '__main__':
    main()
