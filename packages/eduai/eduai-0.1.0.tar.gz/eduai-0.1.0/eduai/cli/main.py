"""
Simple CLI for eduai. Run demo modes from the command line.
Usage:
    python -m eduai.cli demo --mode summarize|quiz|explain
"""

import argparse
from .. import EduAI

SAMPLE_TEXT = (
    "Photosynthesis is the process plants use to turn sunlight into energy. "
    "It happens in leaves and uses water and carbon dioxide. "
    "This process makes oxygen which animals need to breathe. "
    "Understanding photosynthesis helps explain how plants grow."
)

def demo(mode: str):
    bot = EduAI()
    if mode == "summarize":
        out = bot.summarize(SAMPLE_TEXT, max_sentences=2)
        print("\n=== Summary ===\n")
        print(out)
    elif mode == "quiz":
        q = bot.generate_quiz(SAMPLE_TEXT, num_questions=3)
        print("\n=== Quiz ===\n")
        for item in q:
            print(f"Q{item['id']}: {item['question']}")
            if item['choices']:
                for idx, c in enumerate(item['choices'], start=1):
                    print(f"  {idx}. {c}")
                print(f"Answer: {item['answer']}")
            print()
    elif mode == "explain":
        e = bot.explain(SAMPLE_TEXT, level="child")
        print("\n=== Explain (child) ===\n")
        print(e)
    else:
        print("Unknown demo mode. Use summarize, quiz, or explain.")

def main():
    parser = argparse.ArgumentParser(prog="eduai")
    sub = parser.add_subparsers(dest="cmd")
    demo_p = sub.add_parser("demo", help="run demo")
    demo_p.add_argument("--mode", choices=["summarize","quiz","explain"], default="summarize")
    args = parser.parse_args()
    if args.cmd == "demo":
        demo(args.mode)
    else:
        parser.print_help()

if __name__ == "__main__":
    main()
