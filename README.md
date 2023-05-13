# sn0-archive

## Step 1: Create a reddit script application

*Instructions are from [@manojkarthick/reddsaver](https://github.com/manojkarthick/reddsaver)*

1. Create a new script application at https://www.reddit.com/prefs/apps
   - Click on create an app at the bottom of the page
   - Input a name for your application, for example: -reddsaver
   - Choose "script" as the type of application
   - Set "http://localhost:8080" or any other URL for the redirect url
   - Click on "create app" - you should now see the application has been created
   - Under your application name, you should see a random string - that is your client ID
   - The random string next to the field "secret" is your client secret
2. Copy the client ID and client secret information returned

## Step 2: Create `_secrets.py`

`_secrets.py` is used by `config.py`. Here's an example:

```py
client_id = "GJPeNG1ngA3"
client_secret = "sdfJsdfsd_dsfo_sdflksjf02"
username = "username"
password = "password"
```

## Step 3: Edit your config.py

The default `config.py` looks like this:

```py
from _secrets import *
sn0_path = "sn0-archive.sqlite3"
user_agent = "sn0-archiver"
media_path = "sn0-media"
```

## Step 4: Provision the database

```shell
python 1_provision.py
```

## Step 5: Archive saved reddit posts and comments

```shell
python 2_archive_reddits.py
```

Optionally, unsave posts after archiving. This may be necessary since the reddit API only shows a limited number of posts.

```shell
python 2_archive_reddits.py and unsave
```

## Step 6: Archive media

```shell
python 3_archive_media.py
```
