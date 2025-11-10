# Research Repository

Public research repository for autonomous agent-based code research.

## Overview

This repository is designed for autonomous code agents (remote and web-based) to conduct independent research tasks. Each research task is fully self-contained within its own directory, allowing agents to work on multiple investigations simultaneously without interference.

## Repository Structure

```
research/
├── README.md                    # This file
├── AGENTS.md                    # Quick start guide for AI agents
├── .github/
│   └── agents/
│       └── agent-config.md      # Configuration and guidelines for autonomous agents
└── [research-task-name]/        # Individual research task directories
    ├── notes.md                 # Working notes tracking progress
    ├── README.md                # Final report (created at end)
    ├── code/                    # Code artifacts
    ├── data/                    # Data files
    └── results/                 # Output and results
```

## Research Task Workflow

### For Autonomous Agents

**Quick Start**: See [AGENTS.md](AGENTS.md) for detailed instructions.

Each research task should:

1. **Create a dedicated directory** named descriptively (e.g., `memory-optimization-study`, `async-pattern-analysis`)
2. **Create a notes.md file** to track your work as you go
3. **Build a README.md report** at the end of your investigation
4. **Work self-contained** - all code, data, and documentation within the task directory
5. **Commit selectively**:
   - Include: notes.md, README.md, code you wrote, git diffs
   - Exclude: full repos, build artifacts, large binaries (>2MB), _summary.md files

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
├── notes.md               # Working notes (create at start, update as you work)
├── README.md              # Final report (create at end)
├── requirements.txt       # Dependencies (Python)
├── package.json          # Dependencies (Node.js)
├── code/                 # Source code you wrote
│   └── experiments/      # Experimental code
├── data/                 # Input data
│   ├── raw/             # Original data
│   └── processed/       # Processed data
├── results/             # Output
│   ├── figures/         # Visualizations
│   └── reports/         # Analysis reports
└── diffs/               # Git diffs from modified repos (not full repos)
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

2. Create a notes.md file to track your work:
   ```bash
   cat > notes.md << 'EOF'
   # Research Notes
   
   ## [Date/Time] - Starting Investigation
   
   Objective: [What you're investigating]
   
   ## [Date/Time] - Initial Setup
   
   [Track your progress here as you work]
   EOF
   ```

3. Work on your research:
   - Add code, data, and experiments
   - Update notes.md as you go
   - Track what you tried and what you learned

4. Create README.md at the end:
   ```bash
   cat > README.md << 'EOF'
   # [Research Task Name]
   
   ## Objective
   [Clear statement of what you investigated]
   
   ## Methodology
   [How you approached the research]
   
   ## Results
   [Key findings]
   
   ## Conclusions
   [Takeaways and recommendations]
   EOF
   ```

5. Commit only relevant files:
   - notes.md and README.md
   - Code you wrote
   - Git diffs (not full repos)
   - Small binaries (<2MB)

### For Autonomous Agents

See [AGENTS.md](AGENTS.md) for quick start instructions and `.github/agents/agent-config.md` for detailed configuration.

## Examples

Example research tasks might include:
- Performance benchmarking studies
- Algorithm comparison analyses
- Framework evaluation research
- Design pattern explorations
- Security vulnerability research
- Code optimization experiments

## Contributing

This repository is designed for autonomous agent operation. Each research task is independent and self-managed. 

For detailed contribution guidelines, please see [CONTRIBUTING.md](CONTRIBUTING.md).

Key principles:
- Well-documented
- Reproducible
- Self-contained
- Properly structured

## Security

For security concerns and best practices, please see [SECURITY.md](SECURITY.md).

## License

This repository is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

Individual research tasks may have additional licensing information in their respective directories.
