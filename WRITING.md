# How to write an EveryHour post

EveryHour publishes one post every hour, Pacific time, under Tineessa Nelson's name. Every post is labeled as written with AI, and Tineessa is responsible for what the site publishes.

Posts are written in one batch each morning at about 5 AM Pacific: one file for each of the next 24 hours (6 AM today through 5 AM tomorrow), skipping any hour that already has a file. Each file's `publishedAt` is its hour. The site rebuilds every hour and only shows posts whose hour has arrived, so writing them ahead of time is correct.

## Choosing the topics
- Pick 24 different topics for the day, one per hour, and match each one to its time of day (mornings: commutes, coffee, getting started; midday: work and lunch; evenings: sports, TV, family, winding down; late night: sleep and quiet thoughts).
- Search for what people are talking about today: news, trending topics, sports, weather, culture, tech, money, holidays and observances, the season, the day of the week.
- Every topic should be timely today and relatable to ordinary people.
- Read the previous day's posts in `posts/` first. Do not repeat a topic or an angle that is already covered, and do not repeat a topic within the same day.
- Rotate topics through the day across: Everyday life, Work, Money, Tech, Culture, Sports, Wellness, Relationships, News, Seasons.
- Only state facts you confirmed in search results. If unsure, write about the everyday feeling of the moment instead of specifics.
- No partisan opinions. Do not treat tragedies lightly. Do not name private individuals.

## Honesty about AI (read this first)
EveryHour is openly written with AI. The site says so on every post and on the About page. The posts must never pretend otherwise.
- Never invent personal experiences, memories, habits, possessions, family members, homes, jobs, bills, health history, or anything else presented as something the author did, has, or lived through. No "I used to...", "my rent...", "last night I...", "when I go for a walk...", "my coworker...".
- Never claim the author wrote, read, reviewed, tried, tasted, watched or attended something.
- Write about the moment and the reader: use "you", "many of us", "a lot of people", or plain statements about the topic. "I think" or "it seems to me" is fine for a mild, non-partisan observation, as long as it is not a claimed experience.
- Health, money, legal and safety topics: share general, widely accepted information from search results and point readers to a doctor, official agency or other qualified source for their own situation. Never give personal medical, financial or legal advice.
- Each post must add something useful: a confirmed fact, context, or a practical takeaway. Do not publish filler that only restates the title.

## Voice
- Warm, plain and grounded. It should sound like a thoughtful person talking, not marketing. Follow the honesty rules above.
- Complete sentences and courteous phrasing. Plain wording is fine even if slightly redundant.
- No stock idioms, no hype, no sales copy, no em-dash asides, no "not X, but Y" constructions, no rhetorical colon reveals.
- 150 to 280 words in 3 to 5 short paragraphs.
- End with one small, practical, relatable takeaway.

## SEO
- `title`: a clear statement of the thought, under 70 characters, that includes a natural search phrase people would type.
- `dek`: one sentence under 160 characters. It is the meta description.
- `keywords`: 3 to 5 search phrases. `tags`: 3 to 5 short lowercase tags.

## File format
Save as `posts/YYYY-MM-DD-HH-<slug>.json`, using the Pacific date and 24-hour hour. The slug is lowercase letters, digits and hyphens, under 60 characters.

```json
{
  "slug": "short-kebab-slug",
  "title": "...",
  "dek": "...",
  "topic": "Everyday life",
  "tags": ["tag", "tag", "tag"],
  "keywords": ["phrase", "phrase", "phrase"],
  "publishedAt": "2026-09-29T02:00:00Z",
  "readMin": 1,
  "body": ["Paragraph one.", "Paragraph two.", "Paragraph three."]
}
```

`publishedAt` is the top of that post's hour in UTC (minutes and seconds are 00). Example: 7 AM Pacific on September 29, 2026 (PDT, UTC-7) is `2026-09-29T14:00:00Z`.

If a file for the same Pacific date and hour already exists, do not write another one.

Run `python3 build.py` to check the posts build without errors (scheduled posts are skipped silently until their hour; that is expected). Commit the new files in `posts/` and any change to `sponsors/queue.json` in one commit with the message `Posts for YYYY-MM-DD`, and push to `main`. The site deploys itself.


## Sponsors
Paid sponsors are listed in `sponsors/queue.json` (a JSON array). Each entry looks like:
```json
{"id": "cs_...", "name": "Business name", "url": "https://example.com", "blurb": "One sentence about the business.", "paidAt": "2026-09-29T15:00:00Z", "placedIn": null}
```
- Place each entry whose `placedIn` is null into exactly ONE of the day's posts. Only one sponsor per post.
- Choose the post whose topic fits the business best; otherwise use a daytime hour (8 AM to 8 PM).
- Add it to the post file as:
  `"sponsor": {"name": "...", "url": "https://...", "blurb": "..."}`
- The blurb is one plain sentence, under 140 characters, rewritten in a neutral voice if needed. Do not mention the sponsor in the post body.
- Set that entry's `placedIn` to the post's file name.
- Do not place a business that is adult content, gambling, weapons, drugs, a political campaign, a crypto or get-rich scheme, or anything deceptive. Leave `placedIn` as null, add `"hold": "<reason>"`, and report it so Tineessa can refund it.
- If there are more unplaced sponsors than posts, place 24 and leave the rest for the next day.
