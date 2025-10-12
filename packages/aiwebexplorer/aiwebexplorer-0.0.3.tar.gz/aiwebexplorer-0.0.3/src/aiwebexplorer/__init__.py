"""AI Web Explorer - An agent for agents to explore the web."""

try:
    from ._version import version as __version__
except ImportError:
    # Fallback for development
    __version__ = "0.0.0+dev"
