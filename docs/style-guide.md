# Editorial Voice

*How we tell it. One point, then the story, in plain words.*

This archive began as a detective's notebook, and it still is one. The pages people read are a reporter's story: simple, casual, matter-of-fact, and warm. The spirit is the plain awe you hear when someone like Mike Rowe, Paul Harvey, Anderson Cooper, Denzel Washington, or Morgan Freeman tells a true thing and then gets out of its way. That is a spirit, not a script. We do not borrow anyone's catchphrase.

## The voice

**One point, told straight.** Every article has one main point, stated in the opening: what makes this story unique in hot rodding. The rest is that story, beginning to end. The ending lands on the same point.

- **Assume the basics.** Readers know drag racing, a quarter mile, an ET, a mph figure, a hot rod, and a car show. Do not define them. A sentence that exists to teach a common word is a sentence to cut.
- **Explain what is actually unusual.** A person. A novel idea. An odd or one-of-a-kind detail, and why it stood out in the industry. Boats down a drag strip. A national meet held after the bosses had said no. A wife and three children as the pit crew. Say it once, plainly.
- **Keep the detail its real size.** Do not inflate a local fact into a legend, and do not turn a strange fact into a joke or a lecture. No melodrama. If it was a lease that was not renewed, say that.
- **Short, plain sentences.** Casual. Spoken. "Ran," not "was observed to achieve." The story keeps moving. No aside that stops it to define a term.
- **Warm, never snide.** We can like these people. We do not sneer, and we do not pile on adjectives to manufacture awe. The awe is already in the fact, if the fact is the right one.
- **Cited in the sentence.** The footnote stays on the claim. A quoted line stays verbatim. A small human detail is welcome when a source gives it, and only then.
- **Period flavor, not parody.** A shop-floor word the sources use is fine. Fake slang is not. If we would wince hearing a person say it, we do not write it.

## The shape of a piece

1. **Open on the point.** Say what is unique here, in plain words. Not a Wikipedia lead, and not a definition. No "X was a notable figure in…" openings, ever.
2. **Tell it straight through.** From the beginning of the story to the end, in time when the sources give a time. Each paragraph follows the one before. A transition ("That fall...", "The town said no.") is better than a new subhead. Subheads are used sparingly (two or three at most), and they should be specific, not labels like "Background" or "Legacy." No bullet lists inside the story. No glossary detour in the middle.
3. **Keep the detective's notebook at the back.** When sources conflict, that is a feature, not a flaw, but it is not argued mid-story. The claim stays in place with its footnote and a superscript ⚠ (sources disagree) or ◐ (single source so far). What each source says, and why the disagreement is interesting, goes into the last section, **Open questions & disputed details**, which links back to the spot. A short hedge in the sentence itself ("by one account", "he recalled") stays.
4. **Land on the point.** The last lines are the same truth the opening named, now that the reader has watched it happen. Do not summarize the whole page. Do not moralize. Do not add a sign-off.

## The facts (non-negotiable)

Narrative technique here means **structure, pacing, word choice, and framing. Never invention.**

What we may not add is a fact the cited sources did not give: a hometown, a feeling, a color, a motive, a mileage, what a nickname referred to, what the weather was. If the sources do not say, the sentence does not guess, and it does not pause to teach a word the reader already has. The gap stays in Open questions, or it stays unsaid.

- **No fact, number, date, color, scene detail, motive, thought, or quote may appear that is not already in the sourced content.** We do not know what the weather was, what anyone felt, or what anyone said unless a source says so.
- **No invented dialogue, no composite scenes, no imagined interiors.** "He must have…" and "one can picture…" are banned. If we want the reader to see it, we find the line in the source that shows it.
- **Quotes stay verbatim**, with speaker, source and date, exactly as they were checked against the original.
- **Every footnote stays attached to the claim it supports.** If a sentence is moved or merged, the citation moves with it.
- **Uncertainty is never upgraded.** A ⚠ conflict stays a conflict. A ◐ single-source claim stays flagged. "Reportedly," "according to," and "by his own account" keep their jobs. The sources not agreeing is part of the fun, so we say so.
- **Answered questions leave the notebook.** When an Open questions item is resolved, it leaves the list: fold the answer into the story with its citations, remove the inline marker and the item, update `docs/data/canonical.yml` (value and snippet) if the fact is canonical, log it under **Resolved** on the Research Trail with the date and the source that settled it, and update any Quick answer that cited it. A resolved conflict is told in the story, not kept as a struck-through item.
- **Reference pages stay reference pages.** The Timeline, Patents, Index, Bibliography, Image Credits, Source Standards and Highlights archive are tools, not stories, and are kept clean.

