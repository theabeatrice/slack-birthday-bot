# 🚀 Quick Start Guide for Complete Beginners

Never built a Slack bot before? No problem! This guide will walk you through everything step-by-step.

## What You'll Need

1. **A computer** (Mac, Windows, or Linux)
2. **Python installed** (version 3.7 or newer)
   - Check if you have it: Open Terminal (Mac/Linux) or Command Prompt (Windows) and type: `python3 --version`
   - Don't have Python? Download it from [python.org](https://www.python.org/downloads/)
3. **A Slack workspace** where you can add apps
   - Don't have admin access? Ask your workspace admin or create a free test workspace at [slack.com](https://slack.com)

## The Simplest Setup Possible

### 1️⃣ Download the Bot Files

If you received these files in a ZIP, extract them to a folder like `Documents/birthday-bot`

### 2️⃣ Create Your Slack App

1. Go to https://api.slack.com/apps in your browser
2. Click the big green **"Create New App"** button
3. Choose **"From an app manifest"**
4. Select your workspace from the dropdown
5. Click the **"JSON"** tab at the top
6. Delete everything in the text box
7. Open the `manifest.json` file from your bot folder
8. Copy EVERYTHING from that file
9. Paste it into the text box on the Slack website
10. Click **"Next"**
11. Click **"Create"**

🎉 You now have a Slack app!

### 3️⃣ Get Your Secret Tokens

Your bot needs two special codes (tokens) to work:

**First Token - Bot Token:**
1. On the left side, click **"OAuth & Permissions"**
2. Click **"Install to Workspace"**
3. Click **"Allow"**
4. You'll see a token that starts with `xoxb-`
5. Click **"Copy"** - save this somewhere safe!

**Second Token - App Token:**
1. On the left side, click **"Basic Information"**
2. Scroll down to **"App-Level Tokens"**
3. Click **"Generate Token and Scopes"**
4. Name it "socket" (or anything you like)
5. Click **"Add Scope"** and choose `connections:write`
6. Click **"Generate"**
7. You'll see a token that starts with `xapp-`
8. Click **"Copy"** - save this somewhere safe!

### 4️⃣ Set Up Your Computer

**Open Terminal (Mac/Linux) or Command Prompt (Windows):**

1. Navigate to your bot folder:
   ```bash
   cd Documents/birthday-bot
   ```
   (Replace with wherever you put your files)

2. Create a special Python environment:
   ```bash
   python3 -m venv .venv
   ```

3. Activate it:
   
   Mac/Linux:
   ```bash
   source .venv/bin/activate
   ```
   
   Windows:
   ```bash
   .venv\Scripts\activate
   ```

4. Install what the bot needs:
   ```bash
   pip install -r requirements.txt
   ```

### 5️⃣ Add Your Tokens

You need to tell your computer about those tokens from Step 3.

**Mac/Linux:**
```bash
export SLACK_BOT_TOKEN=xoxb-paste-your-bot-token-here
export SLACK_APP_TOKEN=xapp-paste-your-app-token-here
```

**Windows (Command Prompt):**
```cmd
set SLACK_BOT_TOKEN=xoxb-paste-your-bot-token-here
set SLACK_APP_TOKEN=xapp-paste-your-app-token-here
```

**Windows (PowerShell):**
```powershell
$env:SLACK_BOT_TOKEN="xoxb-paste-your-bot-token-here"
$env:SLACK_APP_TOKEN="xapp-paste-your-app-token-here"
```

Replace `xoxb-paste-your-bot-token-here` with your actual token!

### 6️⃣ Run Your Bot!

```bash
python birthday_bot.py
```

You should see:
```
⚡️ Birthday Bot is running!
```

**🎊 SUCCESS! Your bot is alive!**

Keep this terminal window open while using your bot.

## Using Your Bot in Slack

1. Open Slack
2. In any channel or DM, type:
   ```
   /addbirthday 12-25
   ```
   (Use your actual birthday in MM-DD format)

3. The bot will confirm it saved your birthday!

4. Try:
   ```
   /listbirthdays
   ```
   to see all birthdays

## Common Issues & Solutions

### "python3: command not found"
- Try `python` instead of `python3`
- Or install Python from python.org

### "No module named 'slack_bolt'"
- Make sure you ran: `pip install -r requirements.txt`
- Make sure your virtual environment is activated (you should see `(.venv)` at the start of your command line)

### Bot doesn't respond to commands
- Is the terminal still showing "⚡️ Birthday Bot is running!"?
- If not, run `python birthday_bot.py` again
- Did you set both tokens? Check for typos!

### "environment variable not set"
- You need to set the tokens every time you open a new terminal
- OR use the `.env` file method (see README.md for details)

## Stopping the Bot

Press `Ctrl+C` in the terminal where the bot is running.

## Running the Bot Again Later

1. Open terminal
2. Navigate to the folder: `cd Documents/birthday-bot`
3. Activate the environment:
   - Mac/Linux: `source .venv/bin/activate`
   - Windows: `.venv\Scripts\activate`
4. Set your tokens again (unless you use a .env file)
5. Run: `python birthday_bot.py`

## What's Next?

Once you're comfortable with the basics:
- Read the full README.md for more features
- Try modifying the code to add new commands
- Deploy your bot to the cloud so it runs 24/7

## Getting Help

Stuck? Don't worry!
- Re-read this guide carefully
- Check the README.md for more details
- Search for your error message online
- The Slack API docs are at https://api.slack.com/

Remember: Everyone struggles with setup at first. You've got this! 💪
