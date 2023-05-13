# sn0-archive

*Reddit archiving scripts*

## requirements

- Minimum Python 3.11.3 (for sqlite)
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
SN0_PATH = "sn0-archive.sqlite3"
USER_AGENT = "sn0-archiver"
MEDIA_PATH = "sn0-media"
GALLERY_DL_COMMAND = "gallery-dl"
ICON_IMG_THREADS = 8
SUBMISSION_MEDIA_THREADS = 2
```

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

Optionally, unsave posts after archiving. This may be necessary since the reddit API only shows a limited number of posts.

```shell
python 2_archive_reddits.py and unsave
```

## Step 6: Archive media

```shell
python 3_archive_media.py
```

## known issues

- no way to specify comment limit
