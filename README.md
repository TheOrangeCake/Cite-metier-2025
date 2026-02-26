# AI Canva

This educational game was developed by [nguyen NGUYEN](https://github.com/TheOrangeCake), [Enrique Murillo Orosco](https://github.com/theblacksnow95) and [Christian Bemba](https://github.com/Lusekk) during the AI Innovation Lab Hackathon. </br>
The concept won first prize and was further developed for use at Cité des Métiers 2025 in Geneva.</br>
Through the game, we aim to show young users (ages 7 to 16) a glimpse of what AI can do in coding, while also highlighting its limitations. The game was played by hundreds of users during the event, and the feedback was very positive.

## The concept

Users start with a simple game and gradually add modifications using AI. The quality of the modifications depends on the quality of the prompt.</br>
The challenge was to develop a good UI/UX for the target audience, especially since AI took roughly one minute to generate each change.

## How does the program work?

* Prompt Processing:</br>
User prompts are processed by adding custom instructions and context files to filter inappropriate content and ensure the output is educational and well-structured.
* Queue System & Real-Time Streaming:</br>
The game uses a queue system to manage Infomaniak API calls for AI-generated code. Responses are streamed directly to the game interface, allowing users to see the code being written in real time. The asynchronous API calls enable users to continue playing while waiting for results.
* Hot Loading & Error Handling:</br>
Generated code is hot-loaded into the game using Watchdog. If the game crashes, a saved state is automatically reloaded, and an educational message is displayed to the user.


## Dependencies

- pygame `apt-get install -y python3-pygame`
- watchdog `python3 -m pip install -U watchdog`

## Image credits

Robot emotes designed by pch.vector - Freepik.com
