import time

def run_with_retries(fn, inputs=None, retries=3, delay=5):
    """
    Runs a function with retry logic.
    Parameters:
    - fn: The function to run (e.g., crew.kickoff).
    - inputs: Dictionary of keyword arguments to pass to the function.
    - retries: Number of retry attempts.
    - delay: Delay (in seconds) between retries.
    Returns:
    - Result of the successful function call.
    Raises:
    - The last exception if all retries fail.
    """
    last_exception = None
    for attempt in range(1, retries + 1):
        try:
            return fn(inputs=inputs)
        except Exception as e:
            last_exception = e
            print(f"[Retry {attempt}/{retries}] Error: {e}")
            if attempt < retries:
                print(f"Retrying in {delay} seconds...")
                time.sleep(delay)
    raise last_exception
