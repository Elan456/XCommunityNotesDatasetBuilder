import argparse
import os
import json
import sys
from checkpoint import Checkpoint

def write_checkpoint_to_json(checkpoint_path, output_file):
    checkpoint = Checkpoint.load(checkpoint_path)
    output_path = os.path.join(checkpoint.output_directory, output_file)

    checkpoint_data = {
        "checkpoint_info": {
            "timestamp": checkpoint.created_at.isoformat(),
            "executed_steps": [step.name for step in checkpoint.executed_steps],
            "dataset_path": checkpoint.dataset_path
        },
        "dataset": checkpoint.get_dataset()
    }

    with open(output_path, "w") as f:
        json.dump(checkpoint_data, f, indent=4)

    print(f"Checkpoint data written to {output_path}")

def main():
    parser = argparse.ArgumentParser(description="Load a checkpoint and write its data to a JSON file.")
    parser.add_argument("--checkpoint_path", required=True, help="Path to the checkpoint file.")
    parser.add_argument("--output_file", required=True, help="Name of the output JSON file.")
    args = parser.parse_args()

    if not args.checkpoint_path:
        print("Error: checkpoint_path is required.", file=sys.stderr)
        sys.exit(1)

    if not args.output_file:
        print("Error: output_file is required.", file=sys.stderr)
        sys.exit(1)

    write_checkpoint_to_json(args.checkpoint_path, args.output_file)

if __name__ == "__main__":
    main()