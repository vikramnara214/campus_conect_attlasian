from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import os
import relate
import uuid

app = FastAPI(title="CampusContext Embedded Backend", version="1.0.0")

DB_PATH = os.getenv("RELATE_DB", "./data/campus.rl")

def get_db():
    return relate.connect(DB_PATH)

class SuggestionCreate(BaseModel):
    feature_id: str
    text: str
    author: str

@app.get("/api/context/feature")
def get_feature_context(keyword: str):
    """Returns primary owner, recent commits, related files, and open suggestions for a feature/issue."""
    conn = get_db()
    try:
        cur = conn.execute("""
            MATCH (f:Feature)
            WHERE f.id = $kw OR f.title CONTAINS $kw
            OPTIONAL MATCH (f)-[:SUGGESTED_FOR]->(sug:Suggestion)
            OPTIONAL MATCH (f)-[:TOUCHES]->(file:File)<-[:TOUCHED]-(c:Commit)<-[:AUTHORED|AUTHORED_BY]-(author:Person)
            OPTIONAL MATCH (f)-[:BELONGS_TO]->(p:Project)
            RETURN f.id AS featureId, f.title AS title,
                   collect(DISTINCT author.name) AS potentialOwners,
                   collect(DISTINCT file.path)[0..5] AS relatedFiles,
                   collect(DISTINCT sug.text) AS suggestions,
                   p.name AS project
            LIMIT 5
        """, {"kw": keyword})
        records = list(cur)
        if not records:
            raise HTTPException(status_code=404, detail="Feature context not found")
        return records[0]
    finally:
        conn.close()

@app.get("/api/collaborators/match")
def match_collaborators(skill_id: str):
    """Matches a project's NEEDS_SKILL to students with proven Git commit history."""
    conn = get_db()
    try:
        cur = conn.execute("""
            MATCH (s:Skill {id: $skill_id})<-[:NEEDS_SKILL]-(f:Feature)
            MATCH (f)-[:TOUCHES]->(file:File)<-[:TOUCHED]-(c:Commit)<-[:AUTHORED|AUTHORED_BY]-(p:Person)
            RETURN p.name AS contributor, count(c) AS commitCount, collect(DISTINCT file.path)[0..3] AS sampleFiles
            ORDER BY commitCount DESC
            LIMIT 10
        """, {"skill_id": skill_id})
        records = list(cur)
        return {"skill": skill_id, "matches": records}
    finally:
        conn.close()

@app.post("/api/context/suggestion")
def create_suggestion(payload: SuggestionCreate):
    """Attaches a new (:Suggestion) node and [:COLLABORATES_ON] edge to a (:Feature)."""
    conn = get_db()
    try:
        sug_id = str(uuid.uuid4())
        cur = conn.execute("""
            MATCH (f:Feature {id: $feature_id})
            MERGE (author:Person {name: $author})
            CREATE (sug:Suggestion {id: $sug_id, text: $text, createdAt: datetime()})
            CREATE (f)-[:SUGGESTED_FOR]->(sug)
            CREATE (author)-[:COLLABORATES_ON {role: "suggestion_author"}]->(f)
            RETURN sug.id AS suggestionId, f.id AS featureId, sug.text AS text, author.name AS author
        """, {"feature_id": payload.feature_id, "text": payload.text, "author": payload.author, "sug_id": sug_id})
        records = list(cur)
        if not records:
            raise HTTPException(status_code=404, detail="Feature not found")
        return {"status": "success", "suggestion": records[0]}
    finally:
        conn.close()