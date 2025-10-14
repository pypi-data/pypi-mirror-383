"""
Arc flow Workflows Module

This module provides various workflow patterns for multi-agent orchestration:
- SequentialWorkflow: Linear chain execution
- ConcurrentWorkflow: Parallel execution
- AgentRearrange: Dynamic routing
- GraphWorkflow: DAG orchestration
- MixtureOfAgents: Expert synthesis
- GroupChat: Conversational collaboration
- ForestSwarm: Dynamic tree selection
- HierarchicalSwarm: Director-worker architecture
- HeavySwarm: Five-phase comprehensive analysis
- SwarmRouter: Universal workflow orchestrator
"""

from arc_flow.workflows.sequential_workflow import SequentialWorkflow
from arc_flow.workflows.concurrent_workflow import ConcurrentWorkflow
from arc_flow.workflows.agent_rearrange import AgentRearrange
from arc_flow.workflows.graph_workflow import GraphWorkflow
from arc_flow.workflows.mixture_of_agents import MixtureOfAgents
from arc_flow.workflows.group_chat import GroupChat
from arc_flow.workflows.forest_swarm import ForestSwarm, AgentTree
from arc_flow.workflows.hierarchical_swarm import HierarchicalSwarm
from arc_flow.workflows.heavy_swarm import HeavySwarm
from arc_flow.workflows.swarm_router import SwarmRouter

__all__ = [
    "SequentialWorkflow",
    "ConcurrentWorkflow",
    "AgentRearrange",
    "GraphWorkflow",
    "MixtureOfAgents",
    "GroupChat",
    "ForestSwarm",
    "AgentTree",
    "HierarchicalSwarm",
    "HeavySwarm",
    "SwarmRouter",
]
