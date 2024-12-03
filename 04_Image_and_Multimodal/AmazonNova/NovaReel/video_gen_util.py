import json
import os
import time

import boto3


def save_invocation_info(invocation_result, model_input):
    invocation_arn = invocation_result["invocationArn"]

    # Create the Bedrock Runtime client.
    bedrock_runtime = boto3.client("bedrock-runtime")
    invocation_job = bedrock_runtime.get_async_invoke(invocationArn=invocation_arn)

    folder_name = get_folder_name_for_job(invocation_job)

    output_folder = os.path.abspath(f"output/{folder_name}")

    # Created the folder.
    os.makedirs(output_folder, exist_ok=True)

    # Save invocation_result as JSON file.
    with open(
        os.path.join(output_folder, "start_async_invoke_response.json"), "w"
    ) as f:
        json.dump(invocation_result, f, indent=2, default=str)

    # Save model_input as JSON file.
    with open(os.path.join(output_folder, "model_input.json"), "w") as f:
        json.dump(model_input, f, indent=2, default=str)

    return output_folder


def get_folder_name_for_job(invocation_job):
    invocation_arn = invocation_job["invocationArn"]
    invocation_id = invocation_arn.split("/")[-1]
    submit_time = invocation_job["submitTime"]
    timestamp = submit_time.astimezone().strftime("%Y-%m-%d_%H-%M-%S")
    folder_name = f"{timestamp}_{invocation_id}"
    return folder_name


def is_video_downloaded_for_invocation_job(invocation_job, output_folder="output"):
    """
    This function checks if the video file for the given invocation job has been downloaded.
    """
    invocation_arn = invocation_job["invocationArn"]
    invocation_id = invocation_arn.split("/")[-1]
    folder_name = get_folder_name_for_job(invocation_job)
    output_folder = os.path.abspath(f"{output_folder}/{folder_name}")
    file_name = f"{invocation_id}.mp4"
    local_file_path = os.path.join(output_folder, file_name)
    return os.path.exists(local_file_path)


def download_video_for_invocation_arn(invocation_arn, bucket_name, destination_folder):
    """
    This function downloads the video file for the given invocation ARN.
    """
    invocation_id = invocation_arn.split("/")[-1]

    # Create the local file path
    file_name = f"{invocation_id}.mp4"
    import os

    output_folder = os.path.abspath(destination_folder)
    local_file_path = os.path.join(output_folder, file_name)

    # Ensure the output folder exists
    os.makedirs(output_folder, exist_ok=True)

    # Create an S3 client
    s3 = boto3.client("s3")

    # List objects in the specified folder
    response = s3.list_objects_v2(Bucket=bucket_name, Prefix=invocation_id)

    # Find the first MP4 file and download it.
    for obj in response.get("Contents", []):
        object_key = obj["Key"]
        if object_key.endswith(".mp4"):
            print(f"""Downloading "{object_key}"...""")
            s3.download_file(bucket_name, object_key, local_file_path)
            print(f"Downloaded to {local_file_path}")
            return local_file_path

    # If we reach this point, no MP4 file was found.
    print(f"Problem: No MP4 file was found in S3 at {bucket_name}/{invocation_id}")


def elapsed_time_for_invocation_job(invocation_job):
    """
    This function returns the elapsed time for the given invocation job.
    """
    invocation_start_time = invocation_job["submitTime"].timestamp()
    if "endTime" in invocation_job:
        invocation_end_time = invocation_job["endTime"].timestamp()
        elapsed_time = int(invocation_end_time - invocation_start_time)
    else:
        elapsed_time = int(time.time() - invocation_start_time)

    return elapsed_time


def monitor_and_download_videos(output_folder="output", submit_time_after=None):
    # Create the Bedrock Runtime client.
    bedrock_runtime = boto3.client("bedrock-runtime")

    # Save failed jobs.
    failed_jobs_args = {"statusEquals": "Failed"}
    if submit_time_after is not None:
        failed_jobs_args["submitTimeAfter"] = submit_time_after

    failed_jobs = bedrock_runtime.list_async_invokes(**failed_jobs_args)

    for job in failed_jobs["asyncInvokeSummaries"]:
        save_failed_job(job)

    # Save completed jobs.
    completed_jobs_args = {"statusEquals": "Completed"}
    if submit_time_after is not None:
        completed_jobs_args["submitTimeAfter"] = submit_time_after

    completed_jobs = bedrock_runtime.list_async_invokes(**completed_jobs_args)

    for job in completed_jobs["asyncInvokeSummaries"]:
        save_completed_job(job)

    monitor_and_download_in_progress_videos(output_folder=output_folder)


