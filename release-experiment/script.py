import os
import requests
import pandas as pd
import numpy as np
from scipy.stats import mannwhitneyu


def get_request(url, headers):
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        return response.json()
    else:
        raise Exception(f"Request failed with status code {response.status_code}")


def fetch_workflow_runtimes(
    token, repo_name, workflow_id, workflow_type, total_count=8
):
    headers = {"Authorization": f"token {token}"}
    runtimes = []

    if workflow_type == "release notes":
        # Fetch the last `runtimes_count` successful workflow runtimes from GitHub Actions.
        api_url = f"https://api.github.com/repos/{repo_name}/actions/workflows/{workflow_id}/runs?status=success"
        response = get_request(api_url, headers)
        workflow_runs = response["workflow_runs"][:total_count]
        for run in workflow_runs:
            # Calculate runtime in minutes
            start_time = run["created_at"]
            end_time = run["updated_at"]
            runtime = (
                pd.to_datetime(end_time) - pd.to_datetime(start_time)
            ).seconds / 60.0
            runtimes.append(runtime)
    elif workflow_type == "release":
        api_url = f"https://api.github.com/repos/{repo_name}/actions/workflows/{workflow_id}/runs?status=success"
        response = get_request(api_url, headers)
        workflow_runs = response["workflow_runs"][:total_count]
        for run in workflow_runs:
            run_id = run["id"]
            api_url = (
                f"https://api.github.com/repos/{repo_name}/actions/runs/{run_id}/jobs"
            )
            response = get_request(api_url, headers)
            release_job = next(
                (job for job in response["jobs"] if job["name"] == "release"), None
            )
            if release_job is None or release_job["conclusion"] != "success":
                continue
            start_time = release_job["started_at"]
            end_time = release_job["completed_at"]
            runtime = (
                pd.to_datetime(end_time) - pd.to_datetime(start_time)
            ).seconds / 60.0
            runtimes.append(runtime)
    elif workflow_type == "publish release":
        api_url = f"https://api.github.com/repos/{repo_name}/actions/workflows/{workflow_id}/runs"
        response = get_request(api_url, headers)
        workflow_runs = response["workflow_runs"]
        for run in workflow_runs:
            if len(runtimes) >= total_count:
                break
            run_id = run["id"]
            api_url = (
                f"https://api.github.com/repos/{repo_name}/actions/runs/{run_id}/jobs"
            )
            response = get_request(api_url, headers)
            email_job = next(
                (
                    job
                    for job in response["jobs"]
                    if job["name"] == "send-announcement-email"
                ),
                None,
            )
            if email_job is None or email_job["conclusion"] != "success":
                continue
            start_time = email_job["started_at"]
            end_time = email_job["completed_at"]
            runtime = (
                pd.to_datetime(end_time) - pd.to_datetime(start_time)
            ).seconds / 60.0
            runtimes.append(runtime)
    return runtimes


