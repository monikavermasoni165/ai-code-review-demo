import os
from git import Repo
import subprocess
import requests
import json
import textwrap
from github import Github

GITHUB_TOKEN= os.environ["GITHUB_TOKEN"]
PR_NUMBER= int(os.environ["PR_NUMBER"])
REPO_FULL= os.environ["REPO_FULL"]
COMMIT_SHA= os.environ["COMMIT_SHA"]
AI_API = "https://stg1.mmc-dallas-int-non-prod-ingress.mgti.mmc.com/coreapi/openai/v1/deployments/mmc-tech-gpt-35-turbo-smart-latest/chat/completions"
AI_KEY = "d9e8a727-e312-4937-bcae-9e0ad3364b23-c7a9d130-774f-496b-83d2-a778aee2d607"


def call_ai(diff_text)
	payload = {"messages" = [
		{
			"role":"system",
			"content":build_system_prompt()
		},
		{
			"role":"user",
			"content":"Review the following code diff. Return JSON that matches the schema exactly. If nothing to report, use an empty items array and a brief summary. Here is the difference ": \n{diff_text}"}
		}
	]
    }
    
    headers = {
    "Content-Type":"application/json",
    "X-Api-Key":{AI_KEY}
    }
    
    response = requests.post(API_URL, headers=headers, json=payload)
    response.raise_for_status()
    try:
        return json.loads(response.json().get("choices")[0]["message"]["content"])
    except Exception as e:
        print("AI response parsing error:",e,response.text)
        return []
    
def chunk_text(s:str, max_chars:int = 12000)-> List[str]:
    chunks=[]
    i=0
    while i< len(s):
        chunks.append(s[i:i+max_chars])
        i+= max_chars
    return chunks or [""]
    
def build_system_prompt() -> str:
    return textwrap.dedent("""
        You are a seasoned code reviewer for a .Net + Angular monorepo. Be concise, actionable, and specific.
        Prefer examples and code diffs.
        Focus on:
        - Correctness/Potential bugs
        - Security(e.g. input validation, secrets, unsafe APIs, wrong logic in terms of functionality)
        - Performance / allocations / async patterns
        - Readability / maintainability(naming, factoring)
        - Framework best practices(ASP.Net Core, EF Core, Angular, RxJS)
        - Output STRICT JSON(no markdown) using this schema:
            { "summary" : "1-3 sentences top level summary",
              "items":[{
              "file":"Relative Path",
              "line":"line number" ,
              "severity":"high|medium|low",
              "Title":" short headline",
              "Details":"what & why; include rationale",
              "Suggestion":"optional concrete fix or code snippet"
              }
              ]
            }
    """).strip()
        
    
def post_comment(comments):
   gn= Github(GITHUB_TOKEN)
   repo= gn.get_repo(REPO_FULL)
   pr= repo.get_pull(PR_NUMBER)
   
   for c in comments:
       try:
           pr.create_review_comment(
           body=c["comment"],
           commit_id=COMMIT_SHA,
           path=c["file"],
           line=int(c["line"])
           print(f"Comment posted on {c['file']}:{c['line']}")
        except Exception as e:
            print("Failed to post coment:",e,c)
    
    
if __name__ == "__main__":
        diff_file= sys.argv[1]
        with open(diff_file) as f:
            diff_text=f.read()
            
        comments= call_ai(diff_text)
        if comments:
            post_comment(comments)
        else:
            print("No AI comments generated")