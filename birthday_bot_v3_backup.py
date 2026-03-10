import os
import json
import random
import csv
import io
from datetime import datetime, date, timedelta
from slack_bolt import App
from slack_bolt.adapter.socket_mode import SocketModeHandler
import schedule
import time
import threading
import pytz

# Initialize the Slack app
app = App(token=os.environ.get("SLACK_BOT_TOKEN"))

# File to store birthdays, wishes, and configuration
BIRTHDAYS_FILE = "birthdays.json"
WISHES_FILE = "birthday_wishes.json"
CONFIG_FILE = "config.json"

# Mountain Time timezone
MOUNTAIN_TZ = pytz.timezone('America/Denver')

# Default configuration
DEFAULT_CONFIG = {
    "announcement_channel": None,
    "announcement_time": "09:00",
    "reminder_days": 3,
    "giphy_enabled": True,
    "giphy_api_key": os.environ.get("GIPHY_API_KEY", "")
}

# Zodiac sign mapping
ZODIAC_SIGNS = {
    (1, 20): ("♑", "Capricorn"),
    (2, 19): ("♒", "Aquarius"),
    (3, 21): ("♓", "Pisces"),
    (4, 20): ("♈", "Aries"),
    (5, 21): ("♉", "Taurus"),
    (6, 21): ("♊", "Gemini"),
    (7, 23): ("♋", "Cancer"),
    (8, 23): ("♌", "Leo"),
    (9, 23): ("♍", "Virgo"),
    (10, 23): ("♎", "Libra"),
    (11, 22): ("♏", "Scorpio"),
    (12, 22): ("♐", "Sagittarius"),
    (12, 31): ("♑", "Capricorn"),
}

# Zodiac element mapping
ZODIAC_ELEMENTS = {
    "Aries": "Fire", "Leo": "Fire", "Sagittarius": "Fire",
    "Taurus": "Earth", "Virgo": "Earth", "Capricorn": "Earth",
    "Gemini": "Air", "Libra": "Air", "Aquarius": "Air",
    "Cancer": "Water", "Scorpio": "Water", "Pisces": "Water"
}

def get_zodiac_sign(month, day):
    """Get zodiac sign emoji and name from birth date"""
    date_tuple = (month, day)
    
    for end_date, (emoji, name) in ZODIAC_SIGNS.items():
        if month < end_date[0] or (month == end_date[0] and day <= end_date[1]):
            return emoji, name
    
    return "♑", "Capricorn"

# Fun birthday messages
BIRTHDAY_MESSAGES = [
    "🎉 Happy Birthday {name}! {zodiac} Hope your day is as amazing as you are! 🎂",
    "🎈 It's {name}'s special day! {zodiac} Wishing you all the best! 🎊",
    "🎂 Another trip around the sun for {name}! {zodiac} Have a fantastic birthday! ☀️",
    "🎁 Hip hip hooray! It's {name}'s birthday today! {zodiac} 🎉",
    "🌟 Sending birthday wishes to the wonderful {name}! {zodiac} Have an incredible day! 🎈",
    "🎊 {name} is leveling up today! {zodiac} Happy Birthday! 🎮",
    "🎵 Happy Birthday to you, happy birthday to you, happy birthday dear {name}! {zodiac} 🎵",
    "🍰 Time to celebrate {name}! {zodiac} May your birthday be filled with joy and cake! 🎂"
]

GIPHY_SEARCH_TERMS = [
    "happy birthday celebration",
    "birthday cake",
    "birthday party",
    "birthday balloons",
    "happy birthday confetti"
]

def get_mountain_time():
    """Get current time in Mountain Time"""
    utc_now = datetime.now(pytz.utc)
    mountain_now = utc_now.astimezone(MOUNTAIN_TZ)
    return mountain_now

