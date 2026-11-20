# Contributing Guidelines

Thank you for your interest in contributing to our project. Whether it's a bug report, new feature, correction, or additional
documentation, we greatly value feedback and contributions from our community.

Please read through this document before submitting any issues or pull requests to ensure we have all the necessary
information to effectively respond to your bug report or contribution.

## Reporting Bugs/Feature Requests

We welcome you to use the GitHub issue tracker to report bugs or suggest features.

When filing an issue, please check existing open, or recently closed, issues to make sure somebody else hasn't already
reported the issue. Please try to include as much information as you can. Details like these are incredibly useful:

* A reproducible test case or series of steps
* The version of our code being used
* Any modifications you've made relevant to the bug
* Anything unusual about your environment or deployment

## Contributing via Pull Requests

Contributions via pull requests are much appreciated. Do note that our [workshop instructions website](https://catalog.workshops.aws/amazon-bedrock) needs to be kept in sync with any major structural changes to this codebase, and releases coordinated between the two. This website is managed by our maintainers outside of GitHub, but we appreciate your suggestions here for updates to the website too.

Before sending us a pull request, please ensure that:

1. You are working against the latest source on the *main* branch.
2. You've completed the **developer setup** as detailed below.
3. You check existing open, and recently merged, pull requests to make sure someone else hasn't addressed the problem already.
4. You open an issue to discuss any significant work - we would hate for your time to be wasted.

To send us a pull request, please:

1. Fork the repository.
2. Modify the source; please focus on the specific change you are contributing. If you also reformat all the code, it will be hard for us to focus on your change.
3. Ensure local tests pass.
4. Commit to your fork using clear commit messages.
5. Send us a pull request, answering any default questions in the pull request interface.
6. Pay attention to any automated CI failures reported in the pull request, and stay involved in the conversation.

GitHub provides additional document on [forking a repository](https://help.github.com/articles/fork-a-repo/) and
[creating a pull request](https://help.github.com/articles/creating-a-pull-request/).

## Finding contributions to work on

Looking at the existing issues is a great way to find something to contribute on. As our projects, by default, use the default GitHub issue labels (enhancement/bug/duplicate/help wanted/invalid/question/wontfix), looking at any 'help wanted' issues is a great place to start.

## Developer setup

We recommend using [uv](https://docs.astral.sh/uv/) to manage your (virtual) environment for the project. Refer to [pyproject.toml](./pyproject.toml) for the supported range of Python versions.

With uv installed, you can create and set up your virtual environment by running:

```sh
uv venv
uv sync --all-extras --all-groups
```

Next, ensure the automated tools are set up **before** committing any changes, to avoid rejected pull requests.

First, **install and activate pre-commit** to automatically lint files before every git commit:

```bash
uv tool install pre-commit --with pre-commit-uv
pre-commit install
```

You can also run these checks manually at any time with:

```bash
pre-commit run --all-files
```

Then, as an added layer of protection, install [nbstripout](https://github.com/kynan/nbstripout) as a [git filter](https://git-scm.com/docs/gitattributes#_filter) to ensure Python notebook outputs and unnecessary metadata are stripped during staging, even if the git pre-commit hook fails to run:

```bash
uv tool install nbstripout
nbstripout --install --attributes .gitattributes

# Verify the status:
nbstripout --status
```

## About our code quality workflows

This repository implements a range of automated workflows as described below, to drive code quality and safety. Pre-commit hooks are configured in [.pre-commit-config.yaml](./.pre-commit-config.yaml), and automated GitHub Action workflows in the [.github/workflows](.github/workflows) folder.

| Automation | What it does | Where it's applied |
|------------|--------------|--------------------|
| [markdownlint-cli2](https://github.com/DavidAnson/markdownlint-cli2) | Validates formatting consistency for Markdown files | Pre-commit hook and PR 'lint' workflow |
| [nbstripout](https://pypi.org/project/nbstripout/) | Strip cell output and unnecessary metadata from Python notebook files | `git add` filter and Pre-commit hook and PR 'lint' workflow |
| [ruff](https://docs.astral.sh/ruff/) | Lints and reformats Python code | Pre-commit hook and PR 'lint' workflow |
| [yamllint](https://yamllint.readthedocs.io/en/stable/) | Validates syntax and formatting issues in configuration YAML files | Pre-commit hook and PR 'lint' workflow |
| Dependabot auto-merge (patch/minor) | Auto-merge patch & minor dependency updates proposed by Dependabot | Continuous (analyzed weekly, Monday) |
| [lychee](https://github.com/lycheeverse/lychee) | Checks URL links aren't broken | Weekly GitHub Workflow (Wednesday) |
| Stale issue/PR cleanup | Marks GitHub issues and PRs with no recent activity | Weekly (Monday) |

## Code of Conduct

This project has adopted the [Amazon Open Source Code of Conduct](https://aws.github.io/code-of-conduct).
For more information see the [Code of Conduct FAQ](https://aws.github.io/code-of-conduct-faq) or contact
opensource-codeofconduct@amazon.com with any additional questions or comments.

## Security issue notifications

If you discover a potential security issue in this project we ask that you notify AWS/Amazon Security via our [vulnerability reporting page](http://aws.amazon.com/security/vulnerability-reporting/). Please do **not** create a public github issue.

## Licensing

See the [LICENSE](LICENSE) file for our project's licensing. We will ask you to confirm the licensing of your contribution.
