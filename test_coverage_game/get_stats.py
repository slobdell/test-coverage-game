import json
import sys
from subprocess import Popen, PIPE
from collections import Counter
# .virtualenv/bin/coverage run manage.py test


class ExcludeLineParser(object):

    @classmethod
    def get_missing_lines_for_filename(cls, filename):
        command = "../.virtualenv/bin/coverage report -m %s" % filename
        command = "coverage report -m %s" % filename
        process = Popen(command.split(), stdout=PIPE)
        output, _ = process.communicate()
        return cls._get_excluded_lines(output)

    @classmethod
    def _get_excluded_lines(cls, coverage_output):
        excluded_line_numbers = []
        ignore_line_count = 2
        ignore_column_count = 4
        lines = [line for line in coverage_output.split("\n")[ignore_line_count:] if line]
        for line in lines:
            exclude_line_strings = line.split()[ignore_column_count:]
            for exclude_line_string in exclude_line_strings:
                exclude_line_string = exclude_line_string.replace(",", "").replace(" ", "")
                exclude_lines = cls._convert_exclude_line_string_to_ints(exclude_line_string)
                excluded_line_numbers.extend(exclude_lines)

        return excluded_line_numbers

    @classmethod
    def _convert_exclude_line_string_to_ints(cls, exclude_line_string):
        if "-" in exclude_line_string:
            try:
                line_start, line_end = exclude_line_string.split("-")
            except:
                print "Error on: %s" % exclude_line_string
                return []
            return range(int(line_start), int(line_end) + 1)
        else:
            try:
                line_number = int(exclude_line_string)
            except ValueError:
                print "Error for values (%s)" % exclude_line_string
                return []
            return [line_number]

LINE_COUNT_THRESH = 100


def _get_output_from_pipe_command(command_with_pipes):
    piped_commands = [command.strip() for command in command_with_pipes.split("|")]
    previous_process = None
    for command in piped_commands:
        process = Popen(command.split(), stdin=previous_process and previous_process.stdout, stdout=PIPE)
        previous_process = process
    output, err = previous_process.communicate()
    return output


def get_python_files(full_command):
    '''
    EXAMPLE:
    full_command = "find . | grep py | grep -v pyc | grep -v \.un | grep -v test | grep -v virtualenv | grep -v \.swp"
    '''
    output = _get_output_from_pipe_command(full_command)
    filenames = [filename for filename in output.split("\n") if filename]
    return filenames


def git_blame_on_files(file_list):
    total_counter = Counter()
    miss_counter = Counter()
    files_to_process = len(file_list)
    for index, filename in enumerate(file_list):
        full_command = "git blame --line-porcelain %s | grep author | grep -v author-" % filename
        output = _get_output_from_pipe_command(full_command)

        git_scorer = GitScorer(output)
        counter = git_scorer.get_author_counts()

        line_to_author = git_scorer.get_line_to_author()
        non_covered_lines = ExcludeLineParser.get_missing_lines_for_filename(filename)
        miss_counter += attribute_missing_coverage_to_author(line_to_author, non_covered_lines)

        total_counter += counter
        if index % 50 == 0:
            print "%s percent complete" % ((index / float(files_to_process)) * 100.0)
    return total_counter, miss_counter


def output_counter_as_percent(counter):
    total_lines = float(sum(counter.values()))
    rank = 1
    for author, line_count in sorted(counter.items(), key=lambda t: t[1], reverse=True):
        print "%s: %s: %s %%" % (rank, author, format((line_count * 100.0) / total_lines, '.2f'))
        rank += 1


def apply_threshold_to_counter(counter):
    for key in counter.keys():
        if counter[key] < LINE_COUNT_THRESH:
            del counter[key]


def attribute_missing_coverage_to_author(line_to_author, non_covered_lines):
    author_to_miss_count = Counter()
    for line_number in non_covered_lines:
        try:
            author = line_to_author[line_number]
        except KeyError:
            return Counter()
        author_to_miss_count[author] += 1
    return author_to_miss_count


class GitScorer(object):

    def __init__(self, gblame_output):
        self.counts_this_file = Counter()
        self.line_to_author = {}
        self._parse_git_blame_output(gblame_output)

    def _get_author_from_line(self, line):
        author = line.replace("author ", "")
        if author.startswith(" ") or author.startswith("\t"):
            return None
        return author

    def _parse_git_blame_output(self, git_blame_output):
        lines = git_blame_output.split("\n")
        for index, line in enumerate(lines):
            if not line:
                continue
            line_number = index + 1
            author = self._get_author_from_line(line)
            if author:
                self.counts_this_file[author] += 1
            self.line_to_author[line_number] = author

    def get_author_counts(self):
        return self.counts_this_file

    def get_line_to_author(self):
        return self.line_to_author


def get_test_coverage_percent_per_author(line_counter, miss_counter):
    author_to_test_coverage = {}
    for author in line_counter.keys():
        line_count = line_counter[author]
        miss_count = miss_counter.get(author, 0)
        miss_percent = float(miss_count) / line_count
        test_coverage_percent = 1.0 - miss_percent
        author_to_test_coverage[author] = test_coverage_percent
    return author_to_test_coverage


if __name__ == "__main__":
    python_files = get_python_files(sys.argv[1])
    line_counter, miss_counter = git_blame_on_files(python_files)
    apply_threshold_to_counter(line_counter)
    output_counter_as_percent(line_counter)
    author_to_test_coverage = get_test_coverage_percent_per_author(line_counter, miss_counter)
    with open("test_coverage_results.json", "w+") as f:
        final_data = {
            "line_counts": line_counter,
            "miss_counts": miss_counter,
            "test_coverage": author_to_test_coverage
        }
        f.write(json.dumps(final_data, indent=4))
