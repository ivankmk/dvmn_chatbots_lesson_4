# Quiz chatbots

This is the Quiz bot implemented in Telegram and VK.

## How to use

**In Telegram**

Begin the game with the command ```/start```


**in VK**

Begin the game by typing ```Привет```

## How to install

### On local machine

Create an .env file in the root of the directory with the following variables
```python

TG_TOKEN = "Your telegram API token"
REDIS_HOST = "Your Redis host"
REDIS_PORT = "Your Redis port"
REDIS_USERNAME = "Your Redis username"
REDIS_PASSWORD = "Your Redis password"
JSON_FILE = "Your JSON file with Questions and Answers"
VK_TOKEN = "Your VK token"
```

**VK**

Create a vk group, in your group, click Manage -> Working with API -> Create key (allow sending messages)

**Telegram**

Create a telegram bot using [@BotFather] (https://telegram.me/botfather). Get your bot token

Load Quiz questions (https://dvmn.org/media/modules_dist/quiz-questions.zip) and convert txt files into JSON dataset using function generate_json from utils.py

Python3 must already be installed. Then use pip (or pip3, there is a conflict with Python2) to install the dependencies:

```python
pip install -r requirements.txt
```

Run the scripts with the following commands:

```python
python vk_bot.py
```

```python
python tg_bot.py
```


### Deploy to Heroku

Clone the repository, login or register on [Heroku](https://dashboard.heroku.com)

Create a new Heroku application, connect your github account in the Deploy tab and select the required repository.

In the Settings tab, set the environment variables as Config Vars.

Activate the bot in the Resourses tab