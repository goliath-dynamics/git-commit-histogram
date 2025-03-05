import os
import subprocess
import argparse
from collections import defaultdict
from datetime import datetime, timedelta
import re

def get_git_log(repo_path):
    os.chdir(repo_path)
    log_format = '--pretty=format:"%an|%ae|%at|%s"'
    result = subprocess.run(['git', 'log', log_format], capture_output=True, text=True)
    # print (result.stdout.strip().split('\n'))
    return result.stdout.strip().split('\n')

def get_branch_name(repo_path):
    os.chdir(repo_path)
    result = subprocess.run(['git', 'rev-parse', '--abbrev-ref', 'HEAD'], capture_output=True, text=True)
    return result.stdout.strip()

def get_repo_name(repo_path):
    os.chdir(repo_path)
    result = subprocess.run(['git', 'remote', 'get-url', 'origin'], capture_output=True, text=True)
    return result.stdout.strip()

def is_valid_timestamp(timestamp):
    try:
        int(timestamp)
        return True
    except ValueError:
        return False

def parse_git_log(log_lines):
    user_info = defaultdict(lambda: {'name': '', 'commits': defaultdict(int)})
    log_pattern = re.compile(r'^(.*?)\|(.*?)\|(.*?)\|(.*)$')
    for line in log_lines:
        match = log_pattern.match(line.strip('"'))
        if match:
            name, email, timestamp, subject = match.groups()
            email = email.lower()
            user_info[email]['name'] = name
            if is_valid_timestamp(timestamp):
                date = datetime.fromtimestamp(int(timestamp)).date()
                user_info[email]['commits'][date] += 1
                if any(keyword in subject.lower() for keyword in ['branch', 'stash', 'revert', 'amend', 'tag']):
                    user_info[email]['commits'][date] += 1
            else:
                print(f"Invalid timestamp: {timestamp}")
                # Handle the invalid timestamp case (e.g., skip, log, etc.)
    return user_info

def get_last_fetch_time(repo_path):
    fetch_head_path = os.path.join(repo_path, '.git', 'FETCH_HEAD')
    if os.path.exists(fetch_head_path):
        fetch_time = datetime.fromtimestamp(os.path.getmtime(fetch_head_path))
        return fetch_time.strftime('%Y-%m-%d %H:%M:%S')
    return "N/A"

def filter_recent_users(user_info):
    one_year_ago = datetime.now().date() - timedelta(weeks=52)
    recent_user_info = {}
    for email, info in user_info.items():
        recent_commits = {date: count for date, count in info['commits'].items() if date >= one_year_ago}
        if recent_commits:
            recent_user_info[email] = {'name': info['name'], 'commits': recent_commits}
    return recent_user_info

