# Contributing to Research Repository

Thank you for your interest in contributing to this research repository! This guide will help you get started.

## Overview

This repository is designed for autonomous agent-based research tasks. Contributions typically involve creating new research tasks or improving existing ones.

## How to Contribute

### Creating a New Research Task

1. **Choose a descriptive name** for your research task using lowercase-with-hyphens format:
   - ✅ `performance-benchmarking-2024`
   - ✅ `react-hooks-patterns`
   - ❌ `My Research Project`

2. **Create the directory structure**:
   ```bash
   mkdir -p [task-name]/{code,data/raw,data/processed,results/figures,results/reports}
   cd [task-name]
   ```

3. **Initialize with a README.md** that includes:
   - Research objective
   - Background and motivation
   - Methodology
   - Setup and installation instructions
   - Usage examples
   - Expected results
   - Conclusions

4. **Document dependencies** in appropriate files:
   - Python: `requirements.txt`
   - Node.js: `package.json`
   - Other: Document in README.md

5. **Keep work self-contained**:
   - All code, data, and documentation within the task directory
   - No cross-task dependencies unless explicitly documented
   - Tasks should be independently runnable

### Code Quality Standards

- **Documentation**: Include clear docstrings and comments
- **Reproducibility**: Pin dependency versions, document random seeds
- **Modularity**: Separate concerns (data loading, processing, analysis, visualization)
- **Testing**: Include basic tests where applicable
- **Clean code**: Follow language-specific style guides

### Commit Messages

Use clear, descriptive commit messages:
```
[task-name] Brief description of changes

Optional longer description explaining why the change was made.
```

Examples:
- `[performance-study] Add initial benchmarking script`
- `[data-analysis] Fix data preprocessing bug`
- `Update README with new task examples`

### Pull Requests

1. **Fork the repository** (for external contributors)
2. **Create a feature branch** from `main`
3. **Make your changes** following the guidelines above
4. **Test your changes** to ensure reproducibility
5. **Submit a pull request** with:
   - Clear title describing the change
   - Description of what was added/changed
   - Link to any related issues
   - Screenshots (if applicable)

### Code Review Process

All contributions will be reviewed for:
- Adherence to repository structure
- Code quality and documentation
- Reproducibility
- No security vulnerabilities
- No sensitive data exposure

## What NOT to Contribute

- ❌ Changes to other tasks' directories without permission
- ❌ Modifications to repository-level configuration without discussion
- ❌ Large binary files (use .gitignore)
- ❌ Sensitive data or API keys
- ❌ Code with security vulnerabilities

## Getting Help

- Review the main [README.md](README.md) for repository overview
- Check [.github/agents/agent-config.md](.github/agents/agent-config.md) for detailed guidelines
- Look at `example-research-task/` for structure reference
- Open an issue for questions or discussions

## License

By contributing, you agree that your contributions will be licensed under the MIT License.

## Code of Conduct

### Our Pledge

We are committed to providing a welcoming and inclusive environment for all contributors.

### Our Standards

Examples of behavior that contributes to a positive environment:
- Using welcoming and inclusive language
- Being respectful of differing viewpoints
- Gracefully accepting constructive criticism
- Focusing on what is best for the research community
- Showing empathy towards others

Examples of unacceptable behavior:
- Harassment or discriminatory language
- Trolling, insulting/derogatory comments
- Publishing others' private information
- Other conduct that could be considered inappropriate in a professional setting

### Enforcement

Instances of unacceptable behavior should be reported to the repository maintainers. All complaints will be reviewed and investigated promptly and fairly.

## Attribution

This Contributing guide is adapted from best practices in open source research repositories.