def load_birthdays():
    """Load birthdays from JSON file"""
    try:
        with open(BIRTHDAYS_FILE, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        return {}

def save_birthdays(birthdays):
    """Save birthdays to JSON file"""
    with open(BIRTHDAYS_FILE, 'w') as f:
        json.dump(birthdays, f, indent=2)

def load_wishes():
    """Load birthday wishes from JSON file"""
    try:
        with open(WISHES_FILE, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        return {}

def save_wishes(wishes):
    """Save birthday wishes to JSON file"""
    with open(WISHES_FILE, 'w') as f:
        json.dump(wishes, f, indent=2)

def load_config():
    """Load configuration from JSON file"""
    try:
        with open(CONFIG_FILE, 'r') as f:
            config = json.load(f)
            for key, value in DEFAULT_CONFIG.items():
                if key not in config:
                    config[key] = value
            return config
    except FileNotFoundError:
        return DEFAULT_CONFIG.copy()

def save_config(config):
    """Save configuration to JSON file"""
    with open(CONFIG_FILE, 'w') as f:
        json.dump(config, f, indent=2)

def get_random_birthday_gif():
    """Get a random birthday GIF from Giphy"""
    try:
        import requests
        config = load_config()
        api_key = config.get("giphy_api_key") or os.environ.get("GIPHY_API_KEY")
        
        if not api_key:
            print("No Giphy API key configured")
            return None
        
        search_term = random.choice(GIPHY_SEARCH_TERMS)
        url = f"https://api.giphy.com/v1/gifs/search?api_key={api_key}&q={search_term}&limit=20&rating=g"
        response = requests.get(url, timeout=5)
        data = response.json()
        
        if data.get('data'):
            gif = random.choice(data['data'])
            return gif['images']['original']['url']
    except Exception as e:
        print(f"Error fetching GIF: {e}")
    return None

def check_birthdays_today():
    """Check if anyone has a birthday today"""
    birthdays = load_birthdays()
    mountain_now = get_mountain_time()
    today_str = mountain_now.strftime("%m-%d")
    
    birthday_people = []
    for user_id, birthday_data in birthdays.items():
        if birthday_data.get("date", "") == today_str:
            month, day = map(int, birthday_data.get("date").split('-'))
            zodiac_emoji, zodiac_name = get_zodiac_sign(month, day)
            birthday_people.append({
                "user_id": user_id,
                "name": birthday_data.get("name", "someone"),
                "zodiac_emoji": zodiac_emoji,
                "zodiac_name": zodiac_name
            })
    
    return birthday_people

def check_upcoming_birthdays(days=3):
    """Check if anyone has a birthday in N days"""
    birthdays = load_birthdays()
    mountain_now = get_mountain_time()
    target_date = mountain_now.date() + timedelta(days=days)
    target_str = target_date.strftime("%m-%d")
    
    upcoming_people = []
    for user_id, birthday_data in birthdays.items():
        if birthday_data.get("date", "") == target_str:
            month, day = map(int, birthday_data.get("date").split('-'))
            zodiac_emoji, zodiac_name = get_zodiac_sign(month, day)
            upcoming_people.append({
                "user_id": user_id,
                "name": birthday_data.get("name", "someone"),
                "date": target_date,
                "zodiac_emoji": zodiac_emoji,
                "zodiac_name": zodiac_name
            })
    
    return upcoming_people

def find_birthday_twins():
    """Find people with the same birthday"""
    birthdays = load_birthdays()
    date_groups = {}
    
    for user_id, data in birthdays.items():
        bday = data.get("date")
        if bday not in date_groups:
            date_groups[bday] = []
        date_groups[bday].append(user_id)
    
    twins = {date: users for date, users in date_groups.items() if len(users) > 1}
    return twins

def calculate_birthday_streak():
    """Find longest streak of days without birthdays"""
    birthdays = load_birthdays()
    if not birthdays:
        return 0
    
    # Convert all birthdays to day-of-year
    days = []
    for data in birthdays.values():
        month, day = map(int, data['date'].split('-'))
        day_of_year = datetime(2024, month, day).timetuple().tm_yday
        days.append(day_of_year)
    
    days = sorted(set(days))
    
    if len(days) <= 1:
        return 365 - len(days)
    
    max_gap = 0
    for i in range(len(days) - 1):
        gap = days[i + 1] - days[i] - 1
        max_gap = max(max_gap, gap)
    
    # Check wrap-around (end of year to beginning)
    wrap_gap = (365 - days[-1]) + days[0] - 1
    max_gap = max(max_gap, wrap_gap)
    
    return max_gap

def post_wish_reminder():
    """Post reminders for upcoming birthdays"""
    config = load_config()
    channel = config.get("announcement_channel")
    reminder_days = config.get("reminder_days", 3)
    
    if not channel:
        return
    
    upcoming = check_upcoming_birthdays(days=reminder_days)
    
    if upcoming:
        for person in upcoming:
            day_name = person['date'].strftime("%A, %B %d")
            message = (
                f"📢 *Upcoming Birthday Alert!* 📢\n\n"
                f"<@{person['user_id']}>'s birthday is coming up on {day_name}! {person['zodiac_emoji']} *{person['zodiac_name']}*\n\n"
                f"💌 Want to wish them a happy birthday? Use:\n"
                f"`/addwish <@{person['user_id']}> Your personal message here`\n\n"
                f"All wishes will be shared on their special day! 🎂"
            )
            
            try:
                app.client.chat_postMessage(
                    channel=channel,
                    text=message
                )
                print(f"Posted birthday reminder for {person['name']}")
            except Exception as e:
                print(f"Error posting reminder: {e}")

def post_birthday_announcement():
    """Automatically post birthday announcements"""
    config = load_config()
    channel = config.get("announcement_channel")
    
    if not channel:
        print("No announcement channel set.")
        return
    
    birthday_people = check_birthdays_today()
    
    if birthday_people:
        for person in birthday_people:
            zodiac_text = f"{person['zodiac_emoji']} *{person['zodiac_name']}*"
            message = random.choice(BIRTHDAY_MESSAGES).format(
                name=f"<@{person['user_id']}>",
                zodiac=zodiac_text
            )
            
            wishes = load_wishes()
            user_wishes = wishes.get(person['user_id'], [])
            
            blocks = [
                {
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": message
                    }
                }
            ]
            
            if user_wishes:
                wishes_text = "\n\n💌 *Birthday Wishes from the Team:*\n\n"
                for wish in user_wishes:
                    wishes_text += f"• <@{wish['from_user']}>: _{wish['message']}_\n"
                
                blocks.append({
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": wishes_text
                    }
                })
            
            if config.get("giphy_enabled", True):
                gif_url = get_random_birthday_gif()
                if gif_url:
                    blocks.append({
                        "type": "image",
                        "image_url": gif_url,
                        "alt_text": "Birthday celebration"
                    })
            
            try:
                app.client.chat_postMessage(
                    channel=channel,
                    text=message,
                    blocks=blocks
                )
                print(f"Posted birthday announcement for {person['name']}")
                
                if person['user_id'] in wishes:
                    del wishes[person['user_id']]
                    save_wishes(wishes)
                    
            except Exception as e:
                print(f"Error posting announcement: {e}")

