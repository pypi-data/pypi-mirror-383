"""
Spymot: Advanced Protein Motif Detection with AlphaFold Structural Validation

A comprehensive protein analysis platform that combines motif detection with 3D structure 
validation using AlphaFold2 confidence scores. Designed for cancer biology research, 
drug discovery, and functional genomics.

Version Information:
- V1: Original foundational system with basic motif detection
- V2: Enhanced production system with 94.6% motif coverage and advanced features

Usage:
    from spymot import analyze_sequence  # V1 functionality
    from spymot.v2 import EnhancedSpymotAnalyzer  # V2 functionality
    
    # Basic analysis
    result = analyze_sequence("p53", "MEEPQSDPSVEPPLSQETFSD...")
    
    # Enhanced analysis
    analyzer = EnhancedSpymotAnalyzer()
    result = analyzer.analyze_sequence_comprehensive("p53", "MEEPQSDPSVEPPLSQETFSD...")
"""

from ._version import __version__

# V1 Imports (Original functionality)
try:
    from .v1.analyzer import analyze_sequence, analyze_by_pdb
    from .v1.motifs import scan_motifs, get_motif_statistics
    from .v1.targeting import predict_targeting
    from .v1.afdb import get_prediction_meta, fetch_pdb_text, mean_plddt_over_region
    from .v1.utils import read_fasta, validate_sequence
    
    __all_v1__ = [
        "analyze_sequence",
        "analyze_by_pdb", 
        "scan_motifs",
        "get_motif_statistics",
        "predict_targeting",
        "get_prediction_meta",
        "fetch_pdb_text",
        "mean_plddt_over_region",
        "read_fasta",
        "validate_sequence"
    ]
except ImportError:
    __all_v1__ = []

# V2 Imports (Enhanced functionality)
try:
    from .v2.enhanced_analyzer import EnhancedSpymotAnalyzer
    from .v2.context_aware_detector import ContextAwareDetector
    from .v2.enhanced_motifs_db import EnhancedMotifDatabase
    
    __all_v2__ = [
        "EnhancedSpymotAnalyzer",
        "ContextAwareDetector", 
        "EnhancedMotifDatabase"
    ]
except ImportError:
    __all_v2__ = []

# Main exports (V1 for backward compatibility)
__all__ = [
    "__version__",
    # V1 exports
    "analyze_sequence",
    "analyze_by_pdb",
    "scan_motifs", 
    "get_motif_statistics",
    "predict_targeting",
    "read_fasta",
    "validate_sequence",
    # V2 exports
    "EnhancedSpymotAnalyzer",
    "ContextAwareDetector",
    "EnhancedMotifDatabase"
]

# Package metadata
__author__ = "Erfan Zohrabi"
__email__ = "erfanzohrabi.ez@gmail.com"
__description__ = "Advanced Protein Motif Detection with AlphaFold Structural Validation"
__url__ = "https://github.com/ErfanZohrabi/Spymot"
__license__ = "MIT"

# Version info
def get_version():
    """Get the current version of Spymot."""
    return __version__

def get_version_info():
    """Get detailed version information."""
    return {
        "version": __version__,
        "author": __author__,
        "email": __email__,
        "description": __description__,
        "url": __url__,
        "license": __license__,
        "v1_available": len(__all_v1__) > 0,
        "v2_available": len(__all_v2__) > 0
    }
