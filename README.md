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
## 4 research projects

### [go-wasm-browser-eval](https://github.com/ajfisher/research/tree/main/go-wasm-browser-eval) (2025-12-24)

This project explores running Go applications in the browser via WebAssembly to lay the foundation for porting Miller (mlr) CLI functionality to client-side environments. Using Go's native WebAssembly support (`GOOS=js GOARCH=wasm`), researchers created a demo exposing simple CSV-processing functions to JavaScript. Comparisons with TinyGo, an alternate compiler promising smaller binaries, were partially hindered due to a Go version mismatch. Still, the effort highlights the potential of TinyGo for significantly smaller and faster WASM modules while identifying challenges with compatibility and deployment.

- **Native Go WASM**: Successfully built a module (~2.5 MB) demonstrating CSV summarization via `syscall/js`.
- **TinyGo**: Promising for size and performance optimization (~300–500 KB expected), but blocked due to incompatibility with Go 1.24.
- **Toolchain Details**: Build scripts automate the usage of `wasm_exec.js` and hosting for browser testing.

Resources: [Native Go WASM Demo](http://localhost:8000/index.html), [TinyGo Compiler](https://tinygo.org/).

### [platform-native-ux-scoring-probe](https://github.com/ajfisher/research/tree/main/platform-native-ux-scoring-probe) (2025-11-20)

This project explores the development of a lightweight CLI probe, similar to Lighthouse, aimed at scoring how "platform-native" a website's critical user flows feel. Using Playwright, the probe executes user flows described in YAML, collects heuristic DOM and network metrics, and generates scores based on factors such as routing, form usage, progressive enhancement, and accessibility. It also features an optional no-JavaScript replay mode to test a site's resilience without client-side JavaScript. The tool produces detailed reports in multiple formats (JSON, HTML, and Markdown) with a visualized platform-native score for each flow.

- Key tools and setup: [Playwright](https://playwright.dev/) for automation; installable via Node 20+.
- Categories scored: Routing (25%), Forms (25%), Data Fetching (20%), Progressive Enhancement (20%), and Semantics/Accessibility (10%).
- Outputs: JSON, HTML, Markdown reports with scores and metrics.
- Future improvements: Add richer timing/paint metrics, expand action vocabulary, support multiple domains, and introduce advanced visualizations.

### [three-sided-football-strategy](https://github.com/ajfisher/research/tree/main/three-sided-football-strategy) (2025-11-20)

This study examined strategic decision-making in three-sided football, focusing on team dynamics across three periods, collaborative versus competitive play, and set-piece strategies. Using Monte Carlo simulations and game-theoretic models, researchers analyzed adaptive and static strategies for teams leading or trailing while factoring in fatigue. Findings emphasize the efficacy of defensive strategies early on, tactical collaboration when chasing, and context-specific set-piece tactics for goals or possession gains. The code and detailed results can be replicated via scripts provided in the [research repository](#F:code/simulation.py†L21-L400).

**Key Findings:**
- Defensive play minimizes goals conceded in earlier periods; adaptive aggression helps trailers but incurs fatigue.
- Late-game collaboration can double a leader's concessions but requires chasers to endure higher fatigue risks.
- Corners, free kicks, and kick-offs favor structured setups for leaders while offering dynamic opportunities for trailers based on context.

### [tag-prediction-ajfisher-me](https://github.com/ajfisher/research/tree/main/tag-prediction-ajfisher-me) (2025-11-15)

This project explores scikit-learn-based approaches to auto-tagging markdown posts on `ajfisher.me`, aiming to recommend consistent front-matter tags. A linear SVM emerged as the best-performing model, though its micro-F1 score of ~0.08 underscores challenges resulting from sparse tag distributions and limited data. Umbrella tags like `web`, `development`, and `internet` were identified as consistently missing across many posts, highlighting opportunities to improve coverage. Future enhancements include integrating contextual embeddings and refining model calibration for better predictions.

- **Key Findings**:
  - Linear SVM outperforms other models but struggles with limited tag generalisation.
  - Common missing tags: `web`, `development`, `internet`, and `media`.
  - No misapplied tags were flagged; however, low cross-validation scores suggest overfitting concerns.

Find the analysis code [here](code/tag_prediction_analysis.py) and sample outputs in [`results/`](results/).

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