def generate_html(user_info, repo_name, last_fetch_time, branch_name):
    report_generated_at = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    master_branches = ['master', 'main', 'latest']
    is_master_branch = branch_name in master_branches

    all_dates = [date for user in user_info.values() for date in user['commits'].keys()]
    last_activity_date = max(all_dates).strftime('%Y-%m-%d')

    html_content = "<html><head><title>Git Log Histogram</title></head><body>"
    html_content += """
    <h1>Git Log Histogram</h1>
    <p>This report shows repo activity of each contributing user in the last year.</p>
    <table style="border-collapse:collapse;border:0px;">
"""
    html_content += f"<tr><td nowrap><b>Report Generated</b></td><td nowrap>{report_generated_at}</td></tr>"
    html_content += f"<tr><td><b>Repository</b></td><td>{repo_name}</td></tr>"
    html_content += f"<tr><td><b>Branch</b></td><td>{branch_name} {'' if is_master_branch else '<span style="border-radius:3px;padding:3px 5px; font-weight:bold;color:red;background:pink;" title="Not on a master branch">!</span>'}</td></tr>"
    html_content += f"<tr><td><b>Last fetch/pull</b></td><td>{last_fetch_time}</td></tr>"
    html_content += f"<tr><td><b>Last activity</b></td><td>{last_activity_date}</td></tr></table>"
    html_content += """
    <p>The histograms below show the number of commits made by each user on each day of the week.  Each column represents a week, each day a cell.  This covers the last year, inclusive of the week before and current week.  Dark green means 5+ actions that day, light green means less than 5 but more than 0 actions that day.</p>
    <p>User contributions are deduped by email address (combined into the same histogram).  Any user who has no activity in the last year is not shown.</p>
    <p>The <b>last activity</b> date is based on what's actively in this exact repo right now.  You will want to stash any changes and `git pull origin` if this appears old or outdated.  Also check what branch you're on -- you'll usually want it to be master/main.</p>
    
    <style>
        * { font-family: Arial, sans-serif; }
        p { font-size:80%;color:#666;max-width:1135px;}
        td { border: 0px; padding:0px;padding:3px 5px;}
        .histogram {border-collapse: collapse;}
        .histogram td { border: 1px solid #999; margin:0px;padding:0px;width: 20px; height: 20px;}
        .few-commits { background-color: lightgreen; }
        .many-commits { background-color: darkgreen; }
        .weekend-no-commits { background-color: lightgrey; }
        .future-commits { background-color: lightgrey; }
    </style>
    """
    for email, info in user_info.items():
        html_content += f"<h2>{info['name']} ({email})</h2>"
        html_content += "<table class='histogram'>"
        for day in range(7):
            html_content += "<tr>"
            for week in range(54):  # 52 weeks + 2 extra columns
                week_start = (datetime.now() - timedelta(weeks=53-week)).date()
                week_start = week_start - timedelta(days=(week_start.weekday() + 1) % 7)  # Ensure week starts on Monday
                date = week_start + timedelta(days=day)
                commits = info['commits'].get(date, 0)
                day_of_week = date.strftime('%A')
                if date > datetime.now().date():
                    cell_class = "future-commits"
                elif commits == 0:
                    if day_of_week in ['Saturday', 'Sunday']:
                        cell_class = "weekend-no-commits"
                    else:
                        cell_class = "" # no-commits
                elif commits < 5:
                    cell_class = "few-commits"
                else:
                    cell_class = "many-commits"
                html_content += f"<td class='{cell_class}' title='{date} ({day_of_week})'></td>"
            html_content += "</tr>"
        html_content += "</table>"
    html_content += "</body></html>"
    html_content += "<p>Report generated by <a href='https://github.com/goliath-dynamics/git-commit-histogram' target='_blank'>git-commit-histogram</a> by David Loschiavo @ Goliath Dynamic Inc.</p>"
    return html_content

def save_html(content, output_path):
    with open(output_path, 'w') as file:
        file.write(content)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Generate an HTML file with user commit histograms for a Git repository.")
    parser.add_argument("-r", "--repo", default=".", help="Path to the git repository")
    parser.add_argument("-o", "--output", default="commit-histogram.html", help="Output HTML file path")
    parser.add_argument("-d", "--days_off", default="Saturday, Sunday", help="Non-working days")
    args = parser.parse_args()

    repo_path = args.repo
    if repo_path.startswith("-r="):
        repo_path = repo_path[3:]
    if repo_path.startswith("--repo="):
        repo_path = repo_path[7:]
    repo_path = os.path.abspath(os.path.join(os.getcwd(), repo_path))
    if not os.path.isdir(repo_path):
        raise FileNotFoundError(f"The directory '{repo_path}' does not exist.")

    branch_name = get_branch_name(repo_path)
    repo_name = get_repo_name(repo_path)
    last_fetch_time = get_last_fetch_time(repo_path)
    log_lines = get_git_log(repo_path)
    user_info = parse_git_log(log_lines)
    recent_user_info = filter_recent_users(user_info)
    html_content = generate_html(recent_user_info, repo_name, last_fetch_time, branch_name)
    save_html(html_content, args.output)
    print(f"HTML file generated at {args.output}")
