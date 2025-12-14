#!/usr/bin/env python3
"""
Deep Research comparison script - runs the same query on both
Perplexity Sonar Deep Research and Google Gemini Deep Research APIs.
"""

import os
import time
import json
import requests
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

PERPLEXITY_API_KEY = os.getenv("PERPLEXITY_API_KEY")
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")

RESEARCH_QUERY = """As of today, produce a fully-cited, primary-source-backed comparison of current AI regulation and enforcement across EU, US, UK, and Canada: include a table with (1) legal instrument name, (2) status, (3) scope, (4) key obligations, (5) effective dates / phase-in timeline, (6) penalties, (7) enforcement agencies + at least 3 concrete enforcement actions or official notices where applicable; then add a 'What changed in the last 90 days' section and a 'Conflicts/uncertainties' section listing claims that differ across sources and how you resolved them (or couldn't)."""

OUTPUT_DIR = Path("research_results")


def run_perplexity_research():
    """Run deep research using Perplexity's Sonar Deep Research API."""
    print("\n" + "="*60)
    print("PERPLEXITY SONAR DEEP RESEARCH")
    print("="*60)

    url = "https://api.perplexity.ai/chat/completions"

    headers = {
        "Authorization": f"Bearer {PERPLEXITY_API_KEY}",
        "Content-Type": "application/json"
    }

    payload = {
        "model": "sonar-deep-research",
        "messages": [
            {
                "role": "system",
                "content": "You are a legal research assistant specializing in AI regulation. Provide comprehensive, well-cited reports with primary sources."
            },
            {
                "role": "user",
                "content": RESEARCH_QUERY
            }
        ],
        "search_mode": "web",
        "temperature": 0.2,
        "reasoning_effort": "high"
    }

    print("Starting Perplexity deep research...")
    print(f"Query: {RESEARCH_QUERY[:100]}...")

    try:
        response = requests.post(url, headers=headers, json=payload, timeout=600)
        response.raise_for_status()

        result = response.json()

        # Extract the response content
        content = result.get("choices", [{}])[0].get("message", {}).get("content", "")
        usage = result.get("usage", {})
        search_results = result.get("search_results", [])

        print(f"\n✓ Research completed!")
        print(f"  - Prompt tokens: {usage.get('prompt_tokens', 'N/A')}")
        print(f"  - Completion tokens: {usage.get('completion_tokens', 'N/A')}")
        print(f"  - Search queries: {usage.get('num_search_queries', 'N/A')}")
        print(f"  - Citations: {len(search_results)} sources")

        # Save results
        OUTPUT_DIR.mkdir(exist_ok=True)

        # Save full response
        with open(OUTPUT_DIR / "perplexity_full_response.json", "w") as f:
            json.dump(result, f, indent=2)

        # Save report
        report_content = f"""# Perplexity Deep Research Report
## AI Regulation Comparison (EU, US, UK, Canada)

*Generated: {time.strftime('%Y-%m-%d %H:%M:%S')}*

---

{content}

---

## Sources

"""
        for i, source in enumerate(search_results, 1):
            report_content += f"{i}. [{source.get('title', 'Untitled')}]({source.get('url', '')})\n"

        with open(OUTPUT_DIR / "perplexity_report.md", "w") as f:
            f.write(report_content)

        print(f"  - Report saved to: {OUTPUT_DIR}/perplexity_report.md")

        return result

    except requests.exceptions.RequestException as e:
        print(f"✗ Perplexity API error: {e}")
        if hasattr(e, 'response') and e.response is not None:
            print(f"  Response: {e.response.text}")
        return None


