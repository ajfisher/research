# Research Repository

Public research repository for autonomous agent-based code research.

## Overview

This repository is designed for autonomous code agents (remote and web-based) to conduct independent research tasks. Each research task is fully self-contained within its own directory, allowing agents to work on multiple investigations simultaneously without interference.

<!--[[[cog
import os
import subprocess
import pathlib
from datetime import datetime, timezone

# Model to use for generating summaries
MODEL = "github/gpt-4o"

# Get all subdirectories with their first commit dates
research_dir = pathlib.Path.cwd()
subdirs_with_dates = []

for d in research_dir.iterdir():
    if d.is_dir() and not d.name.startswith('.') and d.name != 'example-research-task':
        # Get the date of the first commit that touched this directory
        try:
            result = subprocess.run(
                ['git', 'log', '--diff-filter=A', '--follow', '--format=%aI', '--reverse', '--', d.name],
                capture_output=True,
                text=True,
                timeout=5
            )
            if result.returncode == 0 and result.stdout.strip():
                # Parse first line (oldest commit)
                date_str = result.stdout.strip().split('\n')[0]
                commit_date = datetime.fromisoformat(date_str.replace('Z', '+00:00'))
                subdirs_with_dates.append((d.name, commit_date))
            else:
                # No git history, use directory modification time
                subdirs_with_dates.append((d.name, datetime.fromtimestamp(d.stat().st_mtime, tz=timezone.utc)))
        except Exception:
            # Fallback to directory modification time
            subdirs_with_dates.append((d.name, datetime.fromtimestamp(d.stat().st_mtime, tz=timezone.utc)))

# Print the heading with count
if subdirs_with_dates:
    print(f"## {len(subdirs_with_dates)} research project{'s' if len(subdirs_with_dates) != 1 else ''}\n")

    # Sort by date, most recent first
    subdirs_with_dates.sort(key=lambda x: x[1], reverse=True)

    for dirname, commit_date in subdirs_with_dates:
        folder_path = research_dir / dirname
        readme_path = folder_path / "README.md"
        summary_path = folder_path / "_summary.md"

        date_formatted = commit_date.strftime('%Y-%m-%d')

        # Get GitHub repo URL
        github_url = None
        try:
            result = subprocess.run(
                ['git', 'remote', 'get-url', 'origin'],
                capture_output=True,
                text=True,
                timeout=2
            )
            if result.returncode == 0 and result.stdout.strip():
                origin = result.stdout.strip()
                # Convert SSH URL to HTTPS URL for GitHub
                if origin.startswith('git@github.com:'):
                    origin = origin.replace('git@github.com:', 'https://github.com/')
                if origin.endswith('.git'):
                    origin = origin[:-4]
                github_url = f"{origin}/tree/main/{dirname}"
        except Exception:
            pass

        if github_url:
            print(f"### [{dirname}]({github_url}) ({date_formatted})\n")
        else:
            print(f"### {dirname} ({date_formatted})\n")

        # Check if summary already exists
        if summary_path.exists():
            # Use cached summary
            with open(summary_path, 'r') as f:
                description = f.read().strip()
                if description:
                    print(description)
                else:
                    print("*No description available.*")
        elif readme_path.exists():
            # Generate new summary using llm command
            prompt = """Summarize this research project concisely. Write just 1 paragraph (3-5 sentences) followed by an optional short bullet list if there are key findings. Vary your opening - don't start with "This report" or "This research". Include 1-2 links to key tools/projects. Be specific but brief. No emoji."""
            result = subprocess.run(
                ['llm', '-m', MODEL, '-s', prompt],
                stdin=open(readme_path),
                capture_output=True,
                text=True,
                timeout=60
            )
            if result.returncode != 0:
                error_msg = f"LLM command failed for {dirname} with return code {result.returncode}"
                if result.stderr:
                    error_msg += f"\nStderr: {result.stderr}"
                raise RuntimeError(error_msg)
            if result.stdout.strip():
                description = result.stdout.strip()
                print(description)
                # Save to cache file
                with open(summary_path, 'w') as f:
                    f.write(description + '\n')
            else:
                raise RuntimeError(f"LLM command returned no output for {dirname}")
        else:
            print("*No description available.*")

        print()  # Add blank line between entries

]]]-->
## 3 research projects

