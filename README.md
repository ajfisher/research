# Research Repository

Public research repository for autonomous agent-based code research.

## Overview

This repository is designed for autonomous code agents (remote and web-based) to conduct independent research tasks. Each research task is fully self-contained within its own directory, allowing agents to work on multiple investigations simultaneously without interference.

## Repository Structure

```
research/
├── README.md                    # This file
├── .github/
│   └── agents/
│       └── agent-config.md      # Configuration and guidelines for autonomous agents
└── [research-task-name]/        # Individual research task directories
    ├── README.md                # Task-specific documentation
    ├── research-notes.md        # Findings and observations
    ├── code/                    # Code artifacts
    ├── data/                    # Data files
    └── results/                 # Output and results
```

## Research Task Workflow

### For Autonomous Agents

Each research task should:

1. **Create a dedicated directory** named descriptively (e.g., `memory-optimization-study`, `async-pattern-analysis`)
2. **Initialize with a README.md** containing:
   - Research question/objective
   - Methodology
   - Dependencies and requirements
   - Expected outcomes
3. **Work self-contained** - all code, data, and documentation within the task directory
4. **Document findings** in `research-notes.md` or similar
5. **Preserve artifacts** - keep all intermediate results for reproducibility

### Directory Naming Convention

Use lowercase with hyphens:
- ✅ `performance-benchmarking-2024`
- ✅ `react-hooks-patterns`
- ❌ `My Research Project`
- ❌ `test_123`

### Task Structure Template

When starting a new research task, create:

```
[task-name]/
├── README.md              # Overview, goals, and methodology
├── research-notes.md      # Observations and findings
├── requirements.txt       # Dependencies (Python)
├── package.json          # Dependencies (Node.js)
├── code/                 # Source code
│   └── experiments/      # Experimental code
├── data/                 # Input data
│   ├── raw/             # Original data
│   └── processed/       # Processed data
└── results/             # Output
    ├── figures/         # Visualizations
    └── reports/         # Analysis reports
```

## Guidelines for Autonomous Operation

### Self-Contained Tasks
- Each task must have all dependencies documented
- No cross-task dependencies unless explicitly documented
- Tasks should be runnable independently

### Documentation Requirements
- Clear research objectives
- Methodology and approach
- Results and conclusions
- Reproduction steps

### Code Standards
- Include setup instructions
- Document environment requirements
- Provide example usage
- Add inline comments for complex logic

### Data Management
- Keep raw data immutable
- Document data sources
- Include data preprocessing scripts
- Version control data transformations

## Getting Started

### For New Research Tasks

1. Create a new directory for your research task:
   ```bash
   mkdir [research-task-name]
   cd [research-task-name]
   ```

2. Initialize with README:
   ```bash
   cat > README.md << 'EOF'
   # [Research Task Name]
   
   ## Objective
   [Clear statement of what you're investigating]
   
   ## Methodology
   [How you'll approach the research]
   
   ## Setup
   [Dependencies and installation steps]
   
   ## Running
   [How to execute the research]
   
   ## Results
   [Where to find results]
   EOF
   ```

3. Add your code, data, and documentation

4. Document findings and conclusions

### For Autonomous Agents

See `.github/agents/agent-config.md` for specific agent configuration and operational guidelines.

## Examples

Example research tasks might include:
- Performance benchmarking studies
- Algorithm comparison analyses
- Framework evaluation research
- Design pattern explorations
- Security vulnerability research
- Code optimization experiments

## Contributing

This repository is designed for autonomous agent operation. Each research task is independent and self-managed. Ensure your work is:
- Well-documented
- Reproducible
- Self-contained
- Properly structured

## License

Each research task may have its own license. Check individual task directories for specific licensing information.
