"""
Core evaluation logic for LLM Cultural Awareness
"""

import numpy as np
from typing import Dict, List, Any, Tuple
from openai import OpenAI
import config
from data_loader import DataLoader

class CulturalEvaluator:
    """Handles cultural dimension evaluation using OpenAI models"""
    
    def __init__(self, api_key: str = None):
        """
        Initialize the evaluator
        
        Args:
            api_key: OpenAI API key (defaults to config value)
        """
        self.client = OpenAI(api_key=api_key or config.OPENAI_API_KEY)
        self.data_loader = DataLoader()
        
    def _extract_question_components(self, question: Any, language: str) -> Tuple[str, str, str]:
        """
        Extract question components based on language
        
        Args:
            question: Question data (dict or other format)
            language: Target language
            
        Returns:
            Tuple of (question_text, option1, option2)
        """
        keys = config.LANGUAGE_KEYS.get(language, config.LANGUAGE_KEYS["English"])
        
        if isinstance(question, dict):
            q = question.get(keys['question'], list(question.values())[0])
            o1 = question.get(keys['option1'], list(question.values())[1])
            o2 = question.get(keys['option2'], list(question.values())[2])
        else:
            # Handle unexpected format
            question_values = list(question.values()) if hasattr(question, 'values') else [str(question)]
            q = question_values[0] if len(question_values) > 0 else "Unknown question"
            o1 = question_values[1] if len(question_values) > 1 else "Option 1"
            o2 = question_values[2] if len(question_values) > 2 else "Option 2"
            
        return str(q), str(o1), str(o2)
    
    def _get_model_response(self, prompt: str, language: str, repetitions: int = 3) -> List[str]:
        """
        Get model responses for a given prompt
        
        Args:
            prompt: The prompt to send to the model
            language: Target language
            repetitions: Number of times to repeat the query
            
        Returns:
            List of model responses
        """
        responses = []
        
        for _ in range(repetitions):
            try:
                response = self.client.chat.completions.create(
                    model=config.MODEL_NAME,
                    messages=[
                        {
                            "role": "system", 
                            "content": f"You are answering questions in {language}. Choose either 'Option 1' or 'Option 2' based on your cultural understanding."
                        },
                        {"role": "user", "content": prompt}
                    ],
                    max_tokens=config.MAX_TOKENS,
                    temperature=config.DEFAULT_TEMPERATURE
                )
                answer = response.choices[0].message.content.strip()
                responses.append(answer)
                
            except Exception as e:
                print(f"Error getting model response: {e}")
                responses.append("Option 1")  # Default fallback
                
        return responses
    
    def _calculate_dimension_score(self, responses: List[str], dimension: str) -> float:
        """
        Calculate cultural dimension score based on responses
        
        Args:
            responses: List of model responses
            dimension: Cultural dimension being evaluated
            
        Returns:
            Proportion score between 0 and 1
        """
        if dimension in config.HIGH_SCORING_DIMENSIONS:
            target_option = "Option 1"
        else:  # LOW_SCORING_DIMENSIONS
            target_option = "Option 2"
        
        # Count responses matching the target option
        matching_responses = sum(1 for response in responses if target_option in response)
        
        return matching_responses / len(responses) if responses else 0.5
    
    def compute_cultural_score(self, questions: List[Any], language: str, dimension: str, 
                             repetitions: int = None, use_cache: bool = True) -> float:
        """
        Compute cultural dimension score for a set of questions
        
        Args:
            questions: List of question dictionaries
            language: Target language
            dimension: Cultural dimension being evaluated
            repetitions: Number of repetitions per question (defaults to config value)
            use_cache: Whether to use cached results if available
            
        Returns:
            Overall cultural dimension score
        """
        repetitions = repetitions or config.DEFAULT_REPETITIONS
        
        # Check cache first
        if use_cache:
            cached_scores = self.data_loader.load_cached_scores(config.CACHE_FILE)
            if (language in cached_scores and 
                dimension in cached_scores[language]):
                print(f"Using cached score for {language} - {dimension}")
                return cached_scores[language][dimension]
        
        print(f"Computing score for {language} - {dimension}...")
        print(f"Processing {len(questions)} questions with {repetitions} repetitions each")
        
        scores = []
        
        for i, question in enumerate(questions):
            try:
                # Extract question components
                q, o1, o2 = self._extract_question_components(question, language)
                
                # Construct prompt
                prompt = f"Question: {q}\nOption 1: {o1}\nOption 2: {o2}\n\nPlease choose either 'Option 1' or 'Option 2'."
                
                # Get model responses
                responses = self._get_model_response(prompt, language, repetitions)
                
                # Calculate score for this question
                question_score = self._calculate_dimension_score(responses, dimension)
                scores.append(question_score)
                
            except Exception as e:
                print(f"Error processing question {i}: {e}")
                scores.append(0.5)  # Neutral score for failed questions
        
        # Calculate overall score using weighted average (equal weights)
        if scores:
            overall_score = np.mean(scores)
        else:
            overall_score = 0.5  # Default neutral score
        
        # Update cache
        if use_cache:
            cached_scores = self.data_loader.load_cached_scores(config.CACHE_FILE)
            if language not in cached_scores:
                cached_scores[language] = {}
            cached_scores[language][dimension] = overall_score
            self.data_loader.save_cached_scores(cached_scores, config.CACHE_FILE)
        
        print(f"Computed score for {language} - {dimension}: {overall_score:.4f}")
        return overall_score
    
    @staticmethod
    def compute_similarity_score(ground_truth_scores: List[float], 
                               computed_scores: List[float]) -> float:
        """
        Compute similarity score between ground truth and computed scores
        Based on Equation 3 from the research paper
        
        Args:
            ground_truth_scores: List of ground truth scores
            computed_scores: List of computed scores
            
        Returns:
            Similarity score between 0 and 1
        """
        if len(ground_truth_scores) != len(computed_scores):
            raise ValueError("Ground truth and computed scores must have same length")
        
        sum_of_squares = np.sum([(gt - comp) ** 2 
                                for gt, comp in zip(ground_truth_scores, computed_scores)])
        similarity = 1 / (1 + np.sqrt(sum_of_squares))
        
        return similarity