def schedule_checker():
    """Background thread for scheduled tasks"""
    config = load_config()
    announcement_time = config.get("announcement_time", "09:00")
    
    schedule.every().day.at(announcement_time).do(post_birthday_announcement)
    schedule.every().day.at(announcement_time).do(post_wish_reminder)
    
    print(f"Scheduler configured for {announcement_time} Mountain Time")
    
    while True:
        schedule.run_pending()
        time.sleep(60)

# NEW COMMAND: Import birthdays from CSV
@app.command("/importbirthdays")
def handle_import_birthdays(ack, command, say):
    """Handle CSV import of birthdays"""
    ack()
    
    say("📁 Please upload your CSV file with birthdays!\n\n"
        "**CSV Format:**\n"
        "```\n"
        "Name,Birthday,Slack User ID\n"
        "John Smith,03-15,U12345678\n"
        "Sarah Jones,07-22,U87654321\n"
        "```\n\n"
        "**Requirements:**\n"
        "• Birthday format: MM-DD\n"
        "• Slack User ID starts with 'U'\n"
        "• No spaces in dates\n\n"
        "Upload your CSV file in this channel and I'll import it! 📤")

# Event listener for file uploads
@app.event("file_shared")
def handle_file_upload(event, say, client):
    """Handle CSV file upload for birthday import"""
    try:
        file_id = event['file_id']
        
        # Get file info
        file_info = client.files_info(file=file_id)
        file_data = file_info['file']
        
        # Check if it's a CSV
        if not (file_data['name'].endswith('.csv') or file_data['mimetype'] == 'text/csv'):
            return  # Not a CSV, ignore
        
        # Download file content
        file_url = file_data['url_private']
        headers = {"Authorization": f"Bearer {os.environ.get('SLACK_BOT_TOKEN')}"}
        
        import requests
        response = requests.get(file_url, headers=headers)
        csv_content = response.text
        
        # Parse CSV
        csv_reader = csv.DictReader(io.StringIO(csv_content))
        
        birthdays = load_birthdays()
        imported_count = 0
        error_count = 0
        errors = []
        
        for row in csv_reader:
            try:
                name = row.get('Name', '').strip()
                birthday = row.get('Birthday', '').strip()
                user_id = row.get('Slack User ID', '').strip()
                
                if not all([name, birthday, user_id]):
                    error_count += 1
                    errors.append(f"Missing data in row: {row}")
                    continue
                
                # Validate date format
                datetime.strptime(f"2024-{birthday}", "%Y-%m-%d")
                
                # Validate Slack User ID
                if not user_id.startswith('U'):
                    error_count += 1
                    errors.append(f"Invalid Slack ID for {name}: {user_id}")
                    continue
                
                # Save birthday
                birthdays[user_id] = {
                    "name": name,
                    "date": birthday
                }
                imported_count += 1
                
            except Exception as e:
                error_count += 1
                errors.append(f"Error processing {name}: {str(e)}")
        
        save_birthdays(birthdays)
        
        # Send result message
        result_message = f"✅ *Import Complete!*\n\n"
        result_message += f"📊 Successfully imported: *{imported_count}* birthdays\n"
        
        if error_count > 0:
            result_message += f"⚠️ Errors: {error_count} rows\n\n"
            if len(errors) <= 5:
                result_message += "*Error details:*\n"
                for error in errors:
                    result_message += f"• {error}\n"
            else:
                result_message += f"*First 5 errors:*\n"
                for error in errors[:5]:
                    result_message += f"• {error}\n"
                result_message += f"\n_...and {len(errors) - 5} more_"
        
        result_message += f"\n\n🎂 Use `/listbirthdays` to see all birthdays!"
        
        say(result_message)
        
    except Exception as e:
        say(f"❌ Error importing CSV: {str(e)}\n\nPlease check your file format and try again!")

