# 1.1.0

- Enhance error handling and logging
- Migrate to `uv` package manager
- Update license references

# 1.0.0

- BREAKING CHANGE: Rename tool from `iac-test` to `nac-test`
- Modernize CLI interface using [typer](https://github.com/fastapi/typer)
- BREAKING CHANGE: Do not deduplicate items in a list of primitive values, for example a list of strings
- BREAKING CHANGE: Deduplicate items in a list of dictionaries consistently, regardless of whether they are in the same file or not
- Randomize pabot port to avoid conflicts with multiple instances of `nac-test` running in parallel
- Be more strict about undefined variables in Jinja templates

# 0.2.6

- Fix issue with directly nested lists in YAML files

# 0.2.5

- Add dry-run option
- Make Robot include and exclude tags available in render process (`robot_include_tags` and `robot_exclude_tags` variables)

# 0.2.4

- Also copy non-robot files to temporary directory used for executing the tests

# 0.2.3

- Handle file errors gracefully
- Allow empty YAML files

# 0.2.2

- Do not merge YAML dictionary list items, where each list item has unique attributes with primitive values

# 0.2.1

- Fix issue with YAML attributes named `tag`
- Fix multiple instances of `include` and `exclude` CLI arguments

# 0.2.0

- Add support for ansible-vault encrypted values
- Add `!env` tag to read values from environment variables

# 0.1.5

- Fix bug related to nested template directories

# 0.1.4

- Upgrade to Robot Framework 6.x
- Add option to provide CLI arguments as environment variables

# 0.1.3

- Add xUnit output (`xunit.xml`)

# 0.1.2

- Add custom Jinja tests
- Add iterate_list_folder rendering directive

# 0.1.1

- Add CLI options to select test cases by tag
- Add Requests and JSONlibrary

# 0.1.0

- Initial release
