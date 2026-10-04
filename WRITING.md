# How to write an EveryHour post

EveryHour is "useful answers for every hour of your California day." It publishes five practical posts a day, one for each part of the day, under Tineessa Nelson's name. Every post is labeled as written with AI, and Tineessa is responsible for what the site publishes. The home page also shows "This hour in California," a panel of live National Weather Service alerts that the site refreshes on every hourly rebuild; nothing needs to be written for it.

The goal is fewer, better posts that people still find useful months from now. Quality and lasting usefulness come before volume, every time.

## Schedule: the five parts of the day
Each slot has its own focus. Choose each post so it fits its slot.

| Slot (Pacific) | Part of the day | Focus |
|---|---|---|
| 7 AM | Morning | Getting ready and the commute: driving, transit, gas, traffic rules, breakfast, getting kids out the door |
| 10 AM | Late morning | Errands and appointments: DMV, doctor and pharmacy, post office, shopping, government services |
| 1 PM | Midday | Work and money: paychecks, taxes, benefits, bills, budgeting, job rights, scams |
| 4 PM | Afternoon | Home and family: home upkeep, utilities, kids and school, pets, older relatives, cooking |
| 7 PM | Evening | Tonight and tomorrow: weather and safety, planning ahead, seasonal prep, sleep, things to do this week |

- Posts are written in one batch each morning at about 5 AM Pacific for that day's five slots, skipping any slot that already has a file. Each file's `publishedAt` is its slot. The site rebuilds every hour and only shows posts whose time has arrived, so writing them ahead of time is correct.
- If there are not five topics worth publishing on a given day, publish fewer. An empty slot is better than a thin post.

## Who the posts are for
Adults living in California who want practical answers about everyday life: money, home, health and safety, work, weather and seasons, local services, and things to do. Where rules, prices or programs differ by state, give the California version first (state agencies, California utilities, Covered California, Cal Fire, Caltrans, CA DMV, county services). A reader outside California should still find the post clear, but California readers come first.

## Choosing the topics
Each day's five posts follow this mix:
- **At least 3 evergreen posts.** These answer a question people will still be searching for in six months or a year: how-to guides, explainers, checklists, "what to know before" pieces. Examples: how long leftovers last, how to read a PG&E bill, what to plant in fall in California, how to appeal a parking ticket in Los Angeles, what Covered California's income limits mean, how to prepare a go-bag for wildfire season.
- **Up to 2 timely posts**, only when something is happening that California readers need to act on: heat or fire warnings, power shutoffs, new state laws taking effect, enrollment deadlines, DMV or tax changes, major local events. A timely post must still give lasting steps, so it stays useful after the day passes.
- Seasonal topics count as evergreen when they are written to be reused every year (for example, "how to keep pets safe in a California heat wave"). Do not put the year in the title of an evergreen post unless the facts change yearly.

Avoid these topics, because large outlets already own them and the posts are worthless by the next morning:
- Game times, TV listings, box office, award shows and celebrity news.
- National "holiday of the day" observances (National X Day), unless there is a real, useful California angle and the post would stand on its own without the observance.
- Market moves, daily headlines or anything where the whole value is "this happened today."

Before choosing topics:
- Read every post in `posts/` from the last 30 days (titles and slugs at minimum). Do not repeat a topic or an angle already covered. An evergreen topic covered before can only come back as a clearly different question.
- Set each post's `topic` to one of: Money, Home, Health, Safety, Work, Seasons, Tech, Everyday life, Local. Rotate them through the week so no topic dominates.
- Check what people are searching for: use search results, "People also ask" style questions and official agency news pages. Pick topics with a real, specific question behind them.

## Value to readers (every post must pass this)
A post is only worth publishing if someone who reads it walks away knowing or able to do something they could not before.
- Start from one real question a reader would type into a search engine. The title and the first paragraph answer it directly.
- Include specifics confirmed in search results: amounts, deadlines, eligibility rules, phone numbers, official links, step-by-step instructions, and where things differ by county or utility.
- Cite official and primary sources first: California state agencies, county and city sites, utilities, federal agencies, universities and UC Cooperative Extension, established health systems. Use news articles only for timely facts.
- Add 3 to 5 `keyPoints`: short, scannable lines with the most useful specifics. They must not just repeat the title.
- Add 1 to 3 `sources`: the pages from your search results that confirm the post's facts, with their real titles and URLs. Never invent or guess a URL; only list pages that appeared in your search results.
- Only state facts you confirmed in search results. If you cannot confirm a detail, leave it out.
- Do not pad. Do not restate the title or dek in the body. Cut any paragraph that only sets a mood.
- Do not write two posts that give the same advice in different words, including across the last 30 days.
- No partisan opinions. Do not treat tragedies lightly. Do not name private individuals.

