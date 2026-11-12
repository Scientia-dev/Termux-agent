# Termux AI Coding Agent

A small AI coding agent that runs on Android in Termux.
It can write files, run terminal commands, and read files — controlled by a local web chat UI.

## Setup

# Termux AI Coding Agent

A small AI coding agent that runs on Android in Termux. It can write files, run terminal commands, and read files — controlled by a local web chat UI.

## Requirements

Android phone, Termux (from F-Droid, not Play Store), and a free API key from console.groq.com.

## Setup

```bash
pkg update && pkg upgrade -y
pkg install python git -y
git clone https://github.com/YOURNAME/termux-agent.git
cd termux-agent
pip install flask requests
export GROQ_API_KEY="your_key_here"
python agent.py

