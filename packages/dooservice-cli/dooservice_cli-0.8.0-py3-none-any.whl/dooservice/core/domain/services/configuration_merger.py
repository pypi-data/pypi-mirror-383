"""Service for merging multiple configuration dictionaries."""

from typing import Any, Dict, List


class ConfigurationMerger:
    """Service for deep merging configuration dictionaries."""

    def merge(self, base: Dict[str, Any], override: Dict[str, Any]) -> Dict[str, Any]:
        """Deep merge two configuration dictionaries.

        Args:
            base: Base configuration dictionary
            override: Override configuration dictionary

        Returns:
            Merged configuration dictionary
        """
        result = base.copy()

        for key, value in override.items():
            if key in result:
                # If both values are dictionaries, merge them recursively
                if isinstance(result[key], dict) and isinstance(value, dict):
                    result[key] = self.merge(result[key], value)
                # If both values are lists, concatenate them
                elif isinstance(result[key], list) and isinstance(value, list):
                    result[key] = self._merge_lists(result[key], value)
                else:
                    # Override with new value
                    result[key] = value
            else:
                # Add new key
                result[key] = value

        return result

    def merge_multiple(self, configurations: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Merge multiple configuration dictionaries in order.

        Args:
            configurations: List of configuration dictionaries to merge

        Returns:
            Merged configuration dictionary
        """
        if not configurations:
            return {}

        result = configurations[0].copy()
        for config in configurations[1:]:
            result = self.merge(result, config)

        return result

    def _merge_lists(self, base: List[Any], override: List[Any]) -> List[Any]:
        """Merge two lists by concatenating unique values.

        Args:
            base: Base list
            override: Override list

        Returns:
            Merged list with unique values
        """
        # For simple types, remove duplicates
        if all(isinstance(item, (str, int, float, bool)) for item in base + override):
            seen = set()
            result = []
            for item in base + override:
                if item not in seen:
                    seen.add(item)
                    result.append(item)
            return result

        # For complex types, just concatenate
        return base + override