def main():
    GITHUB_TOKEN = os.environ["GITHUB_TOKEN"]
    REPO_NAME = os.environ["REPO_NAME"]
    RELEASE_NOTES_WORKFLOW_ID = os.environ["RELEASE_NOTES_WORKFLOW_ID"]
    RELEASE_WORKFLOW_ID = os.environ["RELEASE_WORKFLOW_ID"]
    PUBLISH_RELEASE_WORKFLOW_ID = os.environ["PUBLISH_RELEASE_WORKFLOW_ID"]

    # Manual execution runtimes for comparison
    release_notes_manual_runtimes = [15, 3, 7, 3, 10, 5, 8, 4]
    release_manual_runtimes = [20, 5, 26, 6, 15, 4, 19, 7]
    publish_release_manual_runtimes = [2, 3, 5, 4, 5, 3, 4, 3]

    # Fetch workflow runtimes and perform Mann-Whitney U test
    release_notes_workflow_runtimes = fetch_workflow_runtimes(
        GITHUB_TOKEN, REPO_NAME, RELEASE_NOTES_WORKFLOW_ID, "release notes"
    )
    _, p_value1 = mannwhitneyu(
        release_notes_workflow_runtimes,
        release_notes_manual_runtimes,
        alternative="two-sided",
    )
    workflow_mean1 = np.mean(release_notes_workflow_runtimes)
    manual_mean1 = np.mean(release_notes_manual_runtimes)
    workflow_std_dev1 = np.std(release_notes_workflow_runtimes)
    manual_std_dev1 = np.std(release_notes_manual_runtimes)

    release_workflow_runtimes = fetch_workflow_runtimes(
        GITHUB_TOKEN, REPO_NAME, RELEASE_WORKFLOW_ID, "release"
    )
    _, p_value2 = mannwhitneyu(
        release_workflow_runtimes,
        release_manual_runtimes,
        alternative="two-sided",
    )
    workflow_mean2 = np.mean(release_workflow_runtimes)
    manual_mean2 = np.mean(release_manual_runtimes)
    workflow_std_dev2 = np.std(release_workflow_runtimes)
    manual_std_dev2 = np.std(release_manual_runtimes)

    publish_release_workflow_runtimes = fetch_workflow_runtimes(
        GITHUB_TOKEN, REPO_NAME, PUBLISH_RELEASE_WORKFLOW_ID, "publish release"
    )
    _, p_value3 = mannwhitneyu(
        publish_release_workflow_runtimes,
        publish_release_manual_runtimes,
        alternative="two-sided",
    )
    workflow_mean3 = np.mean(publish_release_workflow_runtimes)
    manual_mean3 = np.mean(publish_release_manual_runtimes)
    workflow_std_dev3 = np.std(publish_release_workflow_runtimes)
    manual_std_dev3 = np.std(publish_release_manual_runtimes)

    print(
        f"Release Notes workflow runtimes (in minutes): {np.round(release_notes_workflow_runtimes, 2)}"
    )
    print(
        f"Mean: {workflow_mean1:.2f}, Standard deviation: {workflow_std_dev1:.2f}, N: {len(release_notes_workflow_runtimes)}"
    )
    print(
        f"Release Notes manual runtimes (in minutes): {np.round(release_notes_manual_runtimes, 2)}"
    )
    print(
        f"Mean: {manual_mean1:.2f}, Standard deviation: {manual_std_dev1:.2f}, N: {len(release_notes_manual_runtimes)}"
    )
    print(f"P-value: {p_value1:.5f}")
    print()
    print(
        f"Release workflow runtimes (in minutes): {np.round(release_workflow_runtimes,2)}"
    )
    print(
        f"Mean: {workflow_mean2:.2f}, Standard deviation: {workflow_std_dev2:.2f}, N: {len(release_workflow_runtimes)}"
    )
    print(f"Release manual runtimes (in minutes): {np.round(release_manual_runtimes)}")
    print(
        f"Mean: {manual_mean2:.2f}, Standard deviation: {manual_std_dev2:.2f}, N: {len(release_manual_runtimes)}"
    )
    print(f"P-value: {p_value2:.5f}")
    print()
    print(
        f"Publish Release workflow runtimes (in minutes): {np.round(publish_release_workflow_runtimes, 2)}"
    )
    print(
        f"Mean: {workflow_mean3:.2f}, Standard deviation: {workflow_std_dev3:.2f}, N: {len(publish_release_workflow_runtimes)}"
    )
    print(
        f"Publish Release manual runtimes (in minutes): {np.round(publish_release_manual_runtimes, 2)}"
    )
    print(
        f"Mean: {manual_mean3:.2f}, Standard deviation: {manual_std_dev3:.2f}, N: {len(publish_release_manual_runtimes)}"
    )
    print(f"P-value: {p_value3:.5f}")


if __name__ == "__main__":
    main()
