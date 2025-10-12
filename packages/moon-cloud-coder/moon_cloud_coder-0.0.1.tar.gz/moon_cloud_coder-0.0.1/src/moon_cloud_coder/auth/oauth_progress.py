"""Qwen OAuth Progress Display Component for Moon-Cloud-Coder.

This module provides a CLI interface to show the progress of Qwen OAuth authentication.
"""

import time
import threading
from typing import Optional
from rich.console import Console
from rich.panel import Panel
from rich.text import Text
from rich.prompt import Prompt
from rich import print as rprint
from rich.spinner import Spinner
from qrcode import QRCode, constants
import os
import webbrowser
from pathlib import Path
import json


class QwenOAuthProgress:
    """Display Qwen OAuth authentication progress in CLI"""
    
    def __init__(self):
        self.console = Console()
        self.spinner = Spinner('dots')
        self.device_auth_info = None
        self.auth_status = 'idle'  # idle, polling, success, error, timeout, cancelled
        self.auth_message = None
        self.countdown_thread = None
        self.time_remaining = 0
        self.cancelled = False
        self.dots_sequence = ['', '.', '..', '...']
        self.dots_index = 0
        
        # For connecting to device auth flow
        self.auth_callback = None

    def set_device_auth_info(self, device_auth_info: dict):
        """Set the device authorization information"""
        self.device_auth_info = device_auth_info
        self.time_remaining = device_auth_info.get('expires_in', 300)  # Default to 5 minutes

    def start_countdown(self):
        """Start the countdown timer in a separate thread"""
        def countdown():
            while self.time_remaining > 0 and not self.cancelled:
                time.sleep(1)
                self.time_remaining -= 1
                if self.time_remaining <= 0:
                    self.auth_status = 'timeout'
                    self.auth_message = 'OAuth token expired. Please restart the authorization process.'
                    break

        self.countdown_thread = threading.Thread(target=countdown)
        self.countdown_thread.daemon = True
        self.countdown_thread.start()
    
    def animate_dots(self):
        """Animate dots in a separate thread"""
        def animate():
            while self.auth_status == 'polling' and self.time_remaining > 0 and not self.cancelled:
                time.sleep(0.5)
                self.dots_index = (self.dots_index + 1) % len(self.dots_sequence)
        
        animation_thread = threading.Thread(target=animate)
        animation_thread.daemon = True
        animation_thread.start()

    def display_progress(self):
        """Display the authentication progress"""
        if self.auth_status == 'timeout':
            # Display timeout message
            content = Text()
            content.append("Qwen OAuth Authentication Timeout\n", style="bold red")
            content.append(self.auth_message or f"OAuth token expired (over {self.device_auth_info.get('expires_in', 300)} seconds). Please select authentication method again.", style="white")
            content.append("\nPress any key to return to authentication type selection.", style="dim")
            
            self.console.print(Panel(content, border_style="red"))
            try:
                input("Press Enter to continue...")
            except KeyboardInterrupt:
                pass
            return False  # Indicate to go back to auth selection
        
        elif self.auth_status == 'cancelled':
            # Display cancellation message
            content = Text()
            content.append("Qwen OAuth Authentication Cancelled\n", style="bold yellow")
            content.append(self.auth_message or "Authentication was cancelled by the user.", style="white")
            content.append("\nReturning to authentication type selection...", style="dim")
            
            self.console.print(Panel(content, border_style="yellow"))
            return False  # Indicate to go back to auth selection
        
        elif self.auth_status == 'error':
            # Display error message
            content = Text()
            content.append("Qwen OAuth Authentication Error\n", style="bold red")
            content.append(self.auth_message or "An error occurred during authentication.", style="white")
            content.append("\nReturning to authentication type selection...", style="dim")
            
            self.console.print(Panel(content, border_style="red"))
            return False  # Indicate to go back to auth selection
        
        elif self.auth_status == 'success':
            # Display success message
            content = Text()
            content.append("Qwen OAuth Authentication Successful!\n", style="bold green")
            content.append(self.auth_message or "Authentication completed successfully.", style="white")
            content.append("\nReturning to main application...", style="dim")
            
            self.console.print(Panel(content, border_style="green"))
            return True  # Success, continue with main app
        
        if not self.device_auth_info:
            # Loading state
            content = Text()
            content.append(f"{self.spinner}" + " Waiting for Qwen OAuth authentication to start...", style="cyan")
            content.append(f"\nTime remaining: {self.time_remaining // 60}:{self.time_remaining % 60:02d}", style="dim")
            content.append("\n(Press Ctrl+C to cancel)", style="bold magenta")
            
            self.console.print(Panel(content, border_style="blue"))
        else:
            # Display QR code and auth information
            content = Text()
            content.append("Qwen OAuth Authentication\n", style="bold blue")
            content.append("Please visit this URL in your browser to authorize:\n", style="white")
            # Use the correct authorization URL format if available
            auth_url = self.device_auth_info.get('verification_uri_complete') or self.device_auth_info['verification_uri']
            content.append(auth_url, style="green bold")
            content.append("\n\nOr scan the QR code below:\n", style="white")

            # Generate and display QR code
            try:
                qr = QRCode(
                    version=1,
                    error_correction=constants.ERROR_CORRECT_L,
                    box_size=2,
                    border=4,
                )
                qr.add_data(self.device_auth_info['verification_uri_complete'])
                qr.make(fit=True)
                
                qr_lines = []
                for row in qr.get_matrix():
                    line = ''.join(['██' if cell else '  ' for cell in row])
                    qr_lines.append(line)
                
                qr_text = '\n'.join(qr_lines)
                content.append(f"\n{qr_text}\n", style="white")
                
                # Also try to open browser automatically
                auto_open = os.getenv('QWEN_AUTO_OPEN_BROWSER', 'true').lower() == 'true'
                if auto_open:
                    try:
                        webbrowser.open(self.device_auth_info['verification_uri_complete'])
                        content.append("\nBrowser opened automatically for authorization", style="dim")
                    except Exception:
                        content.append(f"\nFailed to open browser automatically", style="yellow")
            except ImportError:
                content.append(f"\n[QR code requires 'qrcode' package: pip install qrcode[pil]]\n", style="yellow")
            
            # Status section
            status_content = Text()
            status_content.append(f"{self.spinner}" + f" Waiting for authorization{self.dots_sequence[self.dots_index]}", style="cyan")
            status_content.append(f"\nTime remaining: {self.time_remaining // 60}:{self.time_remaining % 60:02d}", style="dim")
            status_content.append("\n(Press Ctrl+C to cancel)", style="bold magenta")
            
            # Combine auth info and status
            full_content = Text.assemble(content, status_content)
            self.console.print(Panel(full_content, border_style="blue"))

        return True  # Continue showing progress
    
    def run_authentication_flow(self, client):
        """Run the full authentication flow with progress display"""
        from .qwen_oauth import authenticate_with_device_flow
        
        try:
            # Start countdown timer and animation
            self.start_countdown()
            self.animate_dots()
            
            # Perform authentication using the existing device flow
            success = authenticate_with_device_flow(client)
            
            if success:
                self.auth_status = 'success'
                self.auth_message = 'Authentication successful! Access token obtained.'
                return True
            else:
                self.auth_status = 'cancelled'
                self.auth_message = 'Authentication was cancelled or failed.'
                return False
                
        except KeyboardInterrupt:
            self.cancelled = True
            self.auth_status = 'cancelled'
            self.auth_message = 'Authentication cancelled by user.'
            return False
        except Exception as e:
            self.cancelled = True
            self.auth_status = 'error'
            self.auth_message = f'Error during authentication: {str(e)}'
            return False