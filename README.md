# 🎂 Slack Birthday Bot

A simple and friendly Slack bot to help your team remember and celebrate birthdays!

## Features

- 📅 **Add birthdays** - Store team member birthdays
- 📋 **List all birthdays** - See everyone's upcoming birthdays sorted by date
- 🎉 **Check today's birthdays** - Find out who's celebrating today
- 🗑️ **Remove birthdays** - Delete birthday entries
- 💬 **Interactive responses** - Bot responds to mentions and birthday keywords

## Prerequisites

- Python 3.7 or higher
- A Slack workspace where you can install apps
- Basic command line knowledge

## Step-by-Step Setup Guide

### Step 1: Create Your Slack App

1. Go to [https://api.slack.com/apps](https://api.slack.com/apps)
2. Click **"Create New App"**
3. Choose **"From an app manifest"**
4. Select your workspace
5. Switch to the **JSON tab**
6. Copy and paste the entire contents of `manifest.json` from this project
7. Click **"Next"**, review the configuration, then click **"Create"**

### Step 2: Get Your Tokens

You'll need two tokens for the bot to work:

#### Bot Token (SLACK_BOT_TOKEN)
1. In your app's settings, click **"OAuth & Permissions"** in the left sidebar
2. Click **"Install to Workspace"** (or "Reinstall to Workspace" if you've already installed it)
3. Click **"Allow"** to authorize the app
4. Copy the **"Bot User OAuth Token"** (starts with `xoxb-`)

#### App Token (SLACK_APP_TOKEN)
1. Click **"Basic Information"** in the left sidebar
2. Scroll down to **"App-Level Tokens"**
3. Click **"Generate Token and Scopes"**
4. Give it a name (e.g., "socket-token")
5. Add the scope **`connections:write`**
6. Click **"Generate"**
7. Copy the token (starts with `xapp-`)

⚠️ **Important**: Keep these tokens secret! Never share them or commit them to version control.

### Step 3: Set Up Your Local Environment

1. **Download/Clone this project** to your computer

2. **Open a terminal** and navigate to the project folder:
   ```bash
   cd path/to/birthday-bot
   ```

3. **Create a virtual environment** (recommended):
   ```bash
   python3 -m venv .venv
   ```

4. **Activate the virtual environment**:
   
   On Mac/Linux:
   ```bash
   source .venv/bin/activate
   ```
   
   On Windows:
   ```bash
   .venv\Scripts\activate
   ```

5. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

### Step 4: Configure Your Tokens

Set your environment variables with the tokens from Step 2:

**On Mac/Linux:**
```bash
export SLACK_BOT_TOKEN=xoxb-your-bot-token-here
export SLACK_APP_TOKEN=xapp-your-app-token-here
```

**On Windows (Command Prompt):**
```cmd
set SLACK_BOT_TOKEN=xoxb-your-bot-token-here
set SLACK_APP_TOKEN=xapp-your-app-token-here
```

**On Windows (PowerShell):**
```powershell
$env:SLACK_BOT_TOKEN="xoxb-your-bot-token-here"
$env:SLACK_APP_TOKEN="xapp-your-app-token-here"
```

💡 **Tip**: For a more permanent solution, create a `.env` file (see below).

### Step 5: Run Your Bot!

```bash
python birthday_bot.py
```

You should see:
```
⚡️ Birthday Bot is running!
```

🎉 Your bot is now live!

## Using the Bot

### Adding a Birthday

Add your own birthday:
```
/addbirthday 03-15
```

Add someone else's birthday:
```
/addbirthday @username 07-22
```

### Viewing All Birthdays

```
/listbirthdays
```

### Checking Today's Birthdays

```
/birthdaytoday
```

### Removing a Birthday

Remove your own:
```
/removebirthday
```

Remove someone else's:
```
/removebirthday @username
```

### Interacting with the Bot

- Mention the bot: `@Birthday Bot` - Get a helpful message
- Say "birthday" in any channel where the bot is present - Get a friendly response!

## Making Development Easier

### Using a .env File

Instead of setting environment variables each time, create a `.env` file in your project directory:

```bash
SLACK_BOT_TOKEN=xoxb-your-bot-token-here
SLACK_APP_TOKEN=xapp-your-app-token-here
```

Then install python-dotenv:
```bash
pip install python-dotenv
```

And add this to the top of `birthday_bot.py`:
```python
from dotenv import load_dotenv
load_dotenv()
```

⚠️ **Never commit your `.env` file to version control!** Add it to `.gitignore`.

## Data Storage

Birthdays are stored in a `birthdays.json` file in the same directory as the bot. This file is created automatically when you add your first birthday.

Example format:
```json
{
  "U12345678": {
    "name": "John Doe",
    "date": "03-15"
  }
}
```

## Troubleshooting

### "Token not found" error
- Make sure you've set both `SLACK_BOT_TOKEN` and `SLACK_APP_TOKEN` environment variables
- Check that the tokens are correct (no extra spaces)

### Bot doesn't respond to commands
- Make sure the bot is running (`python birthday_bot.py`)
- Verify Socket Mode is enabled in your app settings
- Try reinstalling the app to your workspace

### "Invalid date format" error
- Use MM-DD format (e.g., `03-15` for March 15)
- Include the leading zero for single-digit months/days

### Bot isn't responding in channels
- Invite the bot to the channel: `/invite @Birthday Bot`
- Or mention the bot directly: `@Birthday Bot`

## Next Steps & Improvements

Here are some ideas to enhance your bot:

- 🔔 **Automatic birthday announcements** - Schedule daily checks and post to a channel
- 🎁 **Birthday reminders** - Notify the team a few days before someone's birthday
- 🎊 **Custom messages** - Personalized birthday greetings
- 📊 **Birthday statistics** - Who has birthdays in which month
- 🌐 **Web dashboard** - View birthdays in a browser
- ☁️ **Deploy to the cloud** - Host on Heroku, AWS, or Google Cloud so it runs 24/7

## Need Help?

- [Bolt for Python Documentation](https://slack.dev/bolt-python/)
- [Slack API Documentation](https://api.slack.com/)
- The Slack Developer Community

## License

Feel free to use and modify this bot for your team! 🎉
