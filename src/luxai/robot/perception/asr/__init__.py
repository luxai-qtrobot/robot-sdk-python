try:
    from .azure import ASRAzureNode
except ImportError:
    ASRAzureNode = None

try:
    from .riva import ASRRivaNode
except ImportError:
    ASRRivaNode = None

try:
    from .groq import ASRGroqNode
except ImportError:
    ASRGroqNode = None

try:
    from .parakeet import ASRParakeetNode
except ImportError:
    ASRParakeetNode = None

__all__ = [
    "ASRAzureNode",
    "ASRRivaNode",
    "ASRGroqNode",
    "ASRParakeetNode",
]
