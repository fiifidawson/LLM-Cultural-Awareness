"""
Utility functions for LLM Cultural Awareness Evaluation
"""

import os
import json
import time
from typing import Dict, Any, List, Optional
from pathlib import Path

class ValidationError(Exception):
    """Custom exception for validation errors"""
    pass

class FileUtils:
    """File operation utilities"""
    
    @staticmethod
    def ensure_directory_exists(path: str) -> None:
        """
        Ensure a directory exists, create if it doesn't
        
        Args:
            path: Directory path to check/create
        """
        Path(path).mkdir(parents=True, exist_ok=True)
    
    @staticmethod
    def validate_file_exists(path: str, file_type: str = "file") -> bool:
        """
        Validate that a file exists
        
        Args:
            path: Path to check
            file_type: Type description for error messages
            
        Returns:
            True if file exists
            
        Raises:
            ValidationError: If file doesn't exist
        """
        if not os.path.exists(path):
            raise ValidationError(f"{file_type} not found: {path}")
        return True
    
    @staticmethod
    def get_file_size(path: str) -> int:
        """Get file size in bytes"""
        return os.path.getsize(path) if os.path.exists(path) else 0
    
    @staticmethod
    def backup_file(path: str) -> str:
        """
        Create a backup of a file with timestamp
        
        Args:
            path: Original file path
            
        Returns:
            Path to backup file
        """
        if not os.path.exists(path):
            return path
        
        timestamp = time.strftime("%Y%m%d_%H%M%S")
        backup_path = f"{path}.backup_{timestamp}"
        
        try:
            import shutil
            shutil.copy2(path, backup_path)
            return backup_path
        except Exception as e:
            print(f"Warning: Could not create backup: {e}")
            return path

class DataValidator:
    """Data validation utilities"""
    
    @staticmethod
    def validate_question_format(question: Any, language: str) -> bool:
        """
        Validate that a question has the correct format
        
        Args:
            question: Question data to validate
            language: Target language
            
        Returns:
            True if valid format
        """
        if not isinstance(question, dict):
            return False
        
        # Check if question has required keys for the language
        from config import LANGUAGE_KEYS
        required_keys = set(LANGUAGE_KEYS.get(language, LANGUAGE_KEYS["English"]).values())
        question_keys = set(question.keys())
        
        # Allow for some flexibility in key matching
        return len(question_keys.intersection(required_keys)) >= 2
    
    @staticmethod
    def validate_dimension_data(data: List[Any], dimension: str, language: str) -> Dict[str, Any]:
        """
        Validate dimension data completeness
        
        Args:
            data: List of questions for the dimension
            dimension: Cultural dimension name
            language: Target language
            
        Returns:
            Validation report dictionary
        """
        report = {
            'dimension': dimension,
            'language': language,
            'total_questions': len(data),
            'valid_questions': 0,
            'invalid_questions': 0,
            'issues': []
        }
        
        for i, question in enumerate(data):
            if DataValidator.validate_question_format(question, language):
                report['valid_questions'] += 1
            else:
                report['invalid_questions'] += 1
                report['issues'].append(f"Question {i}: Invalid format")
        
        if report['invalid_questions'] > 0:
            print(f"Warning: {dimension} ({language}) has {report['invalid_questions']} invalid questions")
        
        return report

