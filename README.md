# LLM Cultural Awareness Evaluation

This research evaluates the cultural awareness of Large Language Models (LLMs) across different languages.

**Note:** This repository contains a streamlined and modularized version of the original evaluation framework, which was initially  developed and  tested on Google Colab. The current  implementation has been restructured for better  maintainability, and readability while preserving all core functionality and achieving  identical results. 

Please note that results may differ  depending on the model version used or due to the inherent unpredictability of responses. Seen an error? Kindly create a PR❤️.

## Overview

The evaluation framework assesses how well LLMs understand and respond to cultural dimensions across three languages:
- **English**
- **Malayalam** 
- **Yoruba**

The framework evaluates six cultural dimensions based on Hofstede's cultural theory:
- **PDI** (Power Distance Index)
- **IDV** (Individualism vs Collectivism)
- **MAS** (Masculinity vs Femininity)
- **UAI** (Uncertainty Avoidance Index)
- **LTO** (Long-term vs Short-term Orientation)
- **IVR** (Indulgence vs Restraint)


## Installation

1. Clone or download the project files
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Set up your OpenAI API key (see Configuration section)

## Configuration

### API Key Setup
Set your OpenAI API key in one of the following ways:

**Option 1: Environment Variable**
```bash
export OPENAI_API_KEY="your-api-key-here"
```

**Option 2: Edit config.py**
```python
OPENAI_API_KEY = "your-api-key-here"
```

### Data Paths
Update the data paths in `config.py` to match your data location:

```python
LANGUAGE_PATHS = {
    "Malayalam": "/path/to/your/Malayalam/data",
    "Yoruba": "/path/to/your/Yoruba/data", 
    "English": "/path/to/your/English/data"
}
```

## Usage

### Basic Usage

Run the complete evaluation:
```python
python main.py
```

### Custom Evaluation

```python
from cultural_evaluator import CulturalEvaluator
from data_loader import DataLoader

# Initialize evaluator
evaluator = CulturalEvaluator(api_key="your-key")

# Load your data
loader = DataLoader()
data = loader.read_json_files("/path/to/data")

# Evaluate specific dimension
score = evaluator.compute_cultural_score(
    questions=data["PDI"],
    language="English",
    dimension="PDI",
    repetitions=3
)
```

## Data Format

The system expects JSON files containing cultural dimension questions in the following format:

```json
[
  {
    "Question": "Your question text here",
    "Option 1": "First option text",
    "Option 2": "Second option text"
  }
]
```

For non-English languages, use the appropriate keys:
- **Malayalam**: "ചോദ്യം", "ഓപ്ഷൻ 1", "ഓപ്ഷൻ 2"
- **Yoruba**: "Ibeere", "Aṣayan 1", "Aṣayan 2"

## Evaluation Process

1. **Data Loading**: Loads question sets for each cultural dimension and language
2. **Model Querying**: Sends questions to the LLM with cultural context
3. **Score Calculation**: Computes dimension scores based on response patterns
4. **Similarity Analysis**: Compares computed scores with ground truth cultural values
5. **Results Analysis**: Generates comprehensive reports and comparisons

## Scoring Methodology

### Cultural Dimension Scores
- Questions are asked multiple times (default: 3 repetitions)
- Responses are analyzed for cultural alignment
- Scores range from 0 to 1 for each dimension

### Similarity Score Calculation
Based on the research paper's methodology:
```
Similarity = 1 / (1 + √(Σ(ground_truth - computed)²))
```

## Output

The evaluation generates:

1. **Console Output**: Real-time progress and results
2. **Cached Scores**: Stored in JSON for efficient re-runs
3. **Final Results**: Comprehensive analysis saved to file


## Customization

### Adding New Languages
1. Add language data path to `config.py`
2. Add language keys mapping to `LANGUAGE_KEYS`
3. Add ground truth scores to `GROUND_TRUTH_SCORES`

### Adding New Dimensions
1. Add dimension to `CULTURAL_DIMENSIONS`
2. Classify as high/low scoring in `HIGH_SCORING_DIMENSIONS` or `LOW_SCORING_DIMENSIONS`
3. Update ground truth scores

### Modifying Evaluation Parameters
Edit values in `config.py`:
- `DEFAULT_REPETITIONS`: Number of questions per repetition
- `DEFAULT_TEMPERATURE`: Model response randomness
- `MAX_TOKENS`: Maximum response length

## Research Context

This implementation is based on academic research evaluating cultural awareness in LLMs. The methodology follows established cultural psychology frameworks and provides quantitative measures of model cultural alignment.

## License

This project is provided for research and educational purposes. Please cite the original research paper when using this code.

## Troubleshooting

### Common Issues

**API Key Error**: Ensure your OpenAI API key is properly set
**Data Path Error**: Verify your data paths exist and contain JSON files
**Permission Error**: Check file permissions for cache and output directories
