import datetime
import subprocess
import urllib.parse
import webbrowser
import ast
import operator
import json


# VOICE OUTPUT
def speak(text):
    print("JARVIS:", text)
    subprocess.run(["termux-tts-speak", str(text)])


# VOICE INPUT
def listen():
    print("\nListening...")
    try:
        result = subprocess.run(
            ["termux-speech-to-text"],
            capture_output=True,
            text=True,
            timeout=60
        )
        command = result.stdout.strip().lower()

        if command:
            print("You:", command)

        return command

    except Exception:
        speak("I could not hear you. Please try again.")
        return ""


# SAFE CALCULATOR
def calculate(expression):
    ops = {
        ast.Add: operator.add,
        ast.Sub: operator.sub,
        ast.Mult: operator.mul,
        ast.Div: operator.truediv,
        ast.Pow: operator.pow,
        ast.USub: operator.neg,
        ast.UAdd: operator.pos,
    }

    def evaluate(node):
        if isinstance(node, ast.Constant) and type(node.value) in (int, float):
            return node.value

        if isinstance(node, ast.BinOp) and type(node.op) in ops:
            left = evaluate(node.left)
            right = evaluate(node.right)

            if isinstance(node.op, ast.Pow):
                if abs(right) > 8 or abs(left) > 100000:
                    raise ValueError("Power too large")

            result = ops[type(node.op)](left, right)

            if isinstance(result, complex) or abs(result) > 1e100:
                raise ValueError("Result too large")

            return result

        if isinstance(node, ast.UnaryOp) and type(node.op) in ops:
            return ops[type(node.op)](evaluate(node.operand))

        raise ValueError("Unsupported calculation")

    return evaluate(ast.parse(expression, mode="eval").body)


# GENERAL RESPONSES
def reply(command):
    now = datetime.datetime.now()

    if any(x in command for x in ["hello", "hey jarvis", "hi jarvis"]):
        return "Hello. JARVIS is online."

    if "your name" in command:
        return "I am JARVIS, your personal assistant."

    if "time" in command:
        return now.strftime("The time is %I:%M %p.")

    if "date" in command or "today" in command:
        return now.strftime("Today is %A, %d %B %Y.")

    if "battery" in command:
        try:
            result = subprocess.run(
                ["termux-battery-status"],
                capture_output=True,
                text=True,
                timeout=10
            )
            data = json.loads(result.stdout)
            return f"Battery is at {data.get('percentage', 'unknown')} percent."
        except Exception:
            return "I could not read the battery status."

    if "search for" in command:
        query = command.split("search for", 1)[1].strip()

        if query:
            url = (
                "https://www.google.com/search?q="
                + urllib.parse.quote_plus(query)
            )
            webbrowser.open(url)
            return "Searching the web for " + query

    if "calculate" in command:
        expression = command.split("calculate", 1)[1].strip()

        try:
            if len(expression) > 100:
                return "That calculation is too long."

            result = calculate(expression)
            return f"The answer is {result}."

        except Exception:
            return "I could not calculate that."

    return "I do not know that command yet."


# ANDROID COMMAND HANDLER
def handle_command(command):
    command = command.lower().strip()

    if "open youtube" in command:
        subprocess.run([
            "am", "start",
            "-a", "android.intent.action.VIEW",
            "-d", "https://www.youtube.com"
        ])
        return "Opening YouTube."

    if "open google" in command:
        subprocess.run([
            "am", "start",
            "-a", "android.intent.action.VIEW",
            "-d", "https://www.google.com"
        ])
        return "Opening Google."

    return reply(command)


# MAIN JARVIS ENGINE
def main():
    speak("JARVIS systems online. Ready for your commands.")

    while True:
        command = listen()

        if not command:
            continue

        if command in (
            "exit",
            "quit",
            "stop jarvis",
            "shut down jarvis"
        ):
            speak("JARVIS signing off.")
            break

        response = handle_command(command)
        speak(response)


if __name__ == "__main__":
    main()