class ScoreUtils:
    """Score calculation and analysis utilities"""
    
    @staticmethod
    def normalize_score(score: float, min_val: float = 0.0, max_val: float = 1.0) -> float:
        """
        Normalize score to specified range
        
        Args:
            score: Score to normalize
            min_val: Minimum value in range
            max_val: Maximum value in range
            
        Returns:
            Normalized score
        """
        return max(min_val, min(max_val, score))
    
    @staticmethod
    def calculate_confidence_interval(scores: List[float], confidence: float = 0.95) -> Dict[str, float]:
        """
        Calculate confidence interval for a list of scores
        
        Args:
            scores: List of score values
            confidence: Confidence level (default 0.95)
            
        Returns:
            Dictionary with mean, lower_bound, upper_bound
        """
        if not scores:
            return {'mean': 0.0, 'lower_bound': 0.0, 'upper_bound': 0.0}
        
        import numpy as np
        
        mean_score = np.mean(scores)
        std_error = np.std(scores, ddof=1) / np.sqrt(len(scores)) if len(scores) > 1 else 0
        
        # Use t-distribution for small samples
        if len(scores) < 30:
            from scipy import stats
            t_value = stats.t.ppf((1 + confidence) / 2, len(scores) - 1)
        else:
            t_value = 1.96  # Approximation for large samples
        
        margin_error = t_value * std_error
        
        return {
            'mean': float(mean_score),
            'lower_bound': float(mean_score - margin_error),
            'upper_bound': float(mean_score + margin_error),
            'margin_error': float(margin_error)
        }
    
    @staticmethod
    def calculate_effect_size(group1_scores: List[float], group2_scores: List[float]) -> float:
        """
        Calculate Cohen's d effect size between two groups
        
        Args:
            group1_scores: First group scores
            group2_scores: Second group scores
            
        Returns:
            Effect size (Cohen's d)
        """
        if not group1_scores or not group2_scores:
            return 0.0
        
        import numpy as np
        
        mean1, mean2 = np.mean(group1_scores), np.mean(group2_scores)
        std1, std2 = np.std(group1_scores, ddof=1), np.std(group2_scores, ddof=1)
        
        # Pooled standard deviation
        n1, n2 = len(group1_scores), len(group2_scores)
        pooled_std = np.sqrt(((n1 - 1) * std1**2 + (n2 - 1) * std2**2) / (n1 + n2 - 2))
        
        if pooled_std == 0:
            return 0.0
        
        return (mean1 - mean2) / pooled_std

class LoggingUtils:
    """Logging and progress tracking utilities"""
    
    @staticmethod
    def create_progress_logger(total_steps: int, description: str = "Processing"):
        """
        Create a simple progress logger
        
        Args:
            total_steps: Total number of steps
            description: Description of the process
            
        Returns:
            Progress logger function
        """
        def log_progress(current_step: int, extra_info: str = ""):
            percentage = (current_step / total_steps) * 100
            bar_length = 50
            filled_length = int(bar_length * current_step // total_steps)
            bar = '█' * filled_length + '-' * (bar_length - filled_length)
            
            print(f'\r{description}: |{bar}| {current_step}/{total_steps} '
                  f'({percentage:.1f}%) {extra_info}', end='', flush=True)
            
            if current_step == total_steps:
                print()  # New line when complete
        
        return log_progress
    
    @staticmethod
    def log_evaluation_start(language: str, dimension: str, question_count: int):
        """Log the start of an evaluation"""
        print(f"\n🔄 Starting evaluation: {language} - {dimension}")
        print(f"   Questions to process: {question_count}")
    
    @staticmethod
    def log_evaluation_complete(language: str, dimension: str, score: float, duration: float):
        """Log the completion of an evaluation"""
        print(f"✅ Completed: {language} - {dimension}")
        print(f"   Score: {score:.4f}, Duration: {duration:.1f}s")

class CacheUtils:
    """Cache management utilities"""
    
    @staticmethod
    def is_cache_valid(cache_file: str, max_age_hours: int = 24) -> bool:
        """
        Check if cache file is valid based on age
        
        Args:
            cache_file: Path to cache file
            max_age_hours: Maximum age in hours
            
        Returns:
            True if cache is valid
        """
        if not os.path.exists(cache_file):
            return False
        
        file_age = time.time() - os.path.getmtime(cache_file)
        max_age_seconds = max_age_hours * 3600
        
        return file_age < max_age_seconds
    
    @staticmethod
    def clear_cache(cache_file: str) -> bool:
        """
        Clear cache file
        
        Args:
            cache_file: Path to cache file
            
        Returns:
            True if successfully cleared
        """
        try:
            if os.path.exists(cache_file):
                os.remove(cache_file)
                print(f"Cache cleared: {cache_file}")
            return True
        except Exception as e:
            print(f"Error clearing cache: {e}")
            return False
    
    @staticmethod
    def get_cache_info(cache_file: str) -> Dict[str, Any]:
        """
        Get cache file information
        
        Args:
            cache_file: Path to cache file
            
        Returns:
            Dictionary with cache information
        """
        if not os.path.exists(cache_file):
            return {'exists': False}
        
        stat = os.stat(cache_file)
        
        try:
            with open(cache_file, 'r') as f:
                cache_data = json.load(f)
                entry_count = sum(len(lang_data) for lang_data in cache_data.values())
        except:
            entry_count = 0
        
        return {
            'exists': True,
            'size_bytes': stat.st_size,
            'modified_time': time.ctime(stat.st_mtime),
            'entry_count': entry_count
        }