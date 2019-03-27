import datetime
import json
from dateutil import parser
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
    print (response_for_all_open_issues.status_code)
    if response_for_all_open_issues.status_code != 200:
        return render_template(
            template_name, 
            error={
                'message':'Not Found'
            }
        )

    # retrieve all open issues 
    all_issues = get_issues_recursively(issues_url)

    # retrieve issues opened in last 24hrs
    open_issues_count_in_last_24_hrs = 0

    # Number of open issues that were opened more than 24 hours ago but less than 7 days ago
    open_issues_count_in_last_7_days = 0
    
    all_open_issues_count = 0

    last_24_hours_datetime = datetime.datetime.now()- datetime.timedelta(days=1)
    last_7_days_datetime = datetime.datetime.now()- datetime.timedelta(days=7)

    
    for item in all_issues:
        if 'pull_request' not in item :
            all_open_issues_count += 1
            created_at = parser.parse(item['created_at'])
            created_at = created_at.replace(tzinfo=None)

            if created_at >= last_24_hours_datetime :
                open_issues_count_in_last_24_hrs += 1
            elif last_7_days_datetime <= created_at < last_24_hours_datetime :
                open_issues_count_in_last_7_days += 1


    return render_template(template_name, context={
        'all_issues': all_open_issues_count,
        'opened_in_last_24_hrs': open_issues_count_in_last_24_hrs,
        'opened_in_last_7_days':open_issues_count_in_last_7_days,
        'opened_before_7_days': all_open_issues_count-open_issues_count_in_last_7_days-open_issues_count_in_last_24_hrs,
        'user_repo_url': user_given_repo_url
    })

def format_url(repo_url):
    return "/".join(repo_url.split('/')[-2:])

def get_issues_recursively(repo_url):
    """
        utility function to retrive issues 
        ( per_page doesn't work for more than 100 in a single network call. 
        it returns max 100 at a time 
        ) 
    """
    page  = 1
    page_size = 100

    issues_fetched = 100
    all_issues = []
    repo_url = repo_url+ "&page={}&per_page=100"
    while issues_fetched == page_size:
        new_repo_url = repo_url.format(page)
        response = requests.get(new_repo_url)
        jsonify_content = json.loads(response.content)
        all_issues.extend(jsonify_content)
        issues_fetched = len(jsonify_content)
        page += 1

    return all_issues


