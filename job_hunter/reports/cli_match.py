from job_hunter.matching.rank import top_matches
from job_hunter.storage.jobs import fetch_job_by_id

def main():
    for job_id, score in top_matches("my-resume"):
        job = fetch_job_by_id(job_id)
        print(f"{score:.2f}  {job.title} – {job.company}  [{job.location}]")
        print(f"     {job.url}\n")

if __name__ == "__main__":
    main()
