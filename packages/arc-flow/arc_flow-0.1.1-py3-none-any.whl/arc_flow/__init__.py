"""
Arc - A Professional Hierarchical Multi-Agent Framework

A comprehensive framework for building hierarchical multi-agent systems with LangGraph,
featuring coordinator-planner-supervisor architecture, team management, and flexible
agent orchestration with improved error handling and validation.

Version: 1.0.0
Author: Arc  Team
License: MIT
"""

__version__ = "1.0.0"
__author__ = "Arc Team"

from arc_flow.core.base import BaseAgent, BaseTeam, BaseNode
from arc_flow.core.state import State, StateManager
from arc_flow.core.supervisor import Supervisor
from arc_flow.agents.team_builder import TeamBuilder
from arc_flow.agents.agent_factory import AgentFactory
from arc_flow.nodes.coordinator import CoordinatorNode
from arc_flow.nodes.planner import PlannerNode
from arc_flow.nodes.generator import ResponseGeneratorNode
from arc_flow.config.config import Config, load_config
from arc_flow.core.orchestrator import GraphOrchestrator
from arc_flow.utils.logging import setup_logging, get_logger

# New imports for improved framework
from arc import exceptions
from arc_flow.config import validation
from arc_flow.utils import retry

__all__ = [
    # Core classes
    "BaseAgent",
    "BaseTeam",
    "BaseNode",
    "State",
    "StateManager",
    "Supervisor",
    
    # Agent classes
    "TeamBuilder",
    "AgentFactory",
    
    # Node classes
    "CoordinatorNode",
    "PlannerNode",
    "ResponseGeneratorNode",
    
    # Configuration
    "Config",
    "load_config",
    
    # Orchestration
    "GraphOrchestrator",
    
    # Utilities
    "setup_logging",
    "get_logger",
    
    # New modules
    "exceptions",
    "validation",
    "retry",
    
    # Version
    "__version__",
    "__author__",
]