The fields every page carries, and the one home for each repeated fact, are in [Article Schema](reference/article-schema.md). Everything else in [Source Standards](reference/source-standards.md) still applies: confidence ratings, the record box on every article, credited images, and links out for photos we cannot host.

## Citing a Voices page

Voices pages are built from quotes, so they cite differently from stories. Each quote carries its source on the line under it, where the reader is looking, instead of in a footnote:

```markdown
> "When the war ended, I started construction on my fuel injector…"

— Stuart Hilborn to the American Hot Rod Foundation, quoted by Mark Vaughn, *Autoweek*, Dec 15, 2013. Access 2026-10-14. https://www.autoweek.com/news/a1946706/fuel-injection-pioneer-stuart-hilborn-1917-2013/

*Told years later: an AHRF interview late in life.*
```

- **The attribution line** starts with an em dash and gives, in this order: the speaker; who they told it to (if someone else published it, "quoted by" that writer); the publication in italics; the date it was published; "Access YYYY-MM-DD."; and the URL. A second quote from the same source may say "quoted in the same *Autoweek* obituary" with its access date and no URL.
- **The memory label** follows in italics, on its own line: *Told years later* (with the gap between event and telling, if known), *Secondhand* (the speaker relays someone else's account, or a writer quotes an earlier interview), or *⚠ Conflicts with the record* (with a link to the page that has the evidence). A quote can carry more than one.
- **Prose between quotes** that states a fact the quote doesn't (a date, a place, a result) takes an ordinary footnote, as on any story page. A Voices page with no such prose may have no footnotes at all.
- **⚠ and ◐ markers** work as on story pages and point to the page's own Open questions items.
- When a story page uses the quote in its "In their own words" box, it names the speaker, publication and year and links to the Voices page ("Full context in Voices"), which carries the full citation.

## What we avoid

- **Glossary prose**: defining a quarter mile, an ET, a red light, a gasser, a flathead, or a street rod in the middle of a story.
- **Inflated details**: a paragraph on a nickname the sources never explain, or three sentences where the fact was one.
- **Listicle prose**: paragraphs that are really bullet points with the bullets taken off.
- **Encyclopedia phrases**: "is a notable," "played a significant role," "is widely regarded as," "legacy" as a subhead, "in conclusion."
- **Filler openings**: "In the world of hot rodding…," "Throughout history…"
- **Purple excess**: three adjectives where one noun would do, engines "roaring" into every sunset. Warmth is pacing and real detail, not decoration.
- **Fake drama**: stakes the sources don't show. If it was a quiet little business decision, we let it be a quiet little business decision, and let the facts supply the charm.
- **Fake certainty**: smoothing a disputed date into a clean one because it reads better. Inventing the missing half of a nickname, a jet car's body style, or a town's character because the sentence would be smoother with it.

## A quick test before anything ships

1. Can you say this article's one point in a single sentence, and does the opening say it?
2. Did we stop to define drag racing, a quarter mile, an ET, a mph number, a hot rod, or a car show? If yes, cut that sentence.
3. Is the unusual detail still its real size, and is every number, date, name, and color still on its footnote?
4. Is each ⚠ and ◐ still there, and still honest, with its item in Open questions? And is everything left in Open questions still open? When an Open questions item is resolved, it leaves the list: fold the answer into the story with its citations, remove the inline marker and the item, update `docs/data/canonical.yml` (value and snippet) if the fact is canonical, log it under **Resolved** on the Research Trail with the date and the source that settled it, and update any Quick answer that cited it.
5. Does the story run from beginning to end, without a lecture in the middle? If a subhead or aside stops the thought, cut it or move it to Open questions.
6. Is the summary in the front matter true to the article, hedges included? Does a fact told elsewhere link to its one canonical home?
7. Did we cut a quote, move a citation off its claim, or add a detail "for color"? If yes, undo it.
8. Does the ending land on the same point the opening named?

## Where a new page goes
File each page in the department that matches its subject, not its source type: see the ten questions in [How the Site Is Organized](taxonomy.md#how-to-choose-a-department). Local or homegrown sourcing is shown with the Grassroots badge in the article record, never with a folder.
