"""
ConfigLoader - Loads and validates YAML configuration files for SFIS ingestion drivers
"""
import os
import yaml
from typing import Dict, List, Any


class ConfigLoader:
    """
    Loads and validates YAML configuration files for ingestion drivers
    """
    
    def load(self, file_path: str) -> Dict[str, Any]:
        """
        Load a single configuration file
        
        Args:
            file_path: Path to the YAML configuration file
            
        Returns:
            Configuration dictionary
            
        Raises:
            FileNotFoundError: If the file doesn't exist
            yaml.YAMLError: If the YAML is malformed
        """
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"Configuration file not found: {file_path}")
        
        with open(file_path, 'r', encoding='utf-8') as f:
            config = yaml.safe_load(f)
        
        return config
    
    def load_all_from_directory(self, directory_path: str) -> List[Dict[str, Any]]:
        """
        Load all YAML configuration files from a directory
        
        Args:
            directory_path: Path to directory containing YAML files
            
        Returns:
            List of configuration dictionaries
        """
        configs = []
        
        if not os.path.isdir(directory_path):
            raise NotADirectoryError(f"Not a directory: {directory_path}")
        
        # Find all YAML files
        for filename in os.listdir(directory_path):
            if filename.endswith(('.yaml', '.yml')):
                file_path = os.path.join(directory_path, filename)
                try:
                    config = self.load(file_path)
                    configs.append(config)
                except (yaml.YAMLError, FileNotFoundError) as e:
                    # Log error but continue processing other files
                    print(f"Warning: Failed to load {filename}: {e}")
        
        return configs
    
    def validate(self, config: Dict[str, Any]) -> bool:
        """
        Validate a configuration dictionary
        
        Args:
            config: Configuration dictionary to validate
            
        Returns:
            True if valid, False otherwise
        """
        required_fields = ['institution', 'driver', 'file_pattern', 'columns']
        
        # Check required top-level fields
        for field in required_fields:
            if field not in config:
                return False
        
        # Validate columns configuration
        columns = config.get('columns', {})
        required_columns = ['date', 'narration', 'amount']
        
        for col in required_columns:
            if col not in columns:
                return False
        
        return True
