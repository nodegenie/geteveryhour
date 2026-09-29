# How to write an EveryHour post

EveryHour publishes one post every hour, Pacific time, under Tineessa Nelson's byline.

## Choosing the topic
- Search for what people are talking about today: news, trending topics, sports, weather, culture, tech, money, holidays and observances, the season, the day of the week.
- Pick ONE topic that is timely today and relatable to ordinary people.
- Read the last 24 hours of posts in `posts/` first. Do not repeat a topic or an angle that is already covered.
- Rotate topics through the day across: Everyday life, Work, Money, Tech, Culture, Sports, Wellness, Relationships, News, Seasons.
- Only state facts you confirmed in search results. If unsure, write about the everyday feeling of the moment instead of specifics.
- No partisan opinions. Do not treat tragedies lightly. Do not name private individuals.

## Voice
- First person, warm, plain and grounded. It should sound like a thoughtful person talking, not marketing.
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

`publishedAt` is the top of the current hour in UTC (minutes and seconds are 00).

If a file for the same Pacific date and hour already exists, do not write another one.

Run `python3 build.py` to check the post builds without errors, then commit only the new file in `posts/` with the message `Post: <title>` and push to `main`. The site deploys itself.
