import _config
from bridge import *

reddit = praw.Reddit(
   username=_config.USERNAME,
   password=_config.PASSWORD,
   client_id=_config.CLIENT_ID,
   user_agent=_config.USER_AGENT,
   client_secret=_config.CLIENT_SECRET,
)
assert(reddit.read_only == False)

me = cast(Redditor, reddit.user.me())
print(f"resaving to u/{me.name}")

conn = bridge()

for (saved,) in conn.execute("select id from submissions where saved = 1").fetchall():
   print(f"+ s/{saved}")
   reddit.submission(saved).save()

for (saved,) in conn.execute("select id from comments where saved = 1").fetchall():
   print(f"+ c/{saved}")
   reddit.comment(saved).save()
