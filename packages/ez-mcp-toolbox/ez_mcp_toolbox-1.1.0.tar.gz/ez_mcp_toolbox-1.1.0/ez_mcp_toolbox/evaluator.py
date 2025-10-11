#!/usr/bin/env python3
"""
ez-mcp-eval: Command-line tool for evaluating LLM applications using Opik.

This tool provides a simple interface to run evaluations on datasets
using Opik's evaluation framework.
"""

import argparse
import asyncio
import json
import os
import sys
from typing import Any, Dict, List, Optional
from dataclasses import dataclass

from opik import Opik, track
from opik.evaluation import evaluate
from opik.evaluation import metrics
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from dotenv import load_dotenv
from litellm import completion
import litellm
from .utils import configure_opik, call_llm_with_tracing, extract_llm_content

load_dotenv()


@dataclass
class EvaluationConfig:
    """Configuration for the evaluation run."""

    prompt: str
    dataset: str
    metric: str
    experiment_name: str
    opik_mode: str = "hosted"
    debug: bool = False
    input_field: str = "input"
    reference_field: str = "answer"
    output_field: str = "output"
    output_ref: str = "reference"
    model: str = "gpt-3.5-turbo"
    model_kwargs: Optional[Dict[str, Any]] = None


class MCPEvaluator:
    """Main evaluator class for running Opik evaluations."""

    def __init__(self, config: EvaluationConfig):
        self.config = config
        self.console = Console()
        self.client = None
        self.dataset = None

    def configure_opik(self):
        """Configure Opik based on the specified mode."""
        configure_opik(self.config.opik_mode, "ez-mcp-eval")

    def setup_client_and_dataset(self):
        """Initialize Opik client and load dataset."""
        try:
            self.console.print(f"🔗 Connecting to Opik...")
            self.client = Opik()

            self.console.print(f"📊 Loading dataset: {self.config.dataset}")
            self.dataset = self.client.get_dataset(name=self.config.dataset)

            self.console.print(f"✅ Dataset loaded successfully")
            self.console.print(f"   - Dataset name: {self.config.dataset}")
            self.console.print(
                f"   - Items count: {len(self.dataset) if hasattr(self.dataset, '__len__') else 'Unknown'}"
            )

        except Exception as e:
            self.console.print(
                f"❌ Failed to load dataset '{self.config.dataset}': {e}"
            )
            raise

    def resolve_prompt(self, prompt_value):
        """Resolve prompt by first checking Opik for a prompt with that name, then fallback to direct value."""
        try:
            # First try to get the prompt from Opik by name
            self.console.print(f"🔍 Looking up prompt '{prompt_value}' in Opik...")
            prompt = self.client.get_prompt(name=prompt_value)

            # If found, use the prompt content
            prompt_content = prompt.prompt if hasattr(prompt, "prompt") else str(prompt)
            self.console.print(
                f"✅ Found prompt in Opik: {prompt_content[:100]}{'...' if len(prompt_content) > 100 else ''}"
            )
            return prompt_content

        except Exception as e:
            # If not found or any error, use the prompt value directly
            self.console.print(
                f"⚠️  Prompt '{prompt_value}' not found in Opik ({e}), using as direct prompt"
            )
            return prompt_value

    def create_evaluation_task(self):
        """Create the evaluation task function."""
        # Resolve the prompt (check Opik first, then use direct value)
        resolved_prompt = self.resolve_prompt(self.config.prompt)

        def evaluation_task(dataset_item):
            """Evaluation task that will be called for each dataset item."""
            try:
                if self.config.debug:
                    self.console.print(f"🔍 Processing dataset item: {dataset_item}")

                # Get the input value from the dataset
                input_value = dataset_item.get(self.config.input_field)

                # Call the LLM with the resolved prompt and input
                try:
                    # Use common utility function for LLM calls with Opik tracing
                    resp = call_llm_with_tracing(
                        model=self.config.model,
                        messages=[
                            {"role": "system", "content": resolved_prompt},
                            {"role": "user", "content": str(input_value)},
                        ],
                        debug=self.config.debug,
                        console=self.console,
                        **self.config.model_kwargs if self.config.model_kwargs else {},
                    )
                    response = resp.choices[0].message.content
                except Exception as llm_error:
                    self.console.print(f"⚠️  LLM call failed: {llm_error}")
                    response = f"LLM Error: {llm_error}"

                if self.config.debug:
                    self.console.print(f"📝 Generated response: {response}")

                # Return simple output structure that can be mapped by scoring_key_mapping
                return {"llm_output": response}

            except Exception as e:
                self.console.print(f"❌ Error processing dataset item: {e}")
                return {"llm_output": f"Error: {e}"}

        return evaluation_task

    def get_metrics(self):
        """Get the metrics to use for evaluation."""
        metric_names = [name.strip() for name in self.config.metric.split(",")]
        metric_instances = []

        for metric_name in metric_names:
            metric_name = metric_name.strip()

            # Try to get the metric class from opik.evaluation.metrics
            try:
                metric_class = getattr(metrics, metric_name)
                metric_instances.append(metric_class())
                self.console.print(f"✅ Loaded metric: {metric_name}")
            except AttributeError:
                self.console.print(
                    f"❌ Unknown metric '{metric_name}'. Available metrics:"
                )
                available_metrics = list_available_metrics()
                for available_metric in available_metrics:
                    self.console.print(f"   - {available_metric}")
                raise ValueError(f"Unknown metric: {metric_name}")

        return metric_instances

    def run_evaluation(self):
        """Run the evaluation using Opik."""
        try:
            self.console.print(f"🚀 Starting evaluation...")
            self.console.print(f"   - Experiment: {self.config.experiment_name}")
            self.console.print(f"   - Dataset: {self.config.dataset}")
            self.console.print(f"   - Metric: {self.config.metric}")

            # Resolve the prompt and show it
            resolved_prompt = self.resolve_prompt(self.config.prompt)
            prompt_display = (
                resolved_prompt[:100] + "..."
                if len(resolved_prompt) > 100
                else resolved_prompt
            )
            self.console.print(f"   - Prompt: {prompt_display}")

            # Create evaluation task
            evaluation_task = self.create_evaluation_task()

            # Get metrics
            metrics = self.get_metrics()

            # Run evaluation - let Opik handle its own progress display
            # Opik's evaluate function has built-in tqdm progress bar
            self.console.print("🔄 Running evaluation...")

            eval_results = evaluate(
                experiment_name=self.config.experiment_name,
                dataset=self.dataset,
                task=evaluation_task,
                scoring_metrics=metrics,
                scoring_key_mapping={
                    "output": "llm_output",  # maps to task output
                    self.config.output_ref: self.config.reference_field,  # maps to dataset's reference field
                },
            )

            self.console.print("✅ Evaluation completed!")

            # Display results
            self.display_results(eval_results)

            return eval_results

        except Exception as e:
            self.console.print(f"❌ Evaluation failed: {e}")
            raise

    def display_results(self, results):
        """Display evaluation results."""
        self.console.print("\n" + "=" * 60)
        self.console.print("📊 EVALUATION RESULTS", style="bold blue")
        self.console.print("=" * 60)

        # Show evaluation information
        self.console.print(f"📈 Experiment: {self.config.experiment_name}")
        self.console.print(f"📊 Dataset: {self.config.dataset}")
        self.console.print(f"🎯 Metric: {self.config.metric}")

        # Show the resolved prompt (truncated if too long)
        resolved_prompt = self.resolve_prompt(self.config.prompt)
        prompt_display = (
            resolved_prompt[:100] + "..."
            if len(resolved_prompt) > 100
            else resolved_prompt
        )
        self.console.print(f"💬 Prompt: {prompt_display}")

        self.console.print("\n✅ Evaluation completed successfully!")

    def run(self):
        """Run the complete evaluation process."""
        try:
            # Configure Opik
            self.configure_opik()

            # Setup client and dataset
            self.setup_client_and_dataset()

            # Run evaluation
            results = self.run_evaluation()

            return results

        except Exception as e:
            self.console.print(f"❌ Evaluation failed: {e}")
            if self.config.debug:
                import traceback

                self.console.print(traceback.format_exc())
            sys.exit(1)


