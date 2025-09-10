"""
Main evaluation script for LLM Cultural Awareness
Based on the research paper: "Evaluating Cultural Awareness of LLMs for Yoruba, Malayalam, and English"
"""

import os
from typing import Dict, Any

# Import custom modules
import config
from data_loader import DataLoader
from cultural_evaluator import CulturalEvaluator
from results_analyzer import ResultsAnalyzer

def setup_environment():
    """Setup the evaluation environment"""
    print("Setting up evaluation environment...")
    
    # Verify data directories exist
    for language, path in config.LANGUAGE_PATHS.items():
        if not os.path.exists(path):
            print(f"⚠️  Warning: Data directory for {language} not found: {path}")
            print(f"    Please ensure your data is placed in the correct directory structure")
        else:
            print(f"✓ {language} data directory found")
    
    # Verify API key
    if config.OPENAI_API_KEY == 'your-api-key-here':
        print("⚠️  Warning: Please set your OpenAI API key in config.py or environment variables")
        return False
    
    print("✓ Configuration loaded")
    return True

def load_evaluation_data() -> Dict[str, Dict[str, Any]]:
    """Load all evaluation data"""
    print("\nLoading evaluation data...")
    
    data_loader = DataLoader()
    translations = data_loader.load_all_language_data(config.LANGUAGE_PATHS)
    
    # Validate loaded data
    total_dimensions = 0
    for language, data in translations.items():
        dimensions_count = len(data)
        total_dimensions += dimensions_count
        print(f"  {language}: {dimensions_count} dimension files")
    
    print(f"✓ Total dimension files loaded: {total_dimensions}")
    
    if total_dimensions == 0:
        print("⚠️  No data loaded. Please check your data paths in config.py")
        return {}
    
    return translations

def run_cultural_evaluation(translations: Dict[str, Dict[str, Any]]) -> Dict[str, Dict[str, float]]:
    """Run the cultural evaluation for all languages and dimensions"""
    print("\nRunning cultural evaluation...")
    
    evaluator = CulturalEvaluator()
    computed_scores = {}
    
    # Get available dimensions across all languages
    all_dimensions = set()
    for lang_data in translations.values():
        all_dimensions.update(lang_data.keys())
    
    print(f"Available dimensions: {sorted(all_dimensions)}")
    
    # Evaluate each language
    for language in translations.keys():
        print(f"\n{'='*60}")
        print(f"EVALUATING {language.upper()}")
        print(f"{'='*60}")
        
        computed_scores[language] = {}
        
        for dimension_file, questions in translations[language].items():
            # Remove .json extension to get dimension name
            dimension = dimension_file.replace('.json', '')
            
            try:
                score = evaluator.compute_cultural_score(
                    questions=questions,
                    language=language,
                    dimension=dimension,
                    repetitions=config.DEFAULT_REPETITIONS
                )
                computed_scores[language][dimension] = score
                
            except Exception as e:
                print(f"Error evaluating {language} - {dimension}: {e}")
                computed_scores[language][dimension] = 0.5  # Default neutral score
    
    return computed_scores

def analyze_results(computed_scores: Dict[str, Dict[str, float]]) -> Dict[str, Any]:
    """Analyze and report the evaluation results"""
    print(f"\n{'='*80}")
    print("ANALYZING RESULTS")
    print(f"{'='*80}")
    
    analyzer = ResultsAnalyzer()
    all_results = {}
    
    # Analyze each language
    for language in computed_scores.keys():
        if language in config.GROUND_TRUTH_SCORES:
            results = analyzer.analyze_language_results(language, computed_scores[language])
            all_results[language] = results
        else:
            print(f"Warning: No ground truth data for {language}")
    
    # Generate comprehensive summary
    summary = analyzer.generate_summary_report(all_results)
    
    # Print dimension comparison table
    analyzer.print_dimension_comparison_table(all_results)
    
    return {
        'detailed_results': all_results,
        'summary': summary,
        'computed_scores': computed_scores,
        'ground_truth_scores': config.GROUND_TRUTH_SCORES
    }

def save_final_results(results: Dict[str, Any]) -> None:
    """Save the final evaluation results"""
    print(f"\n{'='*80}")
    print("SAVING RESULTS")
    print(f"{'='*80}")
    
    # Prepare results for saving
    final_results = {
        'model_evaluated': config.MODEL_NAME,
        'evaluation_parameters': {
            'repetitions_per_question': config.DEFAULT_REPETITIONS,
            'temperature': config.DEFAULT_TEMPERATURE,
            'max_tokens': config.MAX_TOKENS
        },
        'computed_scores': results['computed_scores'],
        'ground_truth_scores': results['ground_truth_scores'],
        'similarity_scores': {},
        'summary': results['summary']
    }
    
    # Extract similarity scores
    for language, lang_results in results['detailed_results'].items():
        if 'overall_similarity' in lang_results:
            final_results['similarity_scores'][language] = lang_results['overall_similarity']
    
    # Save to file
    data_loader = DataLoader()
    data_loader.save_results(final_results, config.RESULTS_FILE)
    
    print("✓ Results saved successfully")

def main():
    """Main evaluation function"""
    print("="*80)
    print("LLM CULTURAL AWARENESS EVALUATION")
    print("="*80)
    print("Based on: 'Evaluating Cultural Awareness of LLMs for Yoruba, Malayalam, and English'")
    print(f"Model: {config.MODEL_NAME}")
    print("="*80)
    
    try:
        # Setup environment
        if not setup_environment():
            return None
        
        # Load data
        translations = load_evaluation_data()
        if not translations:
            print("Evaluation terminated: No data available")
            return None
        
        # Run evaluation
        computed_scores = run_cultural_evaluation(translations)
        
        # Analyze results
        results = analyze_results(computed_scores)
        
        # Save results
        save_final_results(results)
        
        print("\n" + "="*80)
        print("EVALUATION COMPLETED SUCCESSFULLY")
        print("="*80)
        
        return results
        
    except KeyboardInterrupt:
        print("\nEvaluation interrupted by user")
        return None
    except Exception as e:
        print(f"\nEvaluation failed with error: {e}")
        import traceback
        traceback.print_exc()
        return None

if __name__ == "__main__":
    results = main()