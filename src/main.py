from crew import run_prompt_weaver_crew
from utils.output_writer import save_clean_output

def main():
    user_input = input("🧠 Enter your raw prompt idea (we'll optimize it using advanced prompt frameworks):\n> ")

    final_prompt = run_prompt_weaver_crew(user_input)  # <--- Notice this fix

    save_clean_output(prompt=final_prompt, instruction=user_input)

    # print("\n🎨 Final Generated Prompt:\n")
    # print(final_prompt)

if __name__ == "__main__":
    main()