def monitor_and_download_in_progress_videos(output_folder="output"):
    # Create the Bedrock Runtime client.
    bedrock_runtime = boto3.client("bedrock-runtime")

    invocation_list = bedrock_runtime.list_async_invokes(statusEquals="InProgress")
    in_progress_jobs = invocation_list["asyncInvokeSummaries"]

    pending_job_arns = [job["invocationArn"] for job in in_progress_jobs]

    print(f'Monitoring {len(pending_job_arns)} "InProgress" jobs.')

    while len(pending_job_arns) > 0:
        job_arns_to_remove = []
        for job_arn in pending_job_arns:
            # Get latest job status.
            job_update = bedrock_runtime.get_async_invoke(invocationArn=job_arn)
            status = job_update["status"]

            if status == "Completed":
                save_completed_job(job_update, output_folder=output_folder)
                job_arns_to_remove.append(job_arn)
            elif status == "Failed":
                save_failed_job(job_update, output_folder=output_folder)
                job_arns_to_remove.append(job_arn)
            else:
                job_id = get_job_id_from_arn(job_update["invocationArn"])
                elapsed_time = elapsed_time_for_invocation_job(job_update)
                minutes, seconds = divmod(elapsed_time, 60)
                # print(
                #     f"Job {job_id} is {status}. Elapsed time: {minutes}m, {seconds}s."
                # )
        for job_arn in job_arns_to_remove:
            pending_job_arns.remove(job_arn)

        time.sleep(10)

    print("Monitoring and download complete!")


def elapsed_time_for_invocation_arn(invocation_arn):
    # Create the Bedrock Runtime client.
    bedrock_runtime = boto3.client("bedrock-runtime")

    # Get the job details.
    invocation_job = bedrock_runtime.get_async_invoke(invocationArn=invocation_arn)

    return elapsed_time_for_invocation_job(invocation_job)


def elapsed_time_for_invocation_job(invocation_job):
    invocation_start_time = invocation_job["submitTime"].timestamp()
    if "endTime" in invocation_job:
        invocation_end_time = invocation_job["endTime"].timestamp()
        elapsed_time = int(invocation_end_time - invocation_start_time)
    else:
        elapsed_time = int(time.time() - invocation_start_time)

    return elapsed_time


def get_job_id_from_arn(invocation_arn):
    return invocation_arn.split("/")[-1]


def save_completed_job(job, output_folder="output"):
    job_id = get_job_id_from_arn(job["invocationArn"])

    output_folder_abs = os.path.abspath(
        f"{output_folder}/{get_folder_name_for_job(job)}"
    )

    # Ensure the output folder exists
    os.makedirs(output_folder_abs, exist_ok=True)

    status_file = os.path.join(output_folder_abs, "completed.json")

    if is_video_downloaded_for_invocation_job(job, output_folder=output_folder):
        print(f"Skipping completed job {job_id}, video already downloaded.")
        return

    s3_bucket_name = (
        job["outputDataConfig"]["s3OutputDataConfig"]["s3Uri"]
        .split("//")[1]
        .split("/")[0]
    )

    download_video_for_invocation_arn(
        job["invocationArn"], s3_bucket_name, output_folder_abs
    )

    # Write the status file to disk as JSON.
    with open(status_file, "w") as f:
        json.dump(job, f, indent=2, default=str)


def save_failed_job(job, output_folder="output"):
    output_folder_abs = os.path.abspath(
        f"{output_folder}/{get_folder_name_for_job(job)}"
    )
    output_file = os.path.join(output_folder_abs, "failed.json")

    job_id = get_job_id_from_arn(job["invocationArn"])

    # If the output file already exists, skip this job.
    if os.path.exists(output_file):
        print(f"Skipping failed job {job_id}, output file already exists.")
        return

    # Ensure the output folder exists
    os.makedirs(output_folder_abs, exist_ok=True)

    with open(output_file, "w") as f:
        print(f"Writing failed job {job_id} to {output_file}.")
        json.dump(job, f, indent=2, default=str)