def parse_arguments():
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(
        description="ez-mcp-eval: Evaluate LLM applications using Opik",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  ez-mcp-eval --prompt "Answer the question" --dataset "my-dataset" --metric "Hallucination"
  ez-mcp-eval --prompt "Summarize this text" --dataset "summarization-dataset" --metric "LevenshteinRatio" --experiment-name "summarization-test"
  ez-mcp-eval --prompt "Translate to French" --dataset "translation-dataset" --metric "Hallucination,LevenshteinRatio" --opik local
  ez-mcp-eval --prompt "Answer the question" --dataset "qa-dataset" --metric "LevenshteinRatio" --input "question" --output "reference=answer"
  ez-mcp-eval --prompt "Answer the question" --dataset "qa-dataset" --metric "LevenshteinRatio" --model-kwargs '{"temperature": 0.7, "max_tokens": 1000}'
        """,
    )

    parser.add_argument(
        "--prompt", required=True, help="The prompt to use for evaluation"
    )

    parser.add_argument(
        "--dataset", required=True, help="Name of the dataset to evaluate on"
    )

    parser.add_argument(
        "--metric",
        required=True,
        help="Name of the metric(s) to use for evaluation. Use comma-separated list for multiple metrics (e.g., 'Hallucination,LevenshteinRatio')",
    )

    parser.add_argument(
        "--experiment-name",
        default="ez-mcp-evaluation",
        help="Name for the evaluation experiment (default: ez-mcp-evaluation)",
    )

    parser.add_argument(
        "--opik",
        choices=["local", "hosted", "disabled"],
        default="hosted",
        help="Opik tracing mode: local, hosted, or disabled (default: hosted)",
    )

    parser.add_argument("--debug", action="store_true", help="Enable debug output")

    parser.add_argument(
        "--input",
        default="input",
        help="Input field name in the dataset (default: input)",
    )

    parser.add_argument(
        "--output",
        default="reference=answer",
        help="Output field mapping in format reference=DATASET_FIELD (default: reference=answer)",
    )

    parser.add_argument(
        "--list-metrics",
        action="store_true",
        help="List all available metrics and exit",
    )

    parser.add_argument(
        "--model",
        default="gpt-3.5-turbo",
        help="LLM model to use for evaluation (default: gpt-3.5-turbo)",
    )

    parser.add_argument(
        "--model-kwargs",
        type=str,
        help='JSON string of additional keyword arguments to pass to the LLM model (e.g., \'{"temperature": 0.7, "max_tokens": 1000}\')',
    )

    return parser.parse_args()


def parse_field_mapping(mapping_str):
    """Parse field mapping in format REFERENCE=QUESTION."""
    if "=" not in mapping_str:
        raise ValueError(
            f"Field mapping must be in format REFERENCE=QUESTION, got: {mapping_str}"
        )

    reference, question = mapping_str.split("=", 1)
    return reference.strip(), question.strip()


def parse_output_mapping(mapping_str):
    """Parse output mapping in format reference=DATASET_FIELD."""
    if "=" not in mapping_str:
        raise ValueError(
            f"Output mapping must be in format reference=DATASET_FIELD, got: {mapping_str}"
        )

    reference, dataset_field = mapping_str.split("=", 1)
    return reference.strip(), dataset_field.strip()


def list_available_metrics():
    """List all available metrics from opik.evaluation.metrics."""
    available_metrics = [
        name
        for name in dir(metrics)
        if not name.startswith("_") and callable(getattr(metrics, name))
    ]
    return sorted(available_metrics)


def main():
    """Main entry point for ez-mcp-eval."""
    args = parse_arguments()

    # Handle --list-metrics option
    if args.list_metrics:
        console = Console()
        console.print("📊 Available metrics from opik.evaluation.metrics:")
        available_metrics = list_available_metrics()
        for metric in available_metrics:
            console.print(f"   - {metric}")
        return

    # Parse field mappings
    input_field = args.input
    output_ref, reference_field = parse_output_mapping(args.output)

    # Parse model kwargs JSON
    model_kwargs = None
    if args.model_kwargs:
        try:
            model_kwargs = json.loads(args.model_kwargs)
        except json.JSONDecodeError as e:
            console = Console()
            console.print(f"❌ Invalid JSON in --model-kwargs: {e}")
            sys.exit(1)

    # Create configuration
    config = EvaluationConfig(
        prompt=args.prompt,
        dataset=args.dataset,
        metric=args.metric,
        experiment_name=args.experiment_name,
        opik_mode=args.opik,
        debug=args.debug,
        input_field=input_field,
        reference_field=reference_field,
        output_field="llm_output",  # Task always returns {"llm_output": response}
        output_ref=output_ref,  # The metric's expected field name (e.g., "reference")
        model=args.model,
        model_kwargs=model_kwargs,
    )

    # Create and run evaluator
    evaluator = MCPEvaluator(config)
    evaluator.run()


if __name__ == "__main__":
    main()
