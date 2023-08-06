
from collections import defaultdict
from datetime import datetime
from datetime import timedelta
import requests

def count_hours(start, end):
    total_hours = (end - start).seconds / 3600 + (end - start).days * 24
    return total_hours


def week_ending_date(date):
    return date + timedelta(days=(6-date.weekday()))

def fetch_reviews(pull_number, repo, headers):
    response = requests.get(f"https://api.github.com/repos/{repo}/pulls/{pull_number}/reviews", headers=headers)
    return response.json()

def process_pull_data(pull, daily_data, weekly_data, repo, headers):
    if pull['base']['ref'] != 'develop':
        return

    closed_at = datetime.strptime(pull['closed_at'], '%Y-%m-%dT%H:%M:%SZ')
    created_at = datetime.strptime(pull['created_at'], '%Y-%m-%dT%H:%M:%SZ')
    creator = pull['user']['login']

    reviews = fetch_reviews(pull['number'], repo, headers)

    first_review_time = None
    approver = None
    for review in reviews:
        if review['state'] in ['APPROVED', 'CHANGES_REQUESTED']:
            first_review_time = datetime.strptime(review['submitted_at'], '%Y-%m-%dT%H:%M:%SZ')
            approver = review['user']['login']
            break

    # Process daily data
    day = closed_at.date()
    if first_review_time:
        daily_data[day]['Open to Review Start'].append(count_hours(created_at, first_review_time))
        daily_data[day]['Review Start to Merge'].append(count_hours(first_review_time, closed_at))
    daily_data[day]['Open to Merge'].append(count_hours(created_at, closed_at))
    daily_data[day]['Number of PRs'] += 1
    daily_data[day]['Creators'][creator] += 1
    if approver:
        daily_data[day]['Approvers'][approver] += 1

    # Process weekly data
    week_end = week_ending_date(closed_at.date())
    if first_review_time:
        weekly_data[week_end]['Open to Review Start'].append(count_hours(created_at, first_review_time))
        weekly_data[week_end]['Review Start to Merge'].append(count_hours(first_review_time, closed_at))
    weekly_data[week_end]['Open to Merge'].append(count_hours(created_at, closed_at))
    weekly_data[week_end]['Number of PRs'] += 1
    weekly_data[week_end]['Creators'][creator] += 1
    if approver:
        weekly_data[week_end]['Approvers'][approver] += 1


def get_data_row(data, key, is_daily=True):
    if is_daily:
        day_string = key.strftime('%Y-%m-%d')
        avg_open_to_merge = sum(data['Open to Merge']) / len(data['Open to Merge']) if data['Open to Merge'] else 0
        avg_open_to_review = sum(data['Open to Review Start']) / len(data['Open to Review Start']) if data['Open to Review Start'] else 0
        avg_review_to_merge = sum(data['Review Start to Merge']) / len(data['Review Start to Merge']) if data['Review Start to Merge'] else 0

        creators_str = "\n".join([f"{name}: {count} PRs" for name, count in data['Creators'].items()])
        approvers_str = "\n".join([f"{name}: {count} approvals" for name, count in data['Approvers'].items()])

        return {
            'Date': day_string,
            'Open to Merge': avg_open_to_merge,
            'Open to Review Start': avg_open_to_review,
            'Review Start to Merge': avg_review_to_merge,
            'Number of PRs': data['Number of PRs'],
            'PR Creators': creators_str,
            'PR Approvers': approvers_str
        }

    else:
        week_start_str = (key - timedelta(days=6)).strftime('%Y-%m-%d')
        week_end_str = key.strftime('%Y-%m-%d')
        week_string = f"{week_start_str} to {week_end_str}"
        avg_open_to_merge = sum(data['Open to Merge']) / len(data['Open to Merge']) if data['Open to Merge'] else 0
        avg_open_to_review = sum(data['Open to Review Start']) / len(data['Open to Review Start']) if data['Open to Review Start'] else 0
        avg_review_to_merge = sum(data['Review Start to Merge']) / len(data['Review Start to Merge']) if data['Review Start to Merge'] else 0

        creators_str = "\n".join([f"{name}: {count} PRs" for name, count in data['Creators'].items()])
        approvers_str = "\n".join([f"{name}: {count} approvals" for name, count in data['Approvers'].items()])

        return {
            'Week': week_string,
            'Open to Merge': avg_open_to_merge,
            'Open to Review Start': avg_open_to_review,
            'Review Start to Merge': avg_review_to_merge,
            'Number of PRs': data['Number of PRs'],
            'PR Creators': creators_str,
            'PR Approvers': approvers_str
        }
