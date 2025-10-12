# Contributing to mcp-perplexity

Thank you for your interest in contributing to the mcp-perplexity project! We welcome contributions from the community. Please take a moment to review this document for guidelines on how to contribute.

## Getting Started

1. **Fork the repository** on GitHub: [https://github.com/daniel-lxs/mcp-perplexity](https://github.com/daniel-lxs/mcp-perplexity)
2. **Clone your fork** locally:
   ```bash
   git clone https://github.com/YOUR_USERNAME/mcp-perplexity.git
   cd mcp-perplexity
   ```
3. **Set up the development environment** using Hatch:
   ```bash
   pip install hatch
   hatch env create
   hatch shell
   ```

## Making Changes

1. Create a new branch for your changes:
   ```bash
   git checkout -b my-feature-branch
   ```
2. Make your changes and ensure they follow the project's coding style
3. Write tests for any new functionality
4. Verify all tests pass:
   ```bash
   hatch run test
   ```
5. Commit your changes with a descriptive message following the [Conventional Commits](https://www.conventionalcommits.org/) format

## Submitting Changes

1. Push your branch to your fork:
   ```bash
   git push origin my-feature-branch
   ```
2. Open a **Pull Request** against the `main` branch of the main repository
3. Provide a clear description of your changes in the PR, including:
   - The problem you're solving
   - Your solution approach
   - Any relevant screenshots or test results

## Code Style

- Follow existing code patterns and style
- Keep code clean and well-documented
- Use type hints where appropriate
- Write clear commit messages following Conventional Commits

## Reporting Issues

If you find a bug or have a feature request, please open an issue on GitHub:
[https://github.com/daniel-lxs/mcp-perplexity/issues](https://github.com/daniel-lxs/mcp-perplexity/issues)

Include as much detail as possible, including:
- Steps to reproduce the issue
- Expected behavior
- Actual behavior
- Any relevant error messages or screenshots

## License

By contributing to this project, you agree that your contributions will be licensed under the project's MIT License. 