# NEW COMMAND: Birthday Month Leaderboard
@app.command("/birthdayleaderboard")
def handle_birthday_leaderboard(ack, say):
    """Show birthday month leaderboard"""
    ack()
    
    birthdays = load_birthdays()
    
    if not birthdays:
        say("No birthdays saved yet! Use `/addbirthday MM-DD` or `/importbirthdays` to add some.")
        return
    
    # Count by month
    month_counts = {}
    for user_id, data in birthdays.items():
        month = int(data['date'].split('-')[0])
        month_name = datetime(2024, month, 1).strftime("%B")
        if month_name not in month_counts:
            month_counts[month_name] = []
        month_counts[month_name].append(user_id)
    
    # Sort by count
    sorted_months = sorted(month_counts.items(), key=lambda x: len(x[1]), reverse=True)
    
    # Get current month for context
    mountain_now = get_mountain_time()
    current_month = mountain_now.strftime("%B")
    
    message = "🏆 *Birthday Month Leaderboard* 🏆\n\n"
    
    medals = ["🥇", "🥈", "🥉"]
    for i, (month, users) in enumerate(sorted_months):
        count = len(users)
        medal = medals[i] if i < 3 else "📅"
        crown = " 👑" if month == current_month else ""
        message += f"{i+1}. {medal} *{month}* - {count} birthday{'s' if count != 1 else ''}{crown}\n"
    
    # Add fun stats
    if sorted_months:
        busiest_month = sorted_months[0][0]
        busiest_count = len(sorted_months[0][1])
        
        # Find quietest month(s)
        all_months = ["January", "February", "March", "April", "May", "June",
                     "July", "August", "September", "October", "November", "December"]
        months_with_birthdays = set(month_counts.keys())
        months_without = [m for m in all_months if m not in months_with_birthdays]
        
        message += f"\n🎂 *Busiest Month:* {busiest_month} ({busiest_count} birthdays)"
        
        if months_without:
            message += f"\n😴 *No birthdays in:* {', '.join(months_without)}"
        
        # Current month context
        if current_month in month_counts:
            current_count = len(month_counts[current_month])
            message += f"\n\n🎉 *This month ({current_month}):* {current_count} birthday{'s' if current_count != 1 else ''}"
    
    say(message)

