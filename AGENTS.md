# AGENTS.md

This file provides instructions for AI coding agents (GitHub Copilot, CODEX, Claude Code, etc.) working in this research repository.

## Research Workflow

Start by creating a new folder for your work with an appropriate name.

Create a `notes.md` file in that folder and append notes to it as you work, tracking what you tried and anything you learned along the way.

Build a `README.md` report at the end of the investigation.

Your final commit should include just that folder and selected items from its contents:

- The `notes.md` and `README.md` files
- Any code you wrote along the way
- If you checked out and modified an existing repo, the output of `git diff` against that modified repo saved as a file - but not a copy of the full repo
- If appropriate, any binary files you created along the way provided they are less than 2MB in size

Do NOT include full copies of code that you fetched as part of your investigation. Your final commit should include only new files you created or diffs showing changes you made to existing code.

Don't create a `_summary.md` file - these are added automatically after you commit your changes.

## Directory Structure

Each research task should follow this structure:

```
[research-task-name]/
├── README.md              # Final report of investigation
├── notes.md              # Working notes tracking progress
├── code/                 # Source code you wrote
├── data/                 # Data files (if needed)
│   ├── raw/             # Original data
│   └── processed/       # Processed data
├── results/             # Outputs
│   ├── figures/         # Visualizations
│   └── reports/         # Analysis reports
└── diffs/               # Git diffs from modified repos (not full repos)
```

## Task Naming Convention

Use lowercase with hyphens:
- ✅ `performance-benchmarking-2024`
- ✅ `react-hooks-patterns`
- ❌ `My Research Project`
- ❌ `test_123`

## Development Environment

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

## Code Standards

- Write clean, documented code
- Include docstrings for functions
- Add inline comments for complex logic
- Use type hints where applicable (Python)
- Handle errors appropriately

## Documentation Requirements

### notes.md
Track your progress as you work:
- Record what you tried
- Document errors encountered
- Note interesting discoveries
- Keep a chronological log of your investigation

### README.md
Create at the end with:
- **Objective**: Clear research question
- **Background**: Context and motivation
- **Methodology**: Approach taken
- **Setup**: Installation and dependencies
- **Results**: Key findings
- **Conclusions**: Takeaways and recommendations
- **Future Work**: Potential extensions

## What to Commit

### Include:
- `notes.md` with your working notes
- `README.md` with final report
- Code you wrote
- Small binary files (<2MB)
- Git diffs showing changes to existing repos

### Exclude:
- Full copies of checked-out repositories
- Large binary files (>2MB)
- Build artifacts and dependencies
- `_summary.md` files (auto-generated)
- Temporary files

## Git Workflow

```bash
# Add your research task folder
git add [research-task-name]/

# Commit with descriptive message
git commit -m "[research-task-name] Brief description of research"

# Push changes
git push
```

## Best Practices

1. **Stay Self-Contained**: Keep all work within your task directory
2. **Document as You Go**: Update `notes.md` frequently
3. **Clean Up**: Remove temporary files before committing
4. **Be Specific**: Use descriptive names for files and variables
5. **Test Your Code**: Ensure reproducibility
6. **Respect Resources**: Don't commit large files or full repos

## Examples

### Example notes.md Entry
```markdown
## 2024-11-08 14:30 - Initial Setup

Installed dependencies using pip. Created virtual environment.

## 2024-11-08 14:45 - First Experiment

Tried approach A but got error:
[error message]

Switching to approach B.

## 2024-11-08 15:20 - Success

Approach B worked! Results saved to results/output.csv
```

### Example Commit
```bash
git add performance-study/
git commit -m "[performance-study] Complete analysis of async patterns"
```

## Repository-Specific Notes

- This is a research repository for autonomous code research
- Each task is independent and self-contained
- Multiple agents can work simultaneously on different tasks
- See `.github/agents/agent-config.md` for additional configuration details

## Support

For questions about:
- **Repository structure**: See main `README.md`
- **Detailed guidelines**: See `.github/agents/agent-config.md`
- **Security practices**: See `SECURITY.md`
- **Contributing**: See `CONTRIBUTING.md`

## Version

Last Updated: 2024-11-08
Version: 1.0
