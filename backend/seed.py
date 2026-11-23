import subprocess
import os
import relate

DB_PATH = os.getenv("RELATE_DB", "./data/campus.rl")

def run_ingest(repo_dir: str):
    print(f"Ingesting git repository from {repo_dir} into {DB_PATH}...")
    subprocess.run(["relate", "run", "git-to-graph", repo_dir, "-d", DB_PATH], check=True)
    print(f"Ingesting file system from {repo_dir}...")
    subprocess.run(["relate", "run", "fs-to-graph", repo_dir, "-d", DB_PATH], check=True)

def seed_custom_domain():
    conn = relate.connect(DB_PATH)

    # 1. Seed custom domain nodes
    conn.execute("""
        MERGE (p:Project {name: "CampusContext"})
        MERGE (f:Feature {id: "JIRA-101", title: "Smart Contributor Routing", description: "Match contributors to project needs using Git history"})
        MERGE (s:Skill {id: "python", name: "Python / FastAPI"})
        MERGE (sug:Suggestion {id: "sug-1", text: "Assign contributor author@campus.edu based on prior commits"})

        MERGE (f)-[:BELONGS_TO]->(p)
        MERGE (f)-[:NEEDS_SKILL]->(s)
        MERGE (f)-[:SUGGESTED_FOR]->(sug)
    """)

    # 2. Link Feature to real ingested File nodes so author/commit traversals return owners
    conn.execute("""
        MATCH (f:Feature {id: "JIRA-101"})
        MATCH (file:File)
        WHERE file.path CONTAINS 'main.py' OR file.path CONTAINS 'seed.py' OR file.path CONTAINS 'README.md'
        MERGE (f)-[:TOUCHES]->(file)
    """)

    conn.close()
    print("Custom domain nodes and file links seeded successfully.")

if __name__ == "__main__":
    import sys
    repo = sys.argv[1] if len(sys.argv) > 1 else "."
    run_ingest(repo)
    seed_custom_domain()