# ENHANCED COMMAND: Team Analytics Dashboard
@app.command("/teamanalytics")
def handle_team_analytics(ack, say):
    """Show comprehensive team birthday analytics"""
    ack()
    
    birthdays = load_birthdays()
    
    if not birthdays:
        say("No birthdays saved yet! Use `/addbirthday MM-DD` or `/importbirthdays` to add some.")
        return
    
    total_birthdays = len(birthdays)
    
    # Month distribution
    month_counts = {}
    zodiac_counts = {}
    element_counts = {"Fire": 0, "Earth": 0, "Air": 0, "Water": 0}
    
    for user_id, data in birthdays.items():
        month, day = map(int, data['date'].split('-'))
        month_name = datetime(2024, month, 1).strftime("%B")
        month_counts[month_name] = month_counts.get(month_name, 0) + 1
        
        _, zodiac_name = get_zodiac_sign(month, day)
        zodiac_counts[zodiac_name] = zodiac_counts.get(zodiac_name, 0) + 1
        element = ZODIAC_ELEMENTS.get(zodiac_name)
        if element:
            element_counts[element] += 1
    
    # Calculate stats
    avg_per_month = total_birthdays / 12
    max_month = max(month_counts.items(), key=lambda x: x[1]) if month_counts else ("None", 0)
    min_month = min(month_counts.items(), key=lambda x: x[1]) if month_counts else ("None", 0)
    
    most_common_zodiac = max(zodiac_counts.items(), key=lambda x: x[1]) if zodiac_counts else ("None", 0)
    least_common_zodiac = min(zodiac_counts.items(), key=lambda x: x[1]) if zodiac_counts else ("None", 0)
    
    # Upcoming birthdays
    mountain_now = get_mountain_time()
    today = mountain_now.date()
    
    this_week = []
    this_month = []
    next_30 = []
    
    for user_id, data in birthdays.items():
        month, day = map(int, data['date'].split('-'))
        bday_this_year = date(today.year, month, day)
        if bday_this_year < today:
            bday_this_year = date(today.year + 1, month, day)
        
        days_until = (bday_this_year - today).days
        
        if days_until <= 7:
            this_week.append(user_id)
        if bday_this_year.month == today.month and bday_this_year.day >= today.day:
            this_month.append(user_id)
        if days_until <= 30:
            next_30.append(user_id)
    
    # Fun facts
    twins = find_birthday_twins()
    longest_gap = calculate_birthday_streak()
    
    # Build message
    message = f"""📈 *Team Birthday Analytics* 📈

👥 *TEAM OVERVIEW:*
• Total birthdays tracked: {total_birthdays}
• Average per month: {avg_per_month:.1f}

📅 *DISTRIBUTION:*
• Busiest month: {max_month[0]} ({max_month[1]} birthdays)
• Quietest month: {min_month[0]} ({min_month[1]} birthday{'s' if min_month[1] != 1 else ''})

⭐ *ZODIAC BREAKDOWN:*
• Most common: {most_common_zodiac[0]} ({most_common_zodiac[1]} {'people' if most_common_zodiac[1] != 1 else 'person'})
• Least common: {least_common_zodiac[0]} ({least_common_zodiac[1]} {'people' if least_common_zodiac[1] != 1 else 'person'})
• Fire signs: {element_counts['Fire']} | Earth: {element_counts['Earth']} | Air: {element_counts['Air']} | Water: {element_counts['Water']}

🎂 *UPCOMING:*
• This week: {len(this_week)} birthday{'s' if len(this_week) != 1 else ''}
• This month: {len(this_month)} birthday{'s' if len(this_month) != 1 else ''}
• Next 30 days: {len(next_30)} birthday{'s' if len(next_30) != 1 else ''}

🎉 *FUN FACTS:*
• Longest gap between birthdays: {longest_gap} days
"""
    
    if twins:
        message += f"• Birthday twins: {len(twins)} pair{'s' if len(twins) != 1 else ''}\n"
        for date, users in list(twins.items())[:2]:  # Show first 2
            user_mentions = " & ".join([f"<@{u}>" for u in users])
            message += f"  └ {user_mentions} ({date})\n"
    else:
        message += "• No birthday twins yet!\n"
    
    say(message)

@app.command("/setbirthdaychannel")
def handle_set_channel(ack, command, say):
    """Set the channel for birthday announcements"""
    ack()
    
    channel_id = command['channel_id']
    config = load_config()
    config['announcement_channel'] = channel_id
    save_config(config)
    
    mountain_now = get_mountain_time()
    current_time = mountain_now.strftime("%I:%M %p %Z")
    
    say(f"✅ Birthday announcements will be posted in this channel!\n\n"
        f"🕐 Daily checks at 9:00 AM Mountain Time\n"
        f"⏰ Current time: {current_time}")

