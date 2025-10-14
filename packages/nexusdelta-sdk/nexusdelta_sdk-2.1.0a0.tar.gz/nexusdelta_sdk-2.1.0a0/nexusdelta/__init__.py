# Nexus Delta SDK
# Official Python SDK for the Nexus Delta AI Agent Marketplace

"""
Nexus Delta SDK - AI Agent Marketplace Platform

A comprehensive SDK for building, deploying, and managing AI agents
in a decentralized marketplace ecosystem.
"""

from .sdk import NexusDeltaSDK
from .exceptions import NexusDeltaError, AuthenticationError, AgentError

__version__ = "2.0.0"
__author__ = "Nexus Delta Team"
__description__ = "AI Agent Marketplace SDK"

__all__ = [
    "NexusDeltaSDK",
    "NexusDeltaError",
    "AuthenticationError",
    "AgentError"
]