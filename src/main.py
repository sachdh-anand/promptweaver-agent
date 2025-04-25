from crew import load_crew
from utils.output_writer import save_clean_output
from crewai import CrewOutput


if __name__ == "__main__":
    user_input = input(
        "🧠 Enter your raw prompt idea (we'll optimize it using advanced prompt frameworks):\n> "
    )

    crew = load_crew()
    result = crew.kickoff(inputs={"instruction": user_input})

    print("\n🔧 Final Generated Prompt:\n")
    print(result)  # full version with frameworks, notes


final_prompt = str(result)
save_clean_output(prompt=final_prompt, instruction=user_input)

