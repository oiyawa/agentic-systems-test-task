from transformers import AutoTokenizer, AutoModelForCausalLM
import torch
import time
from .prompt_templates import PROMPT_INITIAL, PROMPT_FEEDBACK
from .sandbox import run_tests_in_sandbox
from .utils import normalize_code_block

class ReActFixAgent:
    def __init__(self, model_name="Qwen/Qwen2.5-0.5B", max_attempts: int = 3):
        self.model_name = model_name
        self.max_attempts = max_attempts
        print(f"[Agent] Loading model {model_name}...")

        self.tokenizer = AutoTokenizer.from_pretrained(model_name)
        if torch.cuda.is_available():
            self.model = AutoModelForCausalLM.from_pretrained(
                model_name, dtype=torch.float16, device_map="cuda"
            )
            self.device = "cuda"
        else:
            self.model = AutoModelForCausalLM.from_pretrained(
                model_name, dtype=torch.float32
            )
            self.device = "cpu"

        self.model.to(self.device)

    def _call_model(self, prompt: str, max_new_tokens: int = 300) -> str:
        inputs = self.tokenizer(prompt, return_tensors="pt").to(self.device)
        outputs = self.model.generate(
            **inputs,
            max_new_tokens=max_new_tokens,
            temperature=0.0,
            do_sample=False,
            eos_token_id=self.tokenizer.eos_token_id,
            pad_token_id=self.tokenizer.eos_token_id,
        )
        text = self.tokenizer.decode(outputs[0], skip_special_tokens=True)
        return text

    def _single_attempt(self, problem, context_feedback: str = None):
        if context_feedback:
            prompt = PROMPT_FEEDBACK.format(
                problem_id=problem.get("id", "<no-id>"),
                buggy_code=problem["buggy_code"],
                test_code=problem["test_code"],
                feedback=context_feedback
            )
        else:
            prompt = PROMPT_INITIAL.format(
                problem_id=problem.get("id", "<no-id>"),
                buggy_code=problem["buggy_code"],
                test_code=problem["test_code"]
            )

        start = time.time()
        model_out = self._call_model(prompt)
        duration = time.time() - start

        candidate_code = normalize_code_block(model_out)

        if not candidate_code.strip() or "def " not in candidate_code:
            return {
                "candidate_code": candidate_code,
                "model_output": model_out,
                "passed": False,
                "stdout": "",
                "stderr": "No valid python function found",
                "duration": duration
            }

        passed, stdout, stderr = run_tests_in_sandbox(candidate_code, problem["test_code"])

        return {
            "candidate_code": candidate_code,
            "model_output": model_out,
            "passed": passed,
            "stdout": stdout,
            "stderr": stderr,
            "duration": duration
        }

    def fix(self, problem: dict) -> dict:
        attempt_results = []
        feedback = None

        for attempt in range(1, self.max_attempts + 1):
            res = self._single_attempt(problem, context_feedback=feedback)
            res["attempt"] = attempt
            attempt_results.append(res)

            if res["passed"]:
                break

            failure_info = (res["stderr"] or res["stdout"]).strip()
            feedback = (
                "The current version failed tests.\n"
                "Here is the test output or error:\n"
                f"{failure_info}\n\n"
                "Return ONLY a corrected python function, nothing else."
            )

        return {
            "problem_id": problem.get("id"),
            "attempts": attempt_results,
            "passed": any(r["passed"] for r in attempt_results)
        }
