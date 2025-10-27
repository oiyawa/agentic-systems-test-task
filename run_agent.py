import argparse
import json
from src.agent import ReActFixAgent
from src.evaluator import Evaluator
from src.utils import safe_write_json

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--bench", required=True, help="path to benchmark json file")
    parser.add_argument("--output", default="results.json")
    parser.add_argument("--model-name", default="Qwen/Qwen2.5-0.5B")
    parser.add_argument("--max-attempts", type=int, default=3)
    args = parser.parse_args()

    with open(args.bench, "r", encoding="utf-8") as f:
        problems = json.load(f)

    agent = ReActFixAgent(model_name=args.model_name, max_attempts=args.max_attempts)
    evaluator = Evaluator(agent, problems)
    results = evaluator.run()
    safe_write_json(args.output, results)
    print(f"Done. Results saved to {args.output}")

if __name__ == "__main__":
    main()