def run_gemini_research():
    """Run deep research using Google Gemini Deep Research API."""
    print("\n" + "="*60)
    print("GOOGLE GEMINI DEEP RESEARCH")
    print("="*60)

    try:
        from google import genai
        client = genai.Client(api_key=GOOGLE_API_KEY)
    except ImportError:
        print("Installing google-genai package...")
        import subprocess
        subprocess.run(["pip", "install", "google-genai"], check=True)
        from google import genai
        client = genai.Client(api_key=GOOGLE_API_KEY)

    print("Starting Gemini deep research...")
    print(f"Query: {RESEARCH_QUERY[:100]}...")
    print("(This may take up to 20 minutes for comprehensive research)")

    try:
        # Start the research
        interaction = client.interactions.create(
            input=RESEARCH_QUERY,
            agent='deep-research-pro-preview-12-2025',
            background=True,
            agent_config={
                "type": "deep-research",
                "thinking_summaries": "auto"
            }
        )

        print(f"Research started: {interaction.id}")

        # Poll for completion
        start_time = time.time()
        while True:
            interaction = client.interactions.get(interaction.id)
            elapsed = int(time.time() - start_time)

            if interaction.status == "completed":
                print(f"\n✓ Research completed in {elapsed} seconds!")
                break
            elif interaction.status == "failed":
                print(f"\n✗ Research failed: {interaction.error}")
                return None

            print(f"  Status: {interaction.status} ({elapsed}s elapsed)...", end="\r")
            time.sleep(10)

        # Extract results
        content = interaction.outputs[-1].text if interaction.outputs else ""
        usage = getattr(interaction, 'usage', {})

        print(f"  - Total tokens: {getattr(usage, 'total_tokens', 'N/A')}")

        # Save results
        OUTPUT_DIR.mkdir(exist_ok=True)

        # Save full response (serialize the Interaction object)
        raw_data = {
            "id": interaction.id,
            "status": interaction.status,
            "outputs": [{"text": o.text, "type": getattr(o, 'type', None)} for o in interaction.outputs] if interaction.outputs else [],
            "usage": {
                "prompt_tokens": getattr(usage, 'prompt_tokens', None),
                "completion_tokens": getattr(usage, 'completion_tokens', None),
                "total_tokens": getattr(usage, 'total_tokens', None),
            } if usage else {}
        }
        with open(OUTPUT_DIR / "gemini_full_response.json", "w") as f:
            json.dump(raw_data, f, indent=2)
        print(f"  - Raw response saved to: {OUTPUT_DIR}/gemini_full_response.json")

        # Save report
        report_content = f"""# Google Gemini Deep Research Report
## AI Regulation Comparison (EU, US, UK, Canada)

*Generated: {time.strftime('%Y-%m-%d %H:%M:%S')}*
*Interaction ID: {interaction.id}*

---

{content}
"""

        with open(OUTPUT_DIR / "gemini_report.md", "w") as f:
            f.write(report_content)

        print(f"  - Report saved to: {OUTPUT_DIR}/gemini_report.md")

        return interaction

    except Exception as e:
        print(f"✗ Gemini API error: {e}")
        return None


def main():
    print("\n" + "#"*60)
    print("# DEEP RESEARCH COMPARISON")
    print("# Query: AI Regulation (EU, US, UK, Canada)")
    print("#"*60)

    if not PERPLEXITY_API_KEY:
        print("Warning: PERPLEXITY_API_KEY not found in .env")
    if not GOOGLE_API_KEY:
        print("Warning: GOOGLE_API_KEY not found in .env")

    # Run both research queries
    perplexity_result = run_perplexity_research() if PERPLEXITY_API_KEY else None
    gemini_result = run_gemini_research() if GOOGLE_API_KEY else None

    # Summary
    print("\n" + "="*60)
    print("SUMMARY")
    print("="*60)
    print(f"Perplexity: {'✓ Completed' if perplexity_result else '✗ Failed or skipped'}")
    print(f"Gemini:     {'✓ Completed' if gemini_result else '✗ Failed or skipped'}")
    print(f"\nResults saved to: {OUTPUT_DIR.absolute()}/")


if __name__ == "__main__":
    main()
