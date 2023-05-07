create table redditors(
   id text primary key,
   name text not null,
   created_utc integer not null,
   icon_img text not null
) strict, without rowid;

create table subreddit(
   id text primary key,
   created_utc integer not null,
   description text,
   display_name text,
   name text not null,
   over18 integer not null,
   public_description text,
   subscriber_count integer
) strict, without rowid;

create table submission(
   id text primary key,
   author text references redditors(id) not null,
   author_flair_text text,
   created_utc integer not null,
   distinguished integer not null,
   edited integer not null,
   is_original_content integer not null,
   is_self integer not null,
   link_flair_text text,
   locked integer not null,
   name text not null,
   comment_count integer not null,
   over_18 integer not null,
   permalink text not null,
   saved integer not null,
   score integer,
   selftext text,
   spoiler integer not null,
   stickied integer not null,
   subreddit text references subreddit(id) not null,
   title text not null,
   upvote_ratio real not null,
   url integer not null
) strict, without rowid;

create table comments(
   id text primary key,
   author text references redditors(id) not null,
   author_flair_text text,
   body text,
   created_utc integer not null,
   distinguished integer not null,
   edited integer not null,
   is_submitter integer not null,
   parent_is_comment text references comments(id),
   parent_is_submission text references submissions(id),
   permalink text not null,
   saved integer not null,
   score integer,
   submission text not null references submissions(id)
) strict, without rowid;
