"""
Description Auto-Complete Module
Provides smart suggestions based on expense history

Tracks description usage to provide auto-complete suggestions
as users type in expense dialogs.
"""

import json
import os
from typing import List, Dict, Optional
from datetime import datetime
from settings_manager import get_settings_manager


class DescriptionHistory:
    """
    Manage description history for auto-complete suggestions.
    
    Tracks which descriptions have been used, how frequently,
    and when they were last used to provide intelligent suggestions.
    """
    
    def __init__(self, file_path="description_history.json"):
        """
        Initialize description history manager.
        
        Args:
            file_path: Path to JSON file storing description history
        """
        self.file_path = file_path
        self.descriptions = []
        self.settings = get_settings_manager()
        self.load()
    
    def load(self):
        """Load description history from JSON file"""
        if os.path.exists(self.file_path):
            try:
                with open(self.file_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.descriptions = data.get('descriptions', [])
            except (json.JSONDecodeError, IOError):
                # If file is corrupted or can't be read, start fresh
                self.descriptions = []
        else:
            self.descriptions = []
    
    def save(self):
        """Save description history to JSON file"""
        try:
            data = {'descriptions': self.descriptions}
            with open(self.file_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
        except IOError:
            # Silently fail if we can't save (non-critical)
            pass
    
    def add_or_update(self, description: str, amount: float):
        """
        Add new description or update existing one with usage tracking.
        
        Args:
            description: Expense description text
            amount: Expense amount (stored for reference, not auto-filled)
        """
        # Normalize description (strip whitespace, case-insensitive matching)
        normalized = description.strip()
        if not normalized:
            return
        
        # Find existing entry (case-insensitive match)
        existing = next(
            (d for d in self.descriptions if d['text'].lower() == normalized.lower()),
            None
        )
        
        if existing:
            # Update existing entry
            existing['count'] += 1
            existing['last_used'] = datetime.now().strftime('%Y-%m-%d')
            existing['last_amount'] = amount  # Store for display hint only
        else:
            # Add new entry
            self.descriptions.append({
                'text': normalized,
                'count': 1,
                'last_used': datetime.now().strftime('%Y-%m-%d'),
                'last_amount': amount  # Store for display hint only
            })
        
        # Sort by count (most used first), then by last_used (recent first)
        # Note: last_used is a string in YYYY-MM-DD format, so we can't use unary minus on it
        # Sort by count descending first, then by last_used descending (newer dates are "greater" strings)
        self.descriptions.sort(
            key=lambda x: (-x['count'], x['last_used']),
            reverse=False
        )
        # The above gives us count descending, but last_used ascending. We need to fix the last_used order.
        # Group by count and re-sort each group by last_used descending
        current_count = None
        group_start = 0
        for i in range(len(self.descriptions)):
            desc = self.descriptions[i]
            if current_count is None:
                current_count = desc['count']
            elif desc['count'] != current_count:
                # End of current group - sort it by last_used descending
                self.descriptions[group_start:i] = sorted(
                    self.descriptions[group_start:i],
                    key=lambda x: x['last_used'],
                    reverse=True
                )
                group_start = i
                current_count = desc['count']
        # Sort the last group
        self.descriptions[group_start:] = sorted(
            self.descriptions[group_start:],
            key=lambda x: x['last_used'],
            reverse=True
        )
        
        # Keep only top N descriptions (limit memory usage)
        max_descriptions = self.settings.get(
            'AutoComplete', 'max_descriptions', 50, value_type=int
        )
        self.descriptions = self.descriptions[:max_descriptions]
        
        self.save()
    
    def get_suggestions(self, partial_text: str = "", limit: int = None) -> List[Dict]:
        """
        Get suggestions based on partial text input.
        
        Args:
            partial_text: Text user has typed so far (empty string = show all top)
            limit: Maximum number of suggestions to return
            
        Returns:
            List of matching descriptions (sorted by usage count, most used first)
            Each dict contains: text, count, last_used, last_amount
        """
        if limit is None:
            limit = self.settings.get(
                'AutoComplete', 'max_suggestions', 5, value_type=int
            )
        
        if not partial_text:
            # No text typed - return most frequently used descriptions
            return self.descriptions[:limit]
        
        # Case-insensitive prefix matching
        partial_lower = partial_text.lower().strip()
        matches = [
            d for d in self.descriptions
            if d['text'].lower().startswith(partial_lower)
        ]
        
        return matches[:limit]
    
    def should_show_on_focus(self) -> bool:
        """Check if auto-complete should show when field receives focus"""
        return self.settings.get(
            'AutoComplete', 'show_on_focus', True, value_type=bool
        )
    
    def get_min_chars(self) -> int:
        """Get minimum characters required before showing suggestions"""
        return self.settings.get(
            'AutoComplete', 'min_chars', 2, value_type=int
        )
    
    def clear_history(self):
        """Clear all description history (useful for privacy/reset)"""
        self.descriptions = []
        self.save()

