# Version Release 🚀

!!! info "Versioning Schema"
    simpleval versioning follows [Semantic Versioning](https://semver.org/).

    **Stable versions**

    `MAJOR.MINOR.PATCH` where:
    
    - `MAJOR` version when you make incompatible or breaking changes
    - `MINOR` version when you add functionality in a backwards-compatible manner
    - `PATCH` version when you make backwards-compatible bug fixes and minor changes

    Examples: `1.0.0`, `1.0.1`, `2.0.0`

    **Pre-release versions**

    For pre-release versions, append `-alpha.x`, `-beta.x`, or `-rc.x` (only those three are allowed),
    where alpha is for early testing, beta is for more stable testing, and rc is for release candidate.

    Examples: `1.0.0-alpha.1`, `1.0.0-beta.1`, `1.0.0-rc.1`

## Release Procedure

### Update Version in `pyproject.toml`

Using `uv` Update the version in `pyproject.toml` to the new version according to the [Versioning Schema](#versioning-schema) above. Make sure you adhere to the versioning rules and only include alpha, beta, or rc for pre-release versions.

examples:
```
uv version --bump patch # 1.0.1 -> 1.0.2
uv version --bump minor # 1.0.1 -> 1.1.0
uv version --bump major # 1.0.1 -> 2.0.0

uv version 1.0.1-alpha.1 # set to pre-release version
uv version 1.0.1-beta.1 # set to pre-release version
uv version 1.0.1-rc.1 # set to pre-release version

```

### Create a Release Tag
On the main branch, create a tag using the git cli. Set the tag value to be `v<new-version>` where `<new-version>` is the value you set in `pyproject.toml`, add a message with the release notes, and push the tag to the remote repository.

!!! info "Update Version Example"
    ```bash
    git checkout main
    git pull origin main
    git tag -a v1.0.1 -m "Release version 1.0.1"
    git push origin v1.0.1
    ```

!!! warning
    The tag name must match the version in `pyproject.toml` exactly prefixed with `v`

    For example: `pyproject.toml` version==`1.0.1` 👉 tag name==`v1.0.1`

### Release Workflow

The tag creation will trigger the GitHub Actions workflow [Release](https://github.com/cyberark/simple-llm-eval/actions/workflows/ci.yml)


!!! Abstract "Release Workflow"
    The release workflow will:
    - Validate the `pyproject.toml` version against the tag name
    - Build the package
    - Create GitHub release with notes
    - Attach binaries to GitHub release
    - *Publish the package to PyPI
    - Publish the docs

### Docs Only Release
In case you make a docs-only update, see [Publishing the Docs](../developers/dev-notes.md/#publishing-the-docs)

<br>
