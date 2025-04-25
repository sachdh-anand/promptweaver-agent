from crew import load_crew

if __name__ == "__main__":
    user_input = input("📝 Enter your instruction: ")
    crew = load_crew()
    result = crew.kickoff(inputs={"instruction": user_input})
    print("\n🔧 Final Generated Prompt:\n", result)
