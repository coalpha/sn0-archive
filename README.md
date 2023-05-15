# sn0-archive v1.0.0

<img src="./misc/icon.png" max-width="10%"/>

*Reddit archiving scripts*

## requirements

- A recent Python version for sqlite v3.37.0. I have python 3.11.3 and it works just fine.
- [gallery-dl](https://github.com/mikf/gallery-dl)
- praw (`pip install praw`)
- disable 2fa

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

`_secrets.py` is used by `_config.py`. Here's an example:

```py
CLIENT_ID = "GJPeNG1ngA3"
CLIENT_SECRET = "sdfJsdfsd_dsfo_sdflksjf02"
USERNAME = "username"
PASSWORD = "password"
```

## Step 3: Edit your _config.py

The default `_config.py` looks like this:

```py
from _secrets import *
SN0_DB_PATH = "sn0-archive.sqlite3"
MEDIA_PATH = "sn0-media"
USER_AGENT = "Python:sn0-archiver:v1.0.0 (by /u/coalfa)"
GALLERY_DL_COMMAND = "gallery-dl"
ICON_IMG_THREADS = 8
SUBMISSION_MEDIA_THREADS = 2
# number of MoreComments to unpack. to archive all comments, set to None
MORECOMMENTS_LIMIT = 32
# number of comments per post to archive, set to None for no limit
COMMENT_LIMIT = None
```

### Comment truncation

With `MORECOMMENTS_LIMIT` and `COMMENT_LIMIT` set to `None`, sn0-archiver will archive all comments. This, however, is quite time consuming and I don't recommend it.

### gallery-dl issues

If you're having difficulty getting `gallery-dl` to show up on your path. Find the `site-packages` directory that your python (or python3) is using. Then add that directory to your `$PYTHONPATH`. For example:

```bash
export PYTHONPATH="$PYTHONPATH:/Library/Frameworks/Python.framework/Versions/3.11/lib/python3.11/site-packages"
```

Next, change the `GALLERY_DL_COMMAND`

```py
GALLERY_DL_COMMAND = "python -m gallery_dl"
# or
GALLERY_DL_COMMAND = "python3 -m gallery_dl"
```

## Step 4: Provision the database

```shell
python 1_provision.py
```

## Step 5: Archive saved reddit posts and comments

```shell
python 2_archive_reddits.py
```

Optionally, unsave posts after archiving. This may be necessary since the reddit API only shows a limited number of saved posts (1000). You can exit this using `ctrl+c` without losing progress on previously saved 

```shell
python 2_archive_reddits.py and unsave
```

If you mistakenly unsaved things, you can run `resave.py` to resave all comments and submissions. It won't be in the order you saved them in though.

## Step 6: Archive media

I recommend running this periodically while `2_archive_reddits.py` is running.

```shell
python 3_archive_media.py
```

## known issues

- `3_archive_media.py` randomly stops sometimes and needs to be restarted.
