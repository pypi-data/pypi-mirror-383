#!/usr/bin/env python3
"""
Feishu Base Client

Core client class for Feishu (Lark) API operations including:
- Authentication and HTTP client initialization
- Long connection event handling via WebSocket
- Event subscription and processing
"""

import os
import threading
import warnings
from typing import Optional, Callable, Dict, Any

# Suppress deprecation warnings from lark_oapi library
warnings.filterwarnings("ignore", category=DeprecationWarning)

import lark_oapi as lark
from fastmcp.utilities.logging import get_logger

logger = get_logger(__name__)


class FeishuClient:
    """
    Base Feishu API client with core functionality for authentication and event handling
    """
    
    def __init__(self, 
            app_id: Optional[str] = None, app_secret: Optional[str] = None, 
            on_event: Callable[[lark.im.v1.P2ImMessageReceiveV1Data], None] = None,
        ):
        """
        Initialize Feishu client with app credentials
        
        Args:
            app_id: Feishu app ID (defaults to FEISHU_APP_ID env var)
            app_secret: Feishu app secret (defaults to FEISHU_APP_SECRET env var)
        """
        self.app_id = app_id or os.getenv("FEISHU_APP_ID")
        self.app_secret = app_secret or os.getenv("FEISHU_APP_SECRET")
        
        if not self.app_id or not self.app_secret:
            raise ValueError("FEISHU_APP_ID and FEISHU_APP_SECRET must be provided")
        
        # Initialize HTTP client for API calls
        self._http_client = lark.Client.builder() \
            .app_id(self.app_id) \
            .app_secret(self.app_secret) \
            .log_level(lark.LogLevel.INFO) \
            .build()
        
        # WebSocket client for long connection events
        self._ws_client = None
        self._event_handler = None
        self._is_connected = False
        self._on_event = on_event
    
    @property
    def http_client(self) -> lark.Client:
        """
        Get the HTTP client for API operations
        
        Returns:
            The lark HTTP client instance
        """
        return self._http_client
        
    def _build_event_handler(self) -> lark.EventDispatcherHandler:
        """
        Build event handler for processing different types of events
        Override this method in subclasses to customize event handling
        """
        return lark.EventDispatcherHandler.builder("", "") \
            .register_p2_im_message_receive_v1(self._handle_message_receive) \
            .register_p2_im_message_message_read_v1(self._handle_message_read) \
            .register_p2_customized_event("out_approval", self._handle_custom_event) \
            .build()
    
    def _handle_message_receive(self, data: lark.im.v1.P2ImMessageReceiveV1) -> None:
        """
        Handle incoming message events (v2.0)
        Override this method in subclasses to implement custom message handling
        
        Args:
            data: Message receive event data
        """
        if self._on_event is None:
            return
        self._on_event(data.event)

    def _handle_message_read(self, data: object) -> None:
        """
        Handle message read events (v1.0)
        Logs the event payload to confirm capture.
        """
        # try:
        #     # Marshal to JSON string if possible (SDK provides JSON helper)
        #     payload = lark.JSON.marshal(data, indent=4)
        #     print(f"[Lark] message_read_v1 captured: {payload}")
        # except Exception:
        #     print(f"[Lark] message_read_v1 captured (raw): {data}")
        pass
    
    def _handle_custom_event(self, data: lark.CustomizedEvent) -> None:
        """
        Handle custom events (v1.0)
        Override this method in subclasses to implement custom event handling
        
        Args:
            data: Custom event data
        """
        logger.info(f"[Custom Event] type: {data.type}, data: {lark.JSON.marshal(data, indent=4)}")
 
    def start_long_connection(self) -> bool:
        """
        Start long connection for receiving events via WebSocket
        
        Returns:
            True if connection started successfully, False otherwise
        """
        try:
            if self._is_connected:
                logger.warning("Long connection is already active")
                return True
            
            # Build event handler
            self._event_handler = self._build_event_handler()
            
            # Create WebSocket client
            self._ws_client = lark.ws.Client(
                self.app_id, 
                self.app_secret,
                event_handler=self._event_handler,
                log_level=lark.LogLevel.DEBUG
            )
            
            # Start connection in a separate thread
            def start_connection():
                try:
                    self._is_connected = True
                    logger.info("Starting Feishu long connection...")
                    self._ws_client.start()
                except Exception as e:
                    logger.error(f"Long connection failed: {str(e)}")
                    self._is_connected = False
            
            connection_thread = threading.Thread(target=start_connection, daemon=True)
            connection_thread.start()
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to start long connection: {str(e)}")
            return False
    
    def stop_long_connection(self) -> bool:
        """
        Stop the long connection
        
        Returns:
            True if connection stopped successfully, False otherwise
        """
        try:
            if not self._is_connected:
                logger.warning("Long connection is not active")
                return True
            
            if self._ws_client:
                # Note: The SDK might not have a direct stop method
                # This is a placeholder for connection cleanup
                self._is_connected = False
                logger.info("Long connection stopped")
                return True
            
            return False
            
        except Exception as e:
            logger.error(f"Failed to stop long connection: {str(e)}")
            return False
    
    def is_connected(self) -> bool:
        """
        Check if long connection is active
        
        Returns:
            True if connected, False otherwise
        """
        return self._is_connected
    
    def get_client_info(self) -> Dict[str, Any]:
        """
        Get client information and status
        
        Returns:
            Dictionary containing client information
        """
        return {
            "app_id": self.app_id,
            "is_connected": self._is_connected,
            "has_http_client": self._http_client is not None,
            "has_ws_client": self._ws_client is not None
        }