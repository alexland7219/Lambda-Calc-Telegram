# Lambda Calculus Interpreter Telegram Bot

This is a Telegram bot written in Python that interprets Lambda Calculus expressions. It allows users to input Lambda Calculus expressions and receive the corresponding evaluation or reduction. Furthermore, it can also be used with the command line (not launching the Telegram Bot).

## Table of Contents

- [Features](#features)
- [Installation](#installation)
- [Usage](#usage)
- [Examples](#examples)
- [Contributing](#contributing)
- [License](#license)

## Features

- Interpretation and reduction of Lambda Calculus expressions
- Supports common Lambda Calculus syntax
- Interactive bot interface on Telegram
- Supports local command-line interface

## Installation

1. Clone the repository:
2. Change into the project directory:
3. Install the required dependencies using pip:

`pip install antlr4-tools antlr4-python3-runtime python-telegram-bot pydot`

4. Set up a Telegram bot:

- Create a new bot using the [BotFather](https://core.telegram.org/bots#botfather) on Telegram.
- Obtain the API token for your bot.
- Save the API token on a file called `token.txt` in this directory.

5. Run the bot:

- Run `antlr4 -Dlanguage=Python3 -no-listener -visitor lc.g4`
- Run `python3 achurch.py` and either launch the Telegram Bot (option `0`) or use the command-line version of the Lambda Calculus Bot (option `1`)

7. Start a conversation with your bot on Telegram and begin interpreting Lambda Calculus expressions!

## Usage

To use the Lambda Calculus interpreter bot, follow these steps:

1. Start a conversation with the bot on Telegram.
2. Send a Lambda Calculus expression as a message to the bot.
3. The bot will evaluate and reduce the expression and respond with the result and the intermediate steps.

Note: The bot supports common Lambda Calculus syntax, such as lambda abstraction (`λ`), function application, and variable names. For example, you can send expressions like `λx.x`, `(λx.x) y`, or `λxy.y` to the bot. You can replace `λ` by backslashes `\`. 

Variable names **must** be a lowercase letter, and you can also define macros that start with an uppercase letter (or are a non-alphabetical symbol) with the command `ID = \x.x` (you will now be able to use `ID` instead of `\x.x` in your Lambda Calculus expressions!). If a macro is a non-alphabetical symbol, say `+`, then the order of an application `TERM +` will be reversed and interpreted as `+ TERM`.

You can list all registered macros with `/macros` or `/macro`, and delete them all with `/clear`.

## Examples

Here are a few examples of Lambda Calculus expressions you can try with the bot:

- `λx.x` (Identity function)
- `(λx.x) y` (Function application)
- `(λx.(x x)) (λx.(x x))` (The Y Combinator)

## Contributing

Contributions to this project are welcome! If you encounter any issues or have suggestions for improvements, please open an issue or submit a pull request.

When contributing, please adhere to the existing code style and follow the [Python PEP 8](https://www.python.org/dev/peps/pep-0008/) guidelines.

## License

This project is licensed under the [GPLv3 License](LICENSE). Feel free to modify and distribute it as needed.

Alexandre Ros Roger - 2023
