# Agent Configuration and Guidelines

## Overview

This document provides configuration and operational guidelines for autonomous agents working in this research repository.

## Agent Capabilities and Permissions

### Allowed Operations

Autonomous agents operating in this repository are authorized to:

1. **Create Research Tasks**
   - Create new directories for research tasks
   - Initialize task structures following the repository template
   - Create and modify files within task directories

2. **Code Development**
   - Write and test code within task directories
   - Install dependencies (document in requirements files)
   - Run experiments and analyses
   - Generate outputs and artifacts

3. **Documentation**
   - Create and update README files
   - Document research findings
   - Write technical reports
   - Add inline code documentation

4. **Data Operations**
   - Create data directories
   - Process and transform data
   - Generate visualizations
   - Export results

5. **Version Control**
   - Commit changes within task directories
   - Create descriptive commit messages
   - Push completed work

### Restricted Operations

Agents should NOT:
- Modify other tasks' directories without explicit permission
- Change repository-level configuration files (README.md, this file)
- Delete or modify existing research artifacts from other tasks
- Share sensitive data externally
- Introduce security vulnerabilities

## Operational Guidelines

### Task Initialization

When starting a new research task:

1. **Choose a descriptive directory name** (lowercase-with-hyphens)
2. **Create the directory structure**:
   ```bash
   mkdir -p [task-name]/{code,data/raw,data/processed,results}
   ```
3. **Initialize README.md** with research objectives
4. **Document dependencies** in appropriate files (package.json, requirements.txt, etc.)

### Working Within a Task

1. **Stay self-contained** - All work within the task directory
2. **Document as you go** - Update research notes regularly
3. **Version control** - Commit meaningful progress incrementally
4. **Test your code** - Ensure reproducibility
5. **Clean up** - Remove temporary files, organize outputs

### Completing a Task

Before considering a task complete:

1. ✅ README.md clearly explains the research
2. ✅ All code is documented and tested
3. ✅ Dependencies are listed
4. ✅ Results are saved and documented
5. ✅ Findings are summarized
6. ✅ Reproduction steps are clear
7. ✅ Temporary files are cleaned up

### Code Quality Standards

```python
# Example: Well-documented research code
def analyze_performance(data, iterations=1000):
    """
    Analyze performance metrics from benchmark data.
    
    Args:
        data: Input dataset with performance measurements
        iterations: Number of iterations to run (default: 1000)
    
    Returns:
        Dictionary with statistical analysis results
    """
    # Implementation
    pass
```

Key principles:
- Clear function/class names
- Docstrings for public interfaces
- Inline comments for complex logic
- Type hints where applicable
- Error handling for edge cases

### Documentation Standards

Each task's README.md should include:

```markdown
# [Research Task Title]

## Objective
Clear, concise statement of research goals.

## Background
Context and motivation for the research.

## Methodology
Step-by-step approach and techniques used.

## Setup and Installation
```bash
# Commands to set up the environment
pip install -r requirements.txt
```

## Usage
```bash
# Commands to run the research
python code/main.py
```

## Results
Summary of findings with references to result files.

## Conclusions
Key takeaways and recommendations.

## Future Work
Potential extensions or follow-up research.
```

## Environment Setup

### Python Projects
```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # or `venv\Scripts\activate` on Windows

# Install dependencies
pip install -r requirements.txt
```

### Node.js Projects
```bash
# Install dependencies
npm install

# Run scripts
npm run [script-name]
```

### Other Languages
Document specific setup requirements in the task README.

## Data Handling

### Data Organization
```
data/
├── raw/              # Original, immutable data
├── processed/        # Cleaned/transformed data
└── README.md         # Data documentation
```

### Data Documentation
Document in `data/README.md`:
- Data sources and acquisition dates
- Data format and schema
- Preprocessing steps
- Known issues or limitations

### Privacy and Security
- No personally identifiable information (PII)
- No API keys or credentials in code
- No proprietary or confidential data
- Use environment variables for secrets

## Results and Outputs

### Organization
```
results/
├── figures/          # Plots, charts, visualizations
├── reports/          # Analysis reports, summaries
├── models/           # Trained models (if applicable)
└── README.md         # Results documentation
```

### Formats
- Figures: PNG, SVG, or PDF
- Data: CSV, JSON, or Parquet
- Reports: Markdown or PDF
- Models: Standard format for framework (e.g., .pkl, .h5)

## Best Practices

### 1. Reproducibility
- Pin dependency versions
- Document random seeds
- Include environment details
- Provide complete setup instructions

### 2. Modularity
- Separate concerns (data loading, processing, analysis, visualization)
- Reusable functions over script code
- Configuration files for parameters

### 3. Testing
```python
# Include basic tests
def test_data_loading():
    """Test that data loads correctly."""
    data = load_data('data/raw/sample.csv')
    assert len(data) > 0
    assert 'required_column' in data.columns
```

### 4. Version Control
- Commit messages: `[task-name] Brief description of changes`
- Commit frequently with logical units of work
- Don't commit large binary files (use .gitignore)

### 5. Resource Management
- Clean up temporary files
- Close file handles properly
- Limit memory usage for large datasets
- Document computational requirements

## Error Handling

When encountering errors:

1. **Document the error** in research notes
2. **Try to resolve** using standard debugging
3. **Document the resolution** for future reference
4. **Update code** to prevent recurrence

## Collaboration Between Agents

If multiple agents work on related tasks:

1. **Communicate via documentation** - Update shared docs
2. **Avoid conflicts** - Work in separate directories
3. **Reference related work** - Link to other tasks in README
4. **Share reusable code** - Consider creating a shared utilities folder

## Examples

### Example Task Structure
```
performance-benchmarking-2024/
├── README.md
├── research-notes.md
├── requirements.txt
├── .gitignore
├── code/
│   ├── benchmarks.py
│   ├── analysis.py
│   └── visualization.py
├── data/
│   ├── raw/
│   │   └── benchmark_results.csv
│   └── processed/
│       └── cleaned_results.csv
└── results/
    ├── figures/
    │   ├── performance_comparison.png
    │   └── trend_analysis.png
    └── reports/
        └── final_report.md
```

### Example .gitignore
```gitignore
# Python
__pycache__/
*.py[cod]
*$py.class
venv/
.env

# Node
node_modules/
npm-debug.log

# Data (if too large)
*.csv
*.parquet
data/raw/*.zip

# Temporary files
*.tmp
.DS_Store
```

## Agent Self-Assessment

Before finalizing work, agents should verify:

- [ ] Research objective is clearly stated
- [ ] Methodology is documented
- [ ] Code is clean and documented
- [ ] Dependencies are listed
- [ ] Results are reproducible
- [ ] Findings are summarized
- [ ] No sensitive data is exposed
- [ ] No security vulnerabilities introduced
- [ ] Task directory is well-organized
- [ ] Git history is clean and meaningful

## Support and Resources

### Common Tools
- **Python**: pandas, numpy, matplotlib, scikit-learn
- **Node.js**: lodash, axios, chart.js
- **Version Control**: git
- **Documentation**: Markdown, Jupyter notebooks

### Troubleshooting
1. Check task README for specific setup instructions
2. Verify dependencies are installed
3. Check for environment-specific issues
4. Review error messages and logs
5. Document issues in research notes

## Updates to This Configuration

This configuration file may be updated as new patterns emerge or requirements change. Agents should check for updates periodically.

**Last Updated**: 2024-11-08
**Version**: 1.0
