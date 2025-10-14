"""Graceful exit handling for DataSage MCP server."""

import signal
import sys
import logging
import threading
import time
from typing import Optional, Callable


class GracefulExit:
    """Handle graceful shutdown of the MCP server."""
    
    def __init__(self):
        self.shutdown_requested = False
        self.cleanup_callbacks = []
        self.logger = logging.getLogger(__name__)
        self._original_handlers = {}
        
    def setup_signal_handlers(self):
        """Setup signal handlers for graceful shutdown."""
        # Store original handlers
        self._original_handlers[signal.SIGINT] = signal.signal(signal.SIGINT, self._signal_handler)
        self._original_handlers[signal.SIGTERM] = signal.signal(signal.SIGTERM, self._signal_handler)
        
        # Windows compatibility
        if hasattr(signal, 'SIGBREAK'):
            self._original_handlers[signal.SIGBREAK] = signal.signal(signal.SIGBREAK, self._signal_handler)
        
        self.logger.info("Signal handlers registered for graceful shutdown")
    
    def _signal_handler(self, signum: int, frame):
        """Handle shutdown signals gracefully."""
        signal_names = {
            signal.SIGINT: "SIGINT (Ctrl+C)",
            signal.SIGTERM: "SIGTERM",
        }
        
        if hasattr(signal, 'SIGBREAK'):
            signal_names[signal.SIGBREAK] = "SIGBREAK"
        
        signal_name = signal_names.get(signum, f"Signal {signum}")
        self.logger.info(f"Received {signal_name}, initiating graceful shutdown...")
        
        if not self.shutdown_requested:
            self.shutdown_requested = True
            self._perform_shutdown()
        else:
            self.logger.warning("Shutdown already in progress, forcing exit...")
            sys.exit(1)
    
    def _perform_shutdown(self):
        """Perform graceful shutdown sequence."""
        try:
            self.logger.info("Starting graceful shutdown sequence")
            
            # Execute cleanup callbacks quickly
            for i, callback in enumerate(self.cleanup_callbacks):
                try:
                    self.logger.info(f"Executing cleanup callback {i+1}/{len(self.cleanup_callbacks)}")
                    callback()
                except Exception as e:
                    self.logger.error(f"Error in cleanup callback {i+1}: {e}")
            
            self.logger.info("DataSage MCP Server shutdown complete")
            
        except Exception as e:
            self.logger.error(f"Error during shutdown: {e}")
        finally:
            # Restore original signal handlers
            self._restore_signal_handlers()
            # Force exit immediately
            import os
            os._exit(0)
    
    def _restore_signal_handlers(self):
        """Restore original signal handlers."""
        for sig, handler in self._original_handlers.items():
            signal.signal(sig, handler)
    
    def add_cleanup_callback(self, callback: Callable[[], None]):
        """Add a cleanup callback to be executed during shutdown."""
        self.cleanup_callbacks.append(callback)
    
    def is_shutdown_requested(self) -> bool:
        """Check if shutdown has been requested."""
        return self.shutdown_requested


# Global instance
_graceful_exit = GracefulExit()


def setup_graceful_exit() -> GracefulExit:
    """Setup graceful exit handling and return the instance."""
    _graceful_exit.setup_signal_handlers()
    return _graceful_exit


def add_cleanup_callback(callback: Callable[[], None]):
    """Add a cleanup callback for shutdown."""
    _graceful_exit.add_cleanup_callback(callback)


def is_shutdown_requested() -> bool:
    """Check if shutdown has been requested."""
    return _graceful_exit.shutdown_requested
