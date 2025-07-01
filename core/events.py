"""
Event system for component communication
🔒 CORE STABLE
"""

import logging
from typing import Dict, List, Callable, Any
from enum import Enum

logger = logging.getLogger(__name__)

class EventType(Enum):
    """Types d'événements système"""
    COMPONENT_REGISTERED = "component_registered"
    COMPONENT_EXECUTED = "component_executed"
    WORKFLOW_STARTED = "workflow_started"
    WORKFLOW_COMPLETED = "workflow_completed"
    WORKFLOW_FAILED = "workflow_failed"
    PROGRESS_UPDATE = "progress_update"

class EventSystem:
    """Système d'événements pour communication entre composants"""
    
    def __init__(self):
        self._listeners: Dict[EventType, List[Callable]] = {}
    
    def subscribe(self, event_type: EventType, callback: Callable):
        """S'abonne à un type d'événement"""
        if event_type not in self._listeners:
            self._listeners[event_type] = []
        
        self._listeners[event_type].append(callback)
        logger.debug(f"Subscribed to event: {event_type}")
    
    def unsubscribe(self, event_type: EventType, callback: Callable):
        """Se désabonne d'un type d'événement"""
        if event_type in self._listeners:
            try:
                self._listeners[event_type].remove(callback)
                logger.debug(f"Unsubscribed from event: {event_type}")
            except ValueError:
                logger.warning(f"Callback not found for event: {event_type}")
    
    def emit(self, event_type: EventType, data: Any = None):
        """Émet un événement vers tous les listeners"""
        if event_type in self._listeners:
            for callback in self._listeners[event_type]:
                try:
                    callback(data)
                except Exception as e:
                    logger.error(f"Error in event callback for {event_type}: {e}")
    
    def clear_all(self):
        """Supprime tous les listeners (pour tests)"""
        self._listeners.clear()
