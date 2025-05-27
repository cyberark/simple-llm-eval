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

# Release Procedure

## The Simple Way (Recommended)

!!! info "The simple way"
    Simply run the release procedure script in one of the following ways:
    
    ```
    ./ci/scripts/create_version_pr.py --version 1.0.0-rc5g # Set a specific version (good for pre-release)
    ./ci/scripts/create_version_pr.py --bump-patch
    ./ci/scripts/create_version_pr.py --bump-minor
    ./ci/scripts/create_version_pr.py --bump-major
    ```

Until this is automated - after the release workflow is complete, update the `CHANGELOG.md` file with the new version and the changes made in this release (take from the release notes).

## The Manual Way

### 1. Update Version in `pyproject.toml`

!!! info "Recommended: Run the create version PR script"
    ```
    ./ci/scripts/create_version_pr.py
    ```

Otherwise follow these steps:

* Update `pyproject.toml`: Using `uv` Update the version according to the versioning schema above. Make sure you adhere to the versioning rules and only include alpha, beta, or rc for pre-release versions.

examples:
```
uv version --bump patch # 1.0.1 -> 1.0.2
uv version --bump minor # 1.0.1 -> 1.1.0
uv version --bump major # 1.0.1 -> 2.0.0

uv version 1.0.1-alpha.1 # set to pre-release version
uv version 1.0.1-beta.1 # set to pre-release version
uv version 1.0.1-rc.1 # set to pre-release version

```

* Run `uv sync` to update `uv.lock`.

* Create a pull request for the changes and merge to main.

### 2. Create a Release Tag
On the main branch, create a tag using the `ci/scripts/create_tag.py` script. The script will read the version from `pyproject.toml`
and create a tag with the correct format.

### 3. Update the Release Notes

* Wait for the [release workflow](https://github.com/cyberark/simple-llm-eval/actions/workflows/release.yml) to end successfully
* Manually open the release notes, click on "generate release notes" and update them as needed
* In the future this will be automated

### 4. Update the Changelog

* After the release workflow is complete, update the `CHANGELOG.md` file with the new version and the changes made in this release (take from the release notes).

### Release Workflow

The tag creation will trigger the GitHub Actions workflow [Release](https://github.com/cyberark/simple-llm-eval/actions/workflows/ci.yml)


!!! Abstract "Release Workflow"
    The release workflow will:
    - Validate the `pyproject.toml` version against the tag name
    - Build the package
    - Create GitHub release
    - Attach binaries to GitHub release
    - *Publish the package to PyPI
    - Publish the docs


### Docs Only Release
In case you make a docs-only update, see [Publishing the Docs](../developers/dev-notes.md/#publishing-the-docs)

<br>
