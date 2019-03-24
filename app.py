import datetime
import json

import requests
from flask import Flask, render_template, request

# define global variables here
GITHUB_ALL_ISSUES = 'https://api.github.com/repos/{}/issues?state=open'

# initializing flask app 
app = Flask(__name__)

@app.route('/', methods=['GET', 'POST'])
def home():
    """
    method for home page. Renders the default home page as well as form submitted
    """
    template_name = 'home.html'
    
    if request.method == 'GET':
        return render_template(template_name)

    repo_url = request.form['url']
    user_given_repo_url = repo_url
    # remove trailing slash if exists in url
    if repo_url.endswith('/'):
        repo_url = repo_url[:-1]

    repo_url = format_url(repo_url)
    issues_url = GITHUB_ALL_ISSUES.format(repo_url)

    # validate url before retrieving any data from github

    response_for_all_open_issues = requests.get(issues_url)

    if response_for_all_open_issues.status_code != 200:
        return render_template(
            template_name, 
            error={
                'message':'Not Found'
            }
        )

    # retrieve all open issues 
    all_open_issues_count = get_all_open_issues(issues_url)

    # retrieve issues opened in last 24hrs
    open_issues_count_in_last_24_hrs = get_open_issues_opened_in_last_24_hrs(issues_url)

    # Number of open issues that were opened more than 24 hours ago but less than 7 days ago
    open_issues_count_in_last_7_days = get_open_issues_opened_in_last_7_days(issues_url) - open_issues_count_in_last_24_hrs
    
    return render_template(template_name, context={
        'all_issues': all_open_issues_count,
        'opened_in_last_24_hrs': open_issues_count_in_last_24_hrs,
        'opened_in_last_7_days':open_issues_count_in_last_7_days,
        'opened_before_7_days': all_open_issues_count-open_issues_count_in_last_7_days,
        'user_repo_url': user_given_repo_url
    })

def format_url(repo_url):
    return "/".join(repo_url.split('/')[-2:])

def get_all_open_issues(repo_url):
    """
        Return the all open issues count for the given repo ( Public )
    """
    response_for_all_open_issues = requests.get(repo_url)
    jsonify_content = json.loads(response_for_all_open_issues.content)
    return len(jsonify_content)

def get_open_issues_opened_in_last_24_hrs(repo_url):
    """
        Return the all open issues count opened in last 24Hrs for the given repo ( Public )
    """
    last_24_hours_datetime = datetime.datetime.now()- datetime.timedelta(days=1)
    repo_url = repo_url + "&since={}".format(last_24_hours_datetime)
    response_for_all_open_issues = requests.get(repo_url)
    jsonify_content = json.loads(response_for_all_open_issues.content)
    return len(jsonify_content)

def get_open_issues_opened_in_last_7_days(repo_url):
    """
        Return the all open issues count opened in last 7 days for the given repo ( Public )
    """
    last_7_days_datetime = datetime.datetime.now()- datetime.timedelta(days=7)
    repo_url = repo_url + "&since={}".format(last_7_days_datetime)
    response_for_all_open_issues = requests.get(repo_url)
    jsonify_content = json.loads(response_for_all_open_issues.content)
    return len(jsonify_content)
