# Git Commit Histogram

This project generates an HTML report that visualizes the commit activity of users in a Git repository over the last 52 weeks. The report includes a histogram that highlights the number of repo actions per day, namely commits.

See [demo.png](https://github.com/goliath-dynamics/git-commit-histogram/blob/main/demo.png) for example output.

## Why

Activity histograms are a great way to see user's code contributions.  While number of lines of code or number of commits are not a quantitative determinant of performance, activity histograms are incredibly useful to provide transparency on who is getting work done and who isn't.  Especially in remote companies, this becomes imperative to check up on.

Github already has individual user histograms, but other repo managers often don't (cough, BitBucket, cough).  This package doesn't concern itself as to which platform you're using.

Also, this allows team leads to get a better overview of the entire repo, all users on one page.  Team managers can use this to check in on whether devs are actually committing code.  Teams can also use it as social pressure to get the underperformers to see how much more weight others are pulling.

## Features

- Generates an HTML report with commit histograms for each user.
- Combines user activity based on email addresses.
- Excludes users in the repo with no commits in the last year.
- Colors cells based on the number of commits:
  - Dark green for many commits.
  - Light green for fewer commits.
  - White for no commits.
  - Grey for weekends with no commits, and the days of this week that are still in the future.
- Includes the date and timestamp of when the report was generated.

## Requirements

- Python 3.x
- Git

## Installation

1. Clone the repository:
    ```sh
    git clone <repository-url>
    ```
2. Navigate to the project directory:
    ```sh
    cd git-commit-histogram
    ```

## Usage Example

Run the script with the path to the Git repository and the output HTML file path:

```sh
python git_commit_histogram.py -r="relative/path/to/git/repo"
```

## Arguments

- `-r`, `--repo`: Path to the Git repository. (default is present working directory).
- `-o`, `--output`: Output HTML file path (default: `commit_histogram.html`).

## License

This project is licensed under the MIT License.
