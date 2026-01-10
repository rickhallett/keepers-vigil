"""
Test personas representing different user behavior patterns.
"""

from .base import Persona, PersonaRegistry
from .explorer import MethodicalExplorer
from .speedrunner import Speedrunner
from .confused import ConfusedUser
from .completionist import Completionist
from .chaotic import ChaoticPlayer

# Register all built-in personas
PersonaRegistry.register(MethodicalExplorer())
PersonaRegistry.register(Speedrunner())
PersonaRegistry.register(ConfusedUser())
PersonaRegistry.register(Completionist())
PersonaRegistry.register(ChaoticPlayer())

__all__ = [
    "Persona",
    "PersonaRegistry",
    "MethodicalExplorer",
    "Speedrunner",
    "ConfusedUser",
    "Completionist",
    "ChaoticPlayer",
]
