"""
Dynamic Log Extractor for ForensIQ CLI Tool

This module provides dynamic log extraction from various system sources including:
- Windows Event Logs (Security, System, Application)
- System process logs
- Network activity logs
- File system activity logs
- Registry changes (Windows)
- Authentication logs
- Service logs

The extractor can be configured to collect logs from different sources
and send them to the ForensIQ API for analysis.
"""

import os
import sys
import json
import subprocess
import time
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from pathlib import Path
import platform

if platform.system() == "Windows":
    try:
        import win32evtlog
        import win32con
        import win32security
        WINDOWS_LOGS_AVAILABLE = True
    except ImportError:
        WINDOWS_LOGS_AVAILABLE = False
        logging.warning("Windows event log modules not available. Install pywin32 for full functionality.")

class DynamicLogExtractor:
    """Extract logs dynamically from various system sources."""
    
    def __init__(self, logger: logging.Logger = None):
        self.logger = logger or logging.getLogger(__name__)
        self.system = platform.system()
        self.last_extraction_time = {}
        
        # Configure log sources based on system
        self.log_sources = self._configure_log_sources()
    
    def _configure_log_sources(self) -> Dict[str, Dict[str, Any]]:
        """Configure available log sources based on the operating system."""
        sources = {}
        
        if self.system == "Windows":
            sources.update({
                'security_events': {
                    'type': 'windows_eventlog',
                    'log_name': 'Security',
                    'description': 'Windows Security Events',
                    'enabled': WINDOWS_LOGS_AVAILABLE
                },
                'system_events': {
                    'type': 'windows_eventlog',
                    'log_name': 'System',
                    'description': 'Windows System Events',
                    'enabled': WINDOWS_LOGS_AVAILABLE
                },
                'application_events': {
                    'type': 'windows_eventlog',
                    'log_name': 'Application',
                    'description': 'Windows Application Events',
                    'enabled': WINDOWS_LOGS_AVAILABLE
                },
                'powershell_logs': {
                    'type': 'windows_eventlog',
                    'log_name': 'Microsoft-Windows-PowerShell/Operational',
                    'description': 'PowerShell Execution Logs',
                    'enabled': WINDOWS_LOGS_AVAILABLE
                }
            })
        
        elif self.system == "Linux":
            sources.update({
                'auth_logs': {
                    'type': 'file',
                    'path': '/var/log/auth.log',
                    'description': 'Authentication logs',
                    'enabled': os.path.exists('/var/log/auth.log')
                },
                'syslog': {
                    'type': 'file',
                    'path': '/var/log/syslog',
                    'description': 'System logs',
                    'enabled': os.path.exists('/var/log/syslog')
                },
                'kernel_logs': {
                    'type': 'file',
                    'path': '/var/log/kern.log',
                    'description': 'Kernel logs',
                    'enabled': os.path.exists('/var/log/kern.log')
                }
            })
        
        # Common sources for all systems
        sources.update({
            'process_monitor': {
                'type': 'process_monitor',
                'description': 'Running processes and new process creation',
                'enabled': True
            },
            'network_connections': {
                'type': 'network_monitor',
                'description': 'Active network connections',
                'enabled': True
            },
            'file_system_activity': {
                'type': 'filesystem_monitor',
                'description': 'File system changes',
                'enabled': True
            }
        })
        
        return sources
    
    def get_available_sources(self) -> List[Dict[str, Any]]:
        """Get list of available log sources."""
        available = []
        for source_id, config in self.log_sources.items():
            if config['enabled']:
                available.append({
                    'id': source_id,
                    'type': config['type'],
                    'description': config['description']
                })
        return available
    
    def extract_logs(self, sources: List[str] = None, time_range_minutes: int = 5) -> Dict[str, List[Dict[str, Any]]]:
        """
        Extract logs from specified sources.
        
        Args:
            sources: List of source IDs to extract from (None for all available)
            time_range_minutes: Extract logs from last N minutes
            
        Returns:
            Dict mapping source IDs to lists of log entries
        """
        if sources is None:
            sources = [s for s in self.log_sources.keys() if self.log_sources[s]['enabled']]
        
        extracted_logs = {}
        end_time = datetime.now()
        start_time = end_time - timedelta(minutes=time_range_minutes)
        
        for source_id in sources:
            if source_id not in self.log_sources:
                self.logger.warning(f"Unknown log source: {source_id}")
                continue
                
            config = self.log_sources[source_id]
            if not config['enabled']:
                self.logger.debug(f"Skipping disabled source: {source_id}")
                continue
            
            try:
                logs = self._extract_from_source(source_id, config, start_time, end_time)
                extracted_logs[source_id] = logs
                self.logger.info(f"Extracted {len(logs)} entries from {source_id}")
            except Exception as e:
                self.logger.error(f"Failed to extract from {source_id}: {e}")
                extracted_logs[source_id] = []
        
        return extracted_logs
    
    def _extract_from_source(self, source_id: str, config: Dict[str, Any], 
                           start_time: datetime, end_time: datetime) -> List[Dict[str, Any]]:
        """Extract logs from a specific source."""
        source_type = config['type']
        
        if source_type == 'windows_eventlog':
            return self._extract_windows_eventlog(config, start_time, end_time)
        elif source_type == 'file':
            return self._extract_from_file(config, start_time, end_time)
        elif source_type == 'process_monitor':
            return self._extract_process_info()
        elif source_type == 'network_monitor':
            return self._extract_network_info()
        elif source_type == 'filesystem_monitor':
            return self._extract_filesystem_info()
        else:
            self.logger.warning(f"Unknown source type: {source_type}")
            return []
    
    def _extract_windows_eventlog(self, config: Dict[str, Any], 
                                start_time: datetime, end_time: datetime) -> List[Dict[str, Any]]:
        """Extract logs from Windows Event Log."""
        if not WINDOWS_LOGS_AVAILABLE:
            return []
        
        logs = []
        log_name = config['log_name']
        
        try:
            # Open the event log
            hand = win32evtlog.OpenEventLog(None, log_name)
            flags = win32evtlog.EVENTLOG_BACKWARDS_READ | win32evtlog.EVENTLOG_SEQUENTIAL_READ
            
            total = win32evtlog.GetNumberOfEventLogRecords(hand)
            events = win32evtlog.ReadEventLog(hand, flags, 0)
            
            for event in events:
                # Convert Windows timestamp to datetime
                event_time = datetime.fromtimestamp(event.TimeGenerated.timestamp())
                
                # Filter by time range
                if start_time <= event_time <= end_time:
                    log_entry = {
                        'timestamp': event_time.isoformat(),
                        'source': log_name,
                        'event_id': event.EventID,
                        'event_type': self._get_event_type_name(event.EventType),
                        'category': event.EventCategory,
                        'computer': event.ComputerName,
                        'user': event.Sid,
                        'message': event.StringInserts[0] if event.StringInserts else '',
                        'raw_data': str(event.Data) if event.Data else ''
                    }
                    logs.append(log_entry)
            
            win32evtlog.CloseEventLog(hand)
            
        except Exception as e:
            self.logger.error(f"Error reading Windows event log {log_name}: {e}")
        
        return logs
    
    def _get_event_type_name(self, event_type: int) -> str:
        """Convert Windows event type number to name."""
        types = {
            win32con.EVENTLOG_ERROR_TYPE: "ERROR",
            win32con.EVENTLOG_WARNING_TYPE: "WARNING", 
            win32con.EVENTLOG_INFORMATION_TYPE: "INFORMATION",
            win32con.EVENTLOG_AUDIT_SUCCESS: "AUDIT_SUCCESS",
            win32con.EVENTLOG_AUDIT_FAILURE: "AUDIT_FAILURE"
        }
        return types.get(event_type, "UNKNOWN")
    
    def _extract_from_file(self, config: Dict[str, Any], 
                         start_time: datetime, end_time: datetime) -> List[Dict[str, Any]]:
        """Extract logs from a file."""
        logs = []
        file_path = config['path']
        
        try:
            # Get last extraction time for this file
            last_pos = self.last_extraction_time.get(file_path, 0)
            
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                f.seek(last_pos)
                lines = f.readlines()
                
                # Update position for next extraction
                self.last_extraction_time[file_path] = f.tell()
                
                for line in lines:
                    line = line.strip()
                    if line:
                        log_entry = {
                            'timestamp': datetime.now().isoformat(),
                            'source': file_path,
                            'message': line,
                            'type': 'file_log'
                        }
                        logs.append(log_entry)
                        
        except Exception as e:
            self.logger.error(f"Error reading file {file_path}: {e}")
        
        return logs
    
    def _extract_process_info(self) -> List[Dict[str, Any]]:
        """Extract information about running processes."""
        logs = []
        
        try:
            if self.system == "Windows":
                # Use wmic for Windows
                result = subprocess.run([
                    'wmic', 'process', 'get', 
                    'ProcessId,ParentProcessId,Name,CommandLine,CreationDate',
                    '/format:csv'
                ], capture_output=True, text=True, timeout=30)
                
                if result.returncode == 0:
                    lines = result.stdout.strip().split('\n')[1:]  # Skip header
                    for line in lines:
                        if line.strip():
                            parts = line.split(',')
                            if len(parts) >= 5:
                                log_entry = {
                                    'timestamp': datetime.now().isoformat(),
                                    'source': 'process_monitor',
                                    'type': 'process_info',
                                    'process_id': parts[3],
                                    'parent_id': parts[2],
                                    'name': parts[1],
                                    'command_line': parts[0],
                                    'creation_date': parts[4]
                                }
                                logs.append(log_entry)
            else:
                # Use ps for Linux/Unix
                result = subprocess.run([
                    'ps', 'aux'
                ], capture_output=True, text=True, timeout=30)
                
                if result.returncode == 0:
                    lines = result.stdout.strip().split('\n')[1:]  # Skip header
                    for line in lines:
                        parts = line.split()
                        if len(parts) >= 11:
                            log_entry = {
                                'timestamp': datetime.now().isoformat(),
                                'source': 'process_monitor',
                                'type': 'process_info',
                                'user': parts[0],
                                'pid': parts[1],
                                'cpu': parts[2],
                                'memory': parts[3],
                                'command': ' '.join(parts[10:])
                            }
                            logs.append(log_entry)
                            
        except Exception as e:
            self.logger.error(f"Error extracting process info: {e}")
        
        return logs
    
    def _extract_network_info(self) -> List[Dict[str, Any]]:
        """Extract network connection information."""
        logs = []
        
        try:
            if self.system == "Windows":
                # Use netstat for Windows
                result = subprocess.run([
                    'netstat', '-ano'
                ], capture_output=True, text=True, timeout=30)
            else:
                # Use netstat for Linux/Unix
                result = subprocess.run([
                    'netstat', '-tulnp'
                ], capture_output=True, text=True, timeout=30)
            
            if result.returncode == 0:
                lines = result.stdout.strip().split('\n')[2:]  # Skip headers
                for line in lines:
                    parts = line.split()
                    if len(parts) >= 4:
                        log_entry = {
                            'timestamp': datetime.now().isoformat(),
                            'source': 'network_monitor',
                            'type': 'network_connection',
                            'protocol': parts[0],
                            'local_address': parts[1],
                            'foreign_address': parts[2],
                            'state': parts[3] if len(parts) > 3 else 'UNKNOWN'
                        }
                        
                        if len(parts) > 4:
                            log_entry['pid'] = parts[4]
                            
                        logs.append(log_entry)
                        
        except Exception as e:
            self.logger.error(f"Error extracting network info: {e}")
        
        return logs
    
    def _extract_filesystem_info(self) -> List[Dict[str, Any]]:
        """Extract recent file system activity."""
        logs = []
        
        try:
            # Get recently modified files in common directories
            search_dirs = []
            
            if self.system == "Windows":
                search_dirs = [
                    "C:\\Windows\\System32",
                    "C:\\Users",
                    "C:\\Program Files",
                    "C:\\Temp"
                ]
            else:
                search_dirs = [
                    "/var/log",
                    "/tmp",
                    "/home",
                    "/etc"
                ]
            
            cutoff_time = time.time() - 300  # Last 5 minutes
            
            for search_dir in search_dirs:
                if os.path.exists(search_dir):
                    try:
                        for root, dirs, files in os.walk(search_dir):
                            # Limit depth to avoid too much scanning
                            dirs[:] = dirs[:5]  # Limit subdirectories
                            
                            for file in files[:10]:  # Limit files per directory
                                file_path = os.path.join(root, file)
                                try:
                                    stat = os.stat(file_path)
                                    if stat.st_mtime > cutoff_time:
                                        log_entry = {
                                            'timestamp': datetime.fromtimestamp(stat.st_mtime).isoformat(),
                                            'source': 'filesystem_monitor',
                                            'type': 'file_modification',
                                            'path': file_path,
                                            'size': stat.st_size,
                                            'modified_time': datetime.fromtimestamp(stat.st_mtime).isoformat()
                                        }
                                        logs.append(log_entry)
                                except (OSError, PermissionError):
                                    continue
                    except (OSError, PermissionError):
                        continue
                        
        except Exception as e:
            self.logger.error(f"Error extracting filesystem info: {e}")
        
        return logs
    
    def format_logs_for_analysis(self, extracted_logs: Dict[str, List[Dict[str, Any]]]) -> str:
        """Format extracted logs for sending to ForensIQ API."""
        formatted_logs = []
        
        for source_id, logs in extracted_logs.items():
            for log_entry in logs:
                # Create a formatted log line
                timestamp = log_entry.get('timestamp', datetime.now().isoformat())
                source = log_entry.get('source', source_id)
                log_type = log_entry.get('type', 'unknown')
                message = log_entry.get('message', '')
                
                # Build additional context
                context = []
                for key, value in log_entry.items():
                    if key not in ['timestamp', 'source', 'type', 'message']:
                        context.append(f"{key}={value}")
                
                context_str = " ".join(context) if context else ""
                
                formatted_line = f"{timestamp} [{source}] {log_type.upper()}: {message} {context_str}".strip()
                formatted_logs.append(formatted_line)
        
        return "\n".join(formatted_logs)
    
    def get_system_summary(self) -> Dict[str, Any]:
        """Get a summary of the current system state."""
        return {
            'system': self.system,
            'hostname': platform.node(),
            'platform': platform.platform(),
            'available_sources': len([s for s in self.log_sources.values() if s['enabled']]),
            'extraction_time': datetime.now().isoformat()
        }
