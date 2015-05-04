import json
import requests

from subprocess import Popen

from .get_stats import (
    get_python_files,
    git_blame_on_files,
    apply_threshold_to_counter,
    output_counter_as_percent,
    get_test_coverage_percent_per_author,
)

POST_URL = "http://test-coverage-game.herokuapp.com/api/%s/"
FINAL_URL = "http://test-coverage-game.herokuapp.com/project/%s/"

SETTINGS_FILENAME = ".coveragegamerc"
REQUIRED_KEYS = (
    "test_run_command",
    "get_python_files_command",
    "project_identifier",
)
GENERIC_ERROR_MESSAGE = "%s must be a JSON file with the required keys: %s" % (SETTINGS_FILENAME, REQUIRED_KEYS)


def get_settings():

    try:
        with open(SETTINGS_FILENAME, "rb") as f:
            contents = f.read()
    except IOError:
        raise ValueError("Could not find settings file: " + GENERIC_ERROR_MESSAGE)
    try:
        settings_dict = json.loads(contents)
    except ValueError:
        raise ValueError("Settings file is not a JSON dictionary: " + GENERIC_ERROR_MESSAGE)
    for key in REQUIRED_KEYS:
        if key not in settings_dict:
            raise ValueError("%s is not listed in your settings file: " % key + GENERIC_ERROR_MESSAGE)
    return settings_dict


def run_tests(run_test_command):
    # virtual_env_bin_dir = sys.path[0]
    split_commands = run_test_command.split()
    for index in xrange(len(split_commands)):
        if "python" in split_commands[index]:
            split_commands[index] = "coverage"  # SBL to do need to replace with venv stuff
            split_commands.insert(index + 1, "run")
    process = Popen(split_commands)
    output, _ = process.communicate()


def get_coverage_data(get_python_files_cmd):
    # FIXME: this needs to get refactored
    python_files = get_python_files(get_python_files_cmd)
    line_counter, miss_counter = git_blame_on_files(python_files)
    apply_threshold_to_counter(line_counter)
    output_counter_as_percent(line_counter)
    author_to_test_coverage = get_test_coverage_percent_per_author(line_counter, miss_counter)
    final_data = {
        "line_counts": line_counter,
        "miss_counts": miss_counter,
        "test_coverage": author_to_test_coverage
    }
    return final_data


def run():
    settings_dict = get_settings()
    run_tests(settings_dict["test_run_command"])
    coverage_data = get_coverage_data(settings_dict["get_python_files_command"])
    for key in ("min_authors", "display_percent"):
        if key in settings_dict:
            coverage_data[key] = settings_dict[key]
    response = requests.post(POST_URL % settings_dict["project_identifier"], data=json.dumps(coverage_data))
    response.raise_for_status()
    print "Finished.  Results can be viewed at %s" (FINAL_URL % settings_dict["project_identifier"])
