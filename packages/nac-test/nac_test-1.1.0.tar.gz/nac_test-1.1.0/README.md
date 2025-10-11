[![Tests](https://github.com/netascode/nac-test/actions/workflows/test.yml/badge.svg)](https://github.com/netascode/nac-test/actions/workflows/test.yml)
![Python Support](https://img.shields.io/badge/python-3.10%20%7C%203.11%20%7C%203.12%20%7C%203.13-informational "Python Support: 3.10, 3.11, 3.12, 3.13")

# nac-test

A CLI tool to render and execute [Robot Framework](https://robotframework.org/) tests using [Jinja](https://jinja.palletsprojects.com/) templating. Combining Robot's language agnostic syntax with the flexibility of Jinja templating allows dynamically rendering a set of test suites from the desired infrastructure state expressed in YAML syntax.

```
$ nac-test --help

 Usage: nac-test [OPTIONS]                                                      
                                                                                
 A CLI tool to render and execute Robot Framework tests using Jinja templating. 
                                                                                
╭─ Options ────────────────────────────────────────────────────────────────────╮
│ *  --data         -d      PATH                     Path to data YAML files.  │
│                                                    [env var: NAC_TEST_DATA]  │
│                                                    [required]                │
│ *  --templates    -t      DIRECTORY                Path to test templates.   │
│                                                    [env var:                 │
│                                                    NAC_TEST_TEMPLATES]       │
│                                                    [required]                │
│ *  --output       -o      DIRECTORY                Path to output directory. │
│                                                    [env var:                 │
│                                                    NAC_TEST_OUTPUT]          │
│                                                    [required]                │
│    --filters      -f      DIRECTORY                Path to Jinja filters.    │
│                                                    [env var:                 │
│                                                    NAC_TEST_FILTERS]         │
│    --tests                DIRECTORY                Path to Jinja tests.      │
│                                                    [env var: NAC_TEST_TESTS] │
│    --include      -i      TEXT                     Selects the test cases by │
│                                                    tag (include).            │
│                                                    [env var:                 │
│                                                    NAC_TEST_INCLUDE]         │
│    --exclude      -e      TEXT                     Selects the test cases by │
│                                                    tag (exclude).            │
│                                                    [env var:                 │
│                                                    NAC_TEST_EXCLUDE]         │
│    --render-only                                   Only render tests without │
│                                                    executing them.           │
│                                                    [env var:                 │
│                                                    NAC_TEST_RENDER_ONLY]     │
│    --dry-run                                       Dry run flag. See robot   │
│                                                    dry run mode.             │
│                                                    [env var:                 │
│                                                    NAC_TEST_DRY_RUN]         │
│    --verbosity    -v      [DEBUG|INFO|WARNING|ERR  Verbosity level.          │
│                           OR|CRITICAL]             [env var:                 │
│                                                    NAC_VALIDATE_VERBOSITY]   │
│                                                    [default: WARNING]        │
│    --version                                       Display version number.   │
│    --help                                          Show this message and     │
│                                                    exit.                     │
╰──────────────────────────────────────────────────────────────────────────────╯
```

All data from the YAML files (`--data` option) will first be combined into a single data structure which is then provided as input to the templating process. Each template in the `--templates` path will then be rendered and written to the `--output` path. If the `--templates` path has subfolders, the folder structure will be retained when rendering the templates.

After all templates have been rendered [Pabot](https://pabot.org/) will execute all test suites in parallel and create a test report in the `--output` path. The `--skiponfailure non-critical` argument will be used by default, meaning all failed tests with a `non-critical` tag will show up as "skipped" instead of "failed" in the final test report.

## Installation

Python 3.10+ is required to install `nac-test`. Don't have Python 3.10 or later? See [Python 3 Installation & Setup Guide](https://realpython.com/installing-python/).

`nac-validate` can be installed in a virtual environment using `pip` or `uv`:

```bash
# Using pip
pip install nac-test

# Using uv (recommended)
uv tools install nac-test
```

The following Robot libraries are included with `nac-test`:

- [RESTinstance](https://github.com/asyrjasalo/RESTinstance) (≥1.5.2)
- [robotframework-requests](https://github.com/MarketSquare/robotframework-requests) (≥0.9.7)
- [robotframework-jsonlibrary](https://github.com/robotframework-thailand/robotframework-jsonlibrary) (≥0.5)
- [robotframework-pabot](https://pabot.org/) (≥4.3.2) for parallel test execution

Any other libraries can of course be added via `pip` or `uv`.

## Ansible Vault Support

Values in YAML files can be encrypted using [Ansible Vault](https://docs.ansible.com/ansible/latest/user_guide/vault.html). This requires Ansible (`ansible-vault` command) to be installed and the following two environment variables to be defined:

```
export ANSIBLE_VAULT_ID=dev
export ANSIBLE_VAULT_PASSWORD=Password123
```

`ANSIBLE_VAULT_ID` is optional, and if not defined will be omitted.

## Additional Tags

### Reading Environment Variables

The `!env` YAML tag can be used to read values from environment variables.

```yaml
root:
  name: !env VAR_NAME
```

## Example

`data.yaml` located in `./data` folder:

```yaml
---
root:
  children:
    - name: ABC
      param: value
    - name: DEF
      param: value
```

`test1.robot` located in `./templates` folder:

```
*** Settings ***
Documentation   Test1

*** Test Cases ***
{% for child in root.children | default([]) %}

Test {{ child.name }}
    Should Be Equal   {{ child.param }}   value
{% endfor %}
```

After running `nac-test` with the following parameters:

```shell
nac-test --data ./data --templates ./templates --output ./tests
```

The following rendered Robot test suite can be found in the `./tests` folder:

```
*** Settings ***
Documentation   Test1

*** Test Cases ***

Test ABC
    Should Be Equal   value   value

Test DEF
    Should Be Equal   value   value
```

As well as the test results and reports:

```shell
$ tree -L 1 tests
tests
├── log.html
├── output.xml
├── pabot_results
├── report.html
├── test1.robot
└── xunit.xml
```

## Custom Jinja Filters

Custom Jinja filters can be used by providing a set of Python classes where each filter is implemented as a separate `Filter` class in a `.py` file located in the `--filters` path. The class must have a single attribute named `name`, the filter name, and a `classmethod()` named `filter` which has one or more arguments. A sample filter can be found below.

```python
class Filter:
    name = "filter1"

    @classmethod
    def filter(cls, data):
        return str(data) + "_filtered"
```

## Custom Jinja Tests

Custom Jinja tests can be used by providing a set of Python classes where each test is implemented as a separate `Test` class in a `.py` file located in the `--tests` path. The class must have a single attribute named `name`, the test name, and a `classmethod()` named `test` which has one or more arguments. A sample test can be found below.

```python
class Test:
    name = "test1"

    @classmethod
    def test(cls, data1, data2):
        return data1 == data2
```

## Rendering Directives

Special rendering directives exist to render a single test suite per (YAML) list item. The directive can be added to the Robot template as a Jinja comment following this syntax:

```
{# iterate_list <YAML_PATH_TO_LIST> <LIST_ITEM_ID> <JINJA_VARIABLE_NAME> #}
```

After running `nac-test` with the data from the previous [example](#example) and the following template:

```
{# iterate_list root.children name child_name #}
*** Settings ***
Documentation   Test1

*** Test Cases ***
{% for child in root.children | default([]) %}
{% if child.name == child_name %}

Test {{ child.name }}
    Should Be Equal   {{ child.param }}   value
{% endif %}
{% endfor %}
```

The following test suites will be rendered:

```shell
$ tree -L 2 tests
tests
├── ABC
│   └── test1.robot
└── DEF
    └── test1.robot
```

A similar directive exists to put the test suites in a common folder though with a unique filename.

```
{# iterate_list_folder <YAML_PATH_TO_LIST> <LIST_ITEM_ID> <JINJA_VARIABLE_NAME> #}
```

The following test suites will be rendered:

```shell
$ tree -L 2 tests
tests
└── test1
    ├── ABC.robot
    └── DEF.robot
```

## Select Test Cases By Tag

It is possible to include and exclude test cases by tag names with the `--include` and `--exclude` CLI options. These options are directly passed to the Pabot/Robot executor and are documented [here](https://robotframework.org/robotframework/latest/RobotFrameworkUserGuide.html#by-tag-names).
