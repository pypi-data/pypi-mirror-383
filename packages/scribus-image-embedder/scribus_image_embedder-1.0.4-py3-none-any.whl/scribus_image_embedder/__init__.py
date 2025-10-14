"""
Scribus Image Embedder
Embed images inline into Scribus .sla files
"""

__version__ = "1.0.0"
__author__ = "Afueth Thomas"

from .embedder import embed_images_in_sla

__all__ = ["embed_images_in_sla"]