### [platform-native-ux-scoring-probe](https://github.com/ajfisher/research/tree/main/platform-native-ux-scoring-probe) (2025-11-20)

This research explores a lightweight CLI tool for assessing how "platform-native" a website feels during critical user flows by leveraging automated heuristics. Using Playwright, the tool executes scripted actions, collects DOM and network data, and optionally tests progressive enhancement by replaying flows without JavaScript. The probe provides category-based scores (e.g., routing, forms, data fetching) and combines them into an overall platform-native score, with results displayed in JSON, HTML, or Markdown formats. Developers can set up the tool quickly, describe flows in simple YAML files, and gain insights into their site's reliance on client-side logic versus browser-native features.

Key resources:
- [Playwright](https://playwright.dev): Headless browser automation used in the probe.
- Full setup and usage instructions in `flows.example.yaml`.

Key findings:
- Heuristic-based scoring effectively captures routing, forms, and PE behaviors with minimal configuration.
- The no-JS mode is a practical test for progressive enhancement resilience.
- Areas for improvement include richer visualizations and expanded action support.

### [three-sided-football-strategy](https://github.com/ajfisher/research/tree/main/three-sided-football-strategy) (2025-11-20)

This study investigates the strategic complexities of three-sided football using computational game theory, focusing on team adaptations across the three 25-minute periods, collaborative dynamics, and set-piece effectiveness. A Monte Carlo simulator and strategy analysis scripts were developed to model scenarios involving fatigue, scoreboard changes, and decision rules, producing valuable insights into optimal plays and alliances. Key findings highlight the payoff of defensive strategies early on, the high-risk but occasionally high-reward nature of late-game collaboration by trailing teams, and the nuanced advantages of different set-piece tactics depending on match context. Tools like the Monte Carlo simulator and strategy analyzer are available for further exploration ([simulation code](code/simulation.py), [strategy analysis](code/analyze_strategies.py)).

### Key Findings
- Defensive play minimizes concessions in early periods; adaptive collaboration or aggression benefits trailing teams during later stages but at the cost of higher fatigue.
- Late-game collaboration between trailing teams can double a leader's concessions, but it demands risky fatigue-intensive behavior.
- Set-piece tactics like structured kick-offs and direct free kicks yield better possession or scoring, depending on context and defensive setups.

### [tag-prediction-ajfisher-me](https://github.com/ajfisher/research/tree/main/tag-prediction-ajfisher-me) (2025-11-15)

This analysis explored classical machine learning methods for auto-tagging blog posts on `ajfisher.me`, aiming to enhance tag consistency and identify potential additions or removals. Using scikit-learn, models were trained on TF–IDF features extracted from post titles and content, with tags treated as multi-label outputs. The linear SVM was the most effective model, suggesting high-confidence tag additions like `web`, `development`, and `internet` for around 42 posts. While no misapplied tags were flagged, the low cross-validation performance indicates room for improvement, such as integrating richer semantic features.

- **Best model**: Linear SVM achieved ~0.08 micro-F1 but struggled with infrequent tags.
- **Suggested tags**: Commonly missing tags included `web`, `development`, and `internet`.
- **Future enhancements**: Use embeddings or topic models and expand labeled data.

<!--[[[end]]]-->

---

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

---

## Updating this README

This README uses [cogapp](https://nedbatchelder.com/code/cog/) to automatically generate project descriptions.

### Automatic updates

A GitHub Action automatically runs `cog -r -P README.md` on every push to main and commits any changes to the README or new `_summary.md` files.

### Manual updates

To update locally:

```bash
# Install dependencies
pip install -r requirements.txt

# Run cogapp to regenerate the project list
cog -r -P README.md
```

The script automatically:
- Discovers all subdirectories in this folder (excluding `.` directories and `example-research-task`)
- Gets the first commit date for each folder and sorts by most recent first
- For each folder, checks if a `_summary.md` file exists
- If the summary exists, it uses the cached version
- If not, it generates a new summary using `llm -m <!--[[[cog
print(MODEL, end='')
]]]-->
github/gpt-4o
<!--[[[end]]]-->` with a prompt that creates engaging descriptions with bullets and links
- Creates markdown links to each project folder on GitHub
- New summaries are saved to `_summary.md` to avoid regenerating them on every run

To regenerate a specific project's description, delete its `_summary.md` file and run `cog -r -P README.md` again.
