#!/usr/bin/env python

"""Utility functions for the filter module."""

import logging
from typing import List, Optional

class InMemoryHandler(logging.Handler):
    """A logging handler that stores log records in memory."""
    
    def __init__(self, capacity: Optional[int] = None):
        """Initialize the handler with optional capacity limit.
        
        Parameters
        ----------
        capacity : Optional[int]
            Maximum number of log records to store. If None, no limit is applied.
        """
        super().__init__()
        self.capacity = capacity
        self.logs: List[str] = []
        
    def emit(self, record: logging.LogRecord) -> None:
        """Store the log record in memory.
        
        Parameters
        ----------
        record : logging.LogRecord
            The log record to store
        """
        log_entry = self.format(record)
        self.logs.append(log_entry)
        if self.capacity and len(self.logs) > self.capacity:
            self.logs.pop(0)
            
    def get_logs(self, log_type: str = 'all') -> List[str]:
        """Get all stored log records.

        Parameters
        ----------
        log_type : str
            log type to get
            possible values are 'all', 'info', 'debug', 'warning', 'error'
            (default: 'all')

        Returns
        -------
        List[str]
            List of formatted log records
        """
        if log_type == 'all':
            return self.logs.copy()
        elif log_type == 'info':
            return [log for log in self.logs if log[22:].startswith('INFO')]
        elif log_type == 'debug':
            return [log for log in self.logs if log[22:].startswith('DEBUG')]
        elif log_type == 'warning':
            return [log for log in self.logs if log[22:].startswith('WARNING')]
        elif log_type == 'error':
            return [log for log in self.logs if log[22:].startswith('ERROR')]
        else:
            raise ValueError(f"Invalid log type: {log_type}")
    
    def clear(self) -> None:
        """Clear all stored log records."""
        self.logs.clear()

SVO_BASE_URL = 'http://svo2.cab.inta-csic.es/theory/fps/fps.php?'

SVO_FILTER_URL = SVO_BASE_URL + 'ID='
SVO_META_URL = SVO_BASE_URL + 'FORMAT=metadata'
