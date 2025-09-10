"""
Results analysis and reporting for LLM Cultural Awareness Evaluation
"""

from typing import Dict, List, Any
import config
from cultural_evaluator import CulturalEvaluator

class ResultsAnalyzer:
    """Handles analysis and reporting of evaluation results"""
    
    def __init__(self):
        self.ground_truth_scores = config.GROUND_TRUTH_SCORES
        
    def analyze_language_results(self, language: str, computed_scores: Dict[str, float]) -> Dict[str, Any]:
        """
        Analyze results for a specific language
        
        Args:
            language: Language name
            computed_scores: Dictionary of computed scores for each dimension
            
        Returns:
            Dictionary containing detailed analysis results
        """
        if language not in self.ground_truth_scores:
            print(f"Warning: No ground truth data available for {language}")
            return {}
        
        ground_truth = self.ground_truth_scores[language]
        results = {
            'language': language,
            'dimension_analysis': {},
            'overall_similarity': 0.0
        }
        
        print(f"\n{language.upper()} RESULTS:")
        print("-" * 50)
        
        # Analyze each dimension
        gt_scores = []
        comp_scores = []
        
        for dimension in config.CULTURAL_DIMENSIONS:
            if dimension in computed_scores and dimension in ground_truth:
                gt_val = ground_truth[dimension]
                comp_val = computed_scores[dimension]
                
                gt_scores.append(gt_val)
                comp_scores.append(comp_val)
                
                # Calculate individual similarity
                individual_similarity = 1 / (1 + abs(gt_val - comp_val))
                
                results['dimension_analysis'][dimension] = {
                    'ground_truth': gt_val,
                    'computed': comp_val,
                    'difference': abs(gt_val - comp_val),
                    'similarity': individual_similarity
                }
                
                print(f"{dimension:4s}: GT={gt_val:.3f}, Computed={comp_val:.3f}, "
                      f"Diff={abs(gt_val - comp_val):.3f}, Similarity={individual_similarity:.3f}")
        
        # Calculate overall similarity
        if gt_scores and comp_scores:
            overall_similarity = CulturalEvaluator.compute_similarity_score(gt_scores, comp_scores)
            results['overall_similarity'] = overall_similarity
            print(f"\nOverall Similarity Score: {overall_similarity:.4f}")
        
        return results
    
    def generate_summary_report(self, all_results: Dict[str, Dict[str, Any]]) -> Dict[str, Any]:
        """
        Generate a comprehensive summary report
        
        Args:
            all_results: Dictionary of results for all languages
            
        Returns:
            Summary report dictionary
        """
        summary = {
            'model_name': config.MODEL_NAME,
            'languages_evaluated': list(all_results.keys()),
            'dimensions_evaluated': config.CULTURAL_DIMENSIONS,
            'language_summaries': {},
            'overall_performance': {}
        }
        
        print("\n" + "="*80)
        print("COMPREHENSIVE EVALUATION SUMMARY")
        print("="*80)
        
        all_similarities = []
        
        for language, results in all_results.items():
            if results and 'overall_similarity' in results:
                similarity = results['overall_similarity']
                all_similarities.append(similarity)
                
                summary['language_summaries'][language] = {
                    'similarity_score': similarity,
                    'best_dimension': self._find_best_dimension(results),
                    'worst_dimension': self._find_worst_dimension(results),
                    'dimension_count': len(results.get('dimension_analysis', {}))
                }
                
                print(f"{language:12s}: Similarity = {similarity:.4f}")
        
        # Overall performance metrics
        if all_similarities:
            summary['overall_performance'] = {
                'mean_similarity': sum(all_similarities) / len(all_similarities),
                'min_similarity': min(all_similarities),
                'max_similarity': max(all_similarities),
                'std_similarity': self._calculate_std(all_similarities)
            }
            
            print(f"\nOverall Performance:")
            print(f"  Mean Similarity: {summary['overall_performance']['mean_similarity']:.4f}")
            print(f"  Min Similarity:  {summary['overall_performance']['min_similarity']:.4f}")
            print(f"  Max Similarity:  {summary['overall_performance']['max_similarity']:.4f}")
            print(f"  Std Deviation:   {summary['overall_performance']['std_similarity']:.4f}")
        
        return summary
    
    def _find_best_dimension(self, results: Dict[str, Any]) -> str:
        """Find the dimension with highest similarity"""
        if 'dimension_analysis' not in results:
            return "N/A"
        
        best_dim = None
        best_similarity = -1
        
        for dim, analysis in results['dimension_analysis'].items():
            if analysis['similarity'] > best_similarity:
                best_similarity = analysis['similarity']
                best_dim = dim
        
        return best_dim or "N/A"
    
    def _find_worst_dimension(self, results: Dict[str, Any]) -> str:
        """Find the dimension with lowest similarity"""
        if 'dimension_analysis' not in results:
            return "N/A"
        
        worst_dim = None
        worst_similarity = float('inf')
        
        for dim, analysis in results['dimension_analysis'].items():
            if analysis['similarity'] < worst_similarity:
                worst_similarity = analysis['similarity']
                worst_dim = dim
        
        return worst_dim or "N/A"
    
    def _calculate_std(self, values: List[float]) -> float:
        """Calculate standard deviation"""
        if len(values) <= 1:
            return 0.0
        
        mean = sum(values) / len(values)
        variance = sum((x - mean) ** 2 for x in values) / (len(values) - 1)
        return variance ** 0.5
    
    def print_dimension_comparison_table(self, all_results: Dict[str, Dict[str, Any]]) -> None:
        """Print a comparison table of all dimensions across languages"""
        print("\n" + "="*80)
        print("DIMENSION COMPARISON TABLE")
        print("="*80)
        
        # Header
        header = f"{'Dimension':>10s}"
        for language in all_results.keys():
            header += f"  {language:>8s}_GT  {language:>8s}_CP  {language:>8s}_SIM"
        print(header)
        print("-" * len(header))
        
        # Data rows
        for dimension in config.CULTURAL_DIMENSIONS:
            row = f"{dimension:>10s}"
            
            for language in all_results.keys():
                if (language in all_results and 
                    'dimension_analysis' in all_results[language] and
                    dimension in all_results[language]['dimension_analysis']):
                    
                    analysis = all_results[language]['dimension_analysis'][dimension]
                    gt = analysis['ground_truth']
                    cp = analysis['computed']
                    sim = analysis['similarity']
                    
                    row += f"     {gt:.3f}     {cp:.3f}     {sim:.3f}"
                else:
                    row += f"       N/A       N/A       N/A"
            
            print(row)