from typing import List, Dict
from tqdm import tqdm
from .utils import truncate_text

class Evaluator:
    def __init__(self, agent, problems: List[Dict]):
        self.agent = agent
        self.problems = problems

    def run(self):
        results = []
        for p in tqdm(self.problems, desc="Problems"):
            res = self.agent.fix(p)
            attempts = []
            for a in res["attempts"]:
                attempts.append({
                    "attempt": a.get("attempt"),
                    "passed": a.get("passed"),
                    "duration": a.get("duration"),
                    "stderr": truncate_text(a.get("stderr", "")),
                    "stdout": truncate_text(a.get("stdout", "")),
                    "candidate_code": truncate_text(a.get("candidate_code", ""), 1000)
                })
            results.append({
                "problem_id": res["problem_id"],
                "passed": res["passed"],
                "attempts": attempts
            })
        total = len(results)
        passed = sum(1 for r in results if r["passed"])
        summary = {"total": total, "passed": passed, "pass@1": passed / total if total else 0.0}
        return {"summary": summary, "results": results}
