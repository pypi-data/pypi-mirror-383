"""
chuk_virtual_fs - A secure, modular virtual filesystem designed for AI agent sandboxes
"""

# Import core components (async native)
# Import utilities
from chuk_virtual_fs import exceptions, path_utils

# Import provider registry
from chuk_virtual_fs.directory import Directory
from chuk_virtual_fs.file import File
from chuk_virtual_fs.fs_manager import AsyncVirtualFileSystem
from chuk_virtual_fs.node_base import FSNode
from chuk_virtual_fs.node_info import EnhancedNodeInfo
from chuk_virtual_fs.provider_base import AsyncStorageProvider
from chuk_virtual_fs.providers import get_provider, list_providers, register_provider
from chuk_virtual_fs.security_config import (
    SECURITY_PROFILES,
    create_custom_security_profile,
    create_secure_provider,
    get_available_profiles,
    get_profile_settings,
)
from chuk_virtual_fs.security_wrapper import SecurityWrapper

# Backwards compatibility aliases
FSNodeInfo = EnhancedNodeInfo
StorageProvider = AsyncStorageProvider
VirtualFileSystem = AsyncVirtualFileSystem  # Legacy sync name now points to async

# Export main classes
__all__ = [
    # Core async components
    "AsyncVirtualFileSystem",
    "VirtualFileSystem",  # Points to AsyncVirtualFileSystem for backward compatibility
    "EnhancedNodeInfo",
    "FSNodeInfo",  # Alias for EnhancedNodeInfo
    "AsyncStorageProvider",
    "StorageProvider",  # Alias for AsyncStorageProvider
    "get_provider",
    "list_providers",
    "register_provider",
    # Security components
    "SecurityWrapper",
    "create_secure_provider",
    "create_custom_security_profile",
    "get_available_profiles",
    "get_profile_settings",
    "SECURITY_PROFILES",
    # Utilities
    "path_utils",
    "exceptions",
    # Legacy components (still available for backward compatibility)
    "FSNode",
    "Directory",
    "File",
]
