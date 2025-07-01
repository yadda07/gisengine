"""
Standard exceptions for GISENGINE
🔒 CORE STABLE
"""

class GISEngineException(Exception):
    """Exception de base pour toutes les erreurs GISENGINE"""
    pass

class ComponentException(GISEngineException):
    """Erreur liée aux composants"""
    pass

class WorkflowException(GISEngineException):
    """Erreur liée à l'exécution de workflow"""
    pass

class ValidationException(GISEngineException):
    """Erreur de validation"""
    pass

class RegistryException(GISEngineException):
    """Erreur du registry de composants"""
    pass

class LoaderException(GISEngineException):
    """Erreur de chargement de plugins"""
    pass
