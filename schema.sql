create table redditors(
   id text primary key,
   name text not null,
   created_utc integer not null,
   icon_img text not null
) strict, without rowid;

create table subreddits(
   id text primary key,
   created_utc integer not null,
   description text,
   display_name text,
   name text not null,
   over18 integer not null,
   public_description text,
   subscriber_count integer
) strict, without rowid;

create table submissions(
   id text primary key,
   author text references redditors(id), -- u/[deleted]
   author_flair_text text,
   created_utc integer not null,
   distinguished integer not null,
   edited integer not null,
   is_gallery integer not null,
   is_original_content integer not null,
   is_selfpost integer not null,
   link_flair_text text,
   name text not null,
   comment_count integer not null,
   over_18 integer not null,
   permalink text not null,
   saved integer not null,
   score integer,
   selftext text,
   spoiler integer not null,
   stickied integer not null,
   subreddit text references subreddits(id) not null,
   title text not null,
   upvote_ratio real not null,
   url text not null
) strict, without rowid;

create table comments(
   id text primary key,
   author text references redditors(id), -- u/[deleted]
   author_flair_text text,
   body text,
   created_utc integer not null,
   distinguished integer not null,
   edited integer not null,
   is_op integer not null,
   parent_comment text references comments(id), -- if null, then parent is submission
   permalink text not null,
   saved integer not null,
   score integer not null,
   stickied integer not null,
   submission text not null references submissions(id)
) strict, without rowid;
