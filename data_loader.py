"""
Data loading utilities for LLM Cultural Awareness Evaluation
"""

import json
import os
from typing import Dict, Any
from pathlib import Path

class DataLoader:
    """Handles loading and saving of JSON data files"""
    
    @staticmethod
    def read_json_files(directory: str) -> Dict[str, Any]:
        """
        Read all JSON files from a directory
        
        Args:
            directory: Path to directory containing JSON files
            
        Returns:
            Dictionary mapping dimension names to their data
        """
        json_data = {}
        
        if not os.path.exists(directory):
            print(f"Warning: Directory {directory} does not exist")
            return json_data
            
        for filename in os.listdir(directory):
            if filename.endswith('.json'):
                try:
                    dimension = filename.split('_')[0]  # Extract dimension from filename
                    file_path = os.path.join(directory, filename)
                    
                    with open(file_path, 'r', encoding='utf-8') as file:
                        json_data[dimension] = json.load(file)
                        
                except Exception as e:
                    print(f"Error reading {filename}: {e}")
                    continue
                    
        return json_data
    
    @staticmethod
    def load_cached_scores(cache_file: str) -> Dict[str, Any]:
        """
        Load cached scores from JSON file
        
        Args:
            cache_file: Path to cache file
            
        Returns:
            Dictionary of cached scores or empty dict if file doesn't exist
        """
        if os.path.exists(cache_file):
            try:
                with open(cache_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                print(f"Error loading cache file: {e}")
                return {}
        return {}
    
    @staticmethod
    def save_cached_scores(scores: Dict[str, Any], cache_file: str) -> None:
        """
        Save scores to cache file
        
        Args:
            scores: Dictionary of scores to save
            cache_file: Path to cache file
        """
        try:
            # Ensure cache directory exists
            os.makedirs(os.path.dirname(cache_file), exist_ok=True)
            
            with open(cache_file, 'w', encoding='utf-8') as f:
                json.dump(scores, f, indent=2, ensure_ascii=False)
                
        except Exception as e:
            print(f"Error saving cache file: {e}")
    
    @staticmethod
    def save_results(results: Dict[str, Any], output_file: str) -> None:
        """
        Save final results to JSON file
        
        Args:
            results: Dictionary of results to save
            output_file: Path to output file
        """
        try:
            # Ensure output directory exists
            os.makedirs(os.path.dirname(output_file), exist_ok=True)
            
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(results, f, indent=2, ensure_ascii=False)
                
            print(f"Results saved to: {output_file}")
            
        except Exception as e:
            print(f"Error saving results file: {e}")
    
    @staticmethod
    def load_all_language_data(language_paths: Dict[str, str]) -> Dict[str, Dict[str, Any]]:
        """
        Load data for all languages
        
        Args:
            language_paths: Dictionary mapping language names to their data paths
            
        Returns:
            Dictionary mapping language names to their loaded data
        """
        translations = {}
        
        for language, path in language_paths.items():
            print(f"Loading {language} data from {path}")
            translations[language] = DataLoader.read_json_files(path)
            
            if translations[language]:
                print(f"Loaded {len(translations[language])} dimension files for {language}")
            else:
                print(f"Warning: No data loaded for {language}")
                
        return translations