@app.command("/addwish")
def handle_add_wish(ack, command, say):
    """Add a birthday wish"""
    ack()
    
    text = command['text'].strip()
    
    if not text:
        say("Please provide a user and message! Format: `/addwish @user Your birthday message here`")
        return
    
    parts = text.split(None, 1)
    
    if len(parts) < 2 or not parts[0].startswith('<@'):
        say("Please mention a user and include a message! Format: `/addwish @user Your birthday message here`")
        return
    
    user_id = parts[0].strip('<@>|')
    message = parts[1]
    
    birthdays = load_birthdays()
    if user_id not in birthdays:
        say(f"<@{user_id}> doesn't have a birthday saved yet!")
        return
    
    wishes = load_wishes()
    if user_id not in wishes:
        wishes[user_id] = []
    
    wishes[user_id].append({
        "from_user": command['user_id'],
        "message": message,
        "timestamp": datetime.now().isoformat()
    })
    
    save_wishes(wishes)
    
    say(f"💌 Your birthday wish for <@{user_id}> has been saved! 🎉")

@app.command("/addbirthday")
def handle_add_birthday(ack, command, say):
    """Add a birthday"""
    ack()
    
    text = command['text'].strip()
    
    if not text:
        say("Please provide a birthday date! Format: `/addbirthday MM-DD` or `/addbirthday @user MM-DD`")
        return
    
    parts = text.split()
    birthdays = load_birthdays()
    
    if parts[0].startswith('<@'):
        if len(parts) < 2:
            say("Please provide a date after the user mention!")
            return
        
        user_id = parts[0].strip('<@>|')
        birthday_date = parts[1]
    else:
        user_id = command['user_id']
        birthday_date = parts[0]
    
    try:
        test_date = datetime.strptime(f"2024-{birthday_date}", "%Y-%m-%d")
        month = test_date.month
        day = test_date.day
        zodiac_emoji, zodiac_name = get_zodiac_sign(month, day)
    except ValueError:
        say("Invalid date format! Please use MM-DD")
        return
    
    birthdays[user_id] = {
        "name": command['user_name'],
        "date": birthday_date
    }
    save_birthdays(birthdays)
    
    say(f"🎂 Birthday saved for <@{user_id}> on {birthday_date}! {zodiac_emoji} *{zodiac_name}*")

@app.command("/listbirthdays")
def handle_list_birthdays(ack, say):
    """List all birthdays"""
    ack()
    
    birthdays = load_birthdays()
    
    if not birthdays:
        say("No birthdays saved yet!")
        return
    
    sorted_birthdays = sorted(
        birthdays.items(),
        key=lambda x: datetime.strptime(f"2024-{x[1]['date']}", "%Y-%m-%d")
    )
    
    message = "🎉 *Upcoming Birthdays* 🎉\n\n"
    for user_id, data in sorted_birthdays:
        date_obj = datetime.strptime(f"2024-{data['date']}", "%Y-%m-%d")
        formatted_date = date_obj.strftime("%B %d")
        month = date_obj.month
        day = date_obj.day
        zodiac_emoji, zodiac_name = get_zodiac_sign(month, day)
        message += f"• <@{user_id}>: {formatted_date} {zodiac_emoji} *{zodiac_name}*\n"
    
    say(message)

@app.command("/removebirthday")
def handle_remove_birthday(ack, command, say):
    """Remove a birthday"""
    ack()
    
    text = command['text'].strip()
    birthdays = load_birthdays()
    
    if text.startswith('<@'):
        user_id = text.strip('<@>|').split()[0]
    else:
        user_id = command['user_id']
    
    if user_id in birthdays:
        del birthdays[user_id]
        save_birthdays(birthdays)
        say(f"Birthday for <@{user_id}> has been removed.")
    else:
        say(f"No birthday found for <@{user_id}>.")

