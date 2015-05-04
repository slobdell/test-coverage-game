[Homepage](http://test-coverage-game.herokuapp.com)

# About

The Test Coverage Game package is meant to be an installable package that posts the results to a public wep application.  The motivation behind the project is to gamify the task of test coverage between the collaborators of your git project.

# Usage

* Install the package with ```
pip install git+git://github.com/slobdell/test-coverage-game.git```
* From your project's root, edit ```
.coveragegamerc``` with required settings.  Sample file is below
* Run ```test-coverage-game``` from your project root

# Sample .coveragegamerc File
```
{
    "test_run_command": "venv/bin/python setup.py test",
    "get_python_files_command": "find . | grep py | grep -v pyc | grep -v \\.un | grep -v test | grep -v virtualenv ",
    "min_authors": 5,
    "display_percent": 0.3,
    "project_identifier": "test_run"
}
```
* ```test_run_command``` denotes the command you'd normally use to run tests.  Must include a ```python``` command
* ```get_python_files_command``` is what you'd run from the shell to list all of the testable python files
* ```project_identifier``` is a unique string to identify your project.  This is currently not globally enforced
* ```min_authors``` sets the minimum number of authors to display on the results (good for small projects where top % might be too small)
* ```display_percent``` denotes the top percentage of "players" to display in the results (so as not to embarass new team members or otherwise demoralize collaborators)

# To View Results
* visit http://test-coverage-game.herokuapp.com/project/{project_identifier}/
* To view results for a particular date: http://test-coverage-game.herokuapp.com/project/{project_identifier}/{yy}/{mm}/{dd}/