## Honesty about AI (read this first)
EveryHour is openly written with AI. The site says so on every post and on the About page. The posts must never pretend otherwise.
- Never invent personal experiences, memories, habits, possessions, family members, homes, jobs, bills, health history, or anything else presented as something the author did, has, or lived through. No "I used to...", "my rent...", "last night I...", "when I go for a walk...", "my coworker...".
- Never claim the author wrote, read, reviewed, tried, tasted, watched or attended something.
- Write about the reader and the topic: use "you", "many people", or plain statements. "I think" is fine for a mild, non-partisan observation, as long as it is not a claimed experience.
- Health, money, legal and safety topics: share general, widely accepted information from official sources and point readers to a doctor, official agency or other qualified source for their own situation. Never give personal medical, financial or legal advice.

## Voice
- Warm, plain and grounded. It should sound like a thoughtful, well-informed neighbor, not marketing.
- Complete sentences and courteous phrasing. Plain wording is fine even if slightly redundant.
- No stock idioms, no hype, no sales copy, no em-dash asides, no "not X, but Y" constructions, no rhetorical colon reveals.
- Evergreen posts: 400 to 700 words, organized so a reader can scan it. Short paragraphs; use numbered steps in the body text when the post is a how-to ("Step 1: ...").
- Timely posts: 250 to 450 words.
- End with one small, practical next step the reader can take today.

## SEO
- `title`: the reader's question or its plain answer, under 70 characters, using the words people actually search. Include "California" or a city or county name when the answer is specific to the state or place.
- `dek`: one sentence under 160 characters that gives the core answer. It is the meta description.
- `keywords`: 3 to 5 search phrases. `tags`: 3 to 5 short lowercase tags, including `california` when relevant.
- Slugs describe the question, without dates for evergreen posts (`how-long-do-leftovers-last-in-the-fridge`, not `sunday-meal-prep-october-4`).

## File format
Save as `posts/YYYY-MM-DD-HH-<slug>.json`, using the Pacific date and 24-hour hour of the slot. The slug is lowercase letters, digits and hyphens, under 60 characters.

```json
{
  "slug": "short-kebab-slug",
  "title": "...",
  "dek": "...",
  "topic": "Money",
  "tags": ["tag", "tag", "tag"],
  "keywords": ["phrase", "phrase", "phrase"],
  "publishedAt": "2026-09-29T14:00:00Z",
  "readMin": 3,
  "keyPoints": ["Short, specific fact or step.", "Another one."],
  "sources": [{"title": "Page title as shown in search", "url": "https://..."}],
  "body": ["Paragraph one.", "Paragraph two.", "Paragraph three."]
}
```

`publishedAt` is the top of that post's hour in UTC (minutes and seconds are 00). Example: 7 AM Pacific on September 29, 2026 (PDT, UTC-7) is `2026-09-29T14:00:00Z`. Compute it with code, not by hand.

If a file for the same Pacific date and hour already exists, do not write another one.

Run `python3 build.py` to check the posts build without errors (scheduled posts are skipped silently until their hour; that is expected). Commit the new files in `posts/` and any change to `sponsors/queue.json` in one commit with the message `Posts for YYYY-MM-DD`, and push to `main`. The site deploys itself.

## Updating older evergreen posts
Once a week (on Mondays), check up to three evergreen posts older than 60 days whose facts may have changed (prices, deadlines, program rules). If a fact changed, update the file in place, keep its slug and file name, add `"updatedAt": "<ISO UTC time>"`, and replace any outdated source. Do not change a post just to change it.

## Sponsors
Paid sponsors are listed in `sponsors/queue.json` (a JSON array). Each entry looks like:
```json
{"id": "cs_...", "name": "Business name", "url": "https://example.com", "blurb": "One sentence about the business.", "paidAt": "2026-09-29T15:00:00Z", "placedIn": null}
```
- Place each entry whose `placedIn` is null into exactly ONE of the day's posts. Only one sponsor per post.
- Choose the post whose topic fits the business best; otherwise use the earliest slot of the day without a sponsor.
- Add it to the post file as:
  `"sponsor": {"name": "...", "url": "https://...", "blurb": "..."}`
- The blurb is one plain sentence, under 140 characters, rewritten in a neutral voice if needed. Do not mention the sponsor in the post body, and never let a sponsor influence what a post says.
- Set that entry's `placedIn` to the post's file name.
- Do not place a business that is adult content, gambling, weapons, drugs, a political campaign, a crypto or get-rich scheme, or anything deceptive. Leave `placedIn` as null, add `"hold": "<reason>"`, and report it so Tineessa can refund it.
- If there are more unplaced sponsors than the day's posts, place as many as there are posts and leave the rest for the next day, oldest payment first.