@app.command("/birthdaytoday")
def handle_birthday_today(ack, say):
    """Check today's birthdays"""
    ack()
    
    birthday_people = check_birthdays_today()
    
    if not birthday_people:
        say("No birthdays today! 🎂")
    else:
        message = "🎉 *Happy Birthday!* 🎉\n\n"
        for person in birthday_people:
            message += f"🎂 <@{person['user_id']}> is celebrating today! {person['zodiac_emoji']} *{person['zodiac_name']}*\n"
        say(message)

@app.command("/birthdaystats")
def handle_birthday_stats(ack, say):
    """Show birthday statistics"""
    ack()
    
    birthdays = load_birthdays()
    
    if not birthdays:
        say("No birthdays saved yet!")
        return
    
    month_counts = {}
    zodiac_counts = {}
    
    for user_id, data in birthdays.items():
        month, day = map(int, data['date'].split('-'))
        month_name = datetime(2024, month, 1).strftime("%B")
        month_counts[month_name] = month_counts.get(month_name, 0) + 1
        
        _, zodiac_name = get_zodiac_sign(month, day)
        zodiac_counts[zodiac_name] = zodiac_counts.get(zodiac_name, 0) + 1
    
    mountain_now = get_mountain_time()
    current_month_name = mountain_now.strftime("%B")
    current_month_count = month_counts.get(current_month_name, 0)
    
    if month_counts:
        max_month = max(month_counts.items(), key=lambda x: x[1])
        max_month_name = max_month[0]
        max_month_count = max_month[1]
    else:
        max_month_name = "None"
        max_month_count = 0
    
    if zodiac_counts:
        max_zodiac = max(zodiac_counts.items(), key=lambda x: x[1])
        max_zodiac_name = max_zodiac[0]
        max_zodiac_count = max_zodiac[1]
    else:
        max_zodiac_name = "None"
        max_zodiac_count = 0
    
    upcoming_this_month = []
    today = mountain_now.date()
    for user_id, data in birthdays.items():
        bday_date = datetime.strptime(f"2024-{data['date']}", "%Y-%m-%d").date()
        if bday_date.month == today.month and bday_date.day >= today.day:
            month, day = map(int, data['date'].split('-'))
            zodiac_emoji, _ = get_zodiac_sign(month, day)
            upcoming_this_month.append(f"<@{user_id}> ({data['date']}) {zodiac_emoji}")
    
    message = f"""📊 *Birthday Statistics* 📊

📅 *Total Birthdays Tracked:* {len(birthdays)}

🎂 *This Month ({current_month_name}):* {current_month_count} birthday{"s" if current_month_count != 1 else ""}

🏆 *Most Popular Month:* {max_month_name} ({max_month_count} birthday{"s" if max_month_count != 1 else ""})

⭐ *Most Common Sign:* {max_zodiac_name} ({max_zodiac_count} {"people" if max_zodiac_count != 1 else "person"})

🎉 *Upcoming This Month:*
"""
    
    if upcoming_this_month:
        for person in upcoming_this_month:
            message += f"• {person}\n"
    else:
        message += "• None\n"
    
    say(message)

@app.event("app_mention")
def handle_mentions(body, say):
    """Respond to mentions"""
    say(f"Hi <@{body['event']['user']}>! 👋 I'm the Birthday Bot!\n\n"
        f"*Commands:*\n"
        f"• `/addbirthday MM-DD` - Add a birthday\n"
        f"• `/importbirthdays` - Import from CSV\n"
        f"• `/listbirthdays` - See all birthdays\n"
        f"• `/addwish @user message` - Add birthday wish\n"
        f"• `/birthdayleaderboard` - Month rankings\n"
        f"• `/teamanalytics` - Full analytics\n"
        f"• `/setbirthdaychannel` - Set channel")

@app.message("birthday")
def respond_to_birthday_message(say):
    """Respond to birthday mentions"""
    say("Did someone say birthday? 🎂 Use `/listbirthdays` to see upcoming birthdays!")

if __name__ == "__main__":
    scheduler_thread = threading.Thread(target=schedule_checker, daemon=True)
    scheduler_thread.start()
    
    mountain_now = get_mountain_time()
    current_time = mountain_now.strftime("%I:%M %p %Z")
    print(f"📅 Scheduler started - checks at 9 AM Mountain Time")
    print(f"⏰ Current Mountain Time: {current_time}")
    
    handler = SocketModeHandler(app, os.environ.get("SLACK_APP_TOKEN"))
    print("⚡️ Birthday Bot v3 is running!")
    handler.start()
