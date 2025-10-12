# ci-starter

Kickstarts the semantic release pipeline for your Python project on GitHub. It creates an configuration file _semantic-release.toml_ for python-semantic-release and a pipeline with reusable workflows in _.github/workflows_.

## Usage

### Prerequisites

You will have to do the flollowing things yourself:

- Create your project:
    - Use uv to initialize your project (must be a package)
        - Fill it with some minimally meaningful content, I recommend:
            - set version to `0.0.0`
            - project urls
            - keywords
            - classifiers
            - license
        - Add a dependency group for running tests (group shall contain at least your test runner, e.g. pytest)
    - Create tests (CI/CD pipeline would fail if no tests are found)
    - Format and check everything with ruff
    - Set up a trusted publisher for your project on pypi.org:
        - Workflow: `continuous-delivery.yml` (default workflow name)
        - Environment name: `pypi`
    - Set up a trusted publisher for your project on test.pypi.org:
        - Workflow: `continuous-delivery.yml`
        - Environment name: `testpypi`
    - Create a GitHub repository for your project
    - Add remote origin and its ssh address at your local clone

### Create CI/CD Pipeline With ci-starter

Run these commands:

```text
$ ci-start psr-config
$ ci-start workflows
$ ci-start update-actions
```

The psr-config command creates the _semantic-release.toml_, the second one creates the workflow files (.github/workflows/*.yml), the third one fetches the current versions of the GitHub Actions used in the workflow files and updates the workflow files accordingly.

It is your responsibility to check whether it is safe to use the suggested current versions of the GitHub Actions (beware of supply chain attacks).
