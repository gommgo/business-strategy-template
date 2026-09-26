2. **"The Doherty Threshold allows you to make the interface slower if you add animation".** The law's page does indeed say: "deliberately adding a delay can increase perceived value and instill trust, even when the process takes much less time" [M8]. This is a **separate claim about perceived value** without any reference to research, and it contradicts the entire Nielsen and RAIL line of thinking. `[debatable]` Practical takeaway: **don't slow the interface down on purpose**, except in narrow cases where an instant result undermines trust (for example, "checking" a document) — and even then, show exactly what is happening.
3. **"Progress bars rescue any delay".** The law's page has a correct formulation: "progress bars make waiting tolerable **regardless of their accuracy**" [M8]; but NN/g also has a caveat: for 2–10 s, a precise percentage indicator can violate "display inertia" [M18].

**How to use the threshold correctly**: treat 400 ms as the **ceiling for interactive response in a work tool**. Anything done more often than a few times per session must fit within it; everything else is governed by the table in file 01 §12.5.

---

## 11. Jakob's Law: "do it the way everyone else does"

**What the law says** [M8]: "Users spend most of their time on other sites. This means they prefer your site to work the same way as all the others they already know".

**How it gets distorted**:
1. **"Copy the market leader".** The law is about the **totality** of the user's experience, not about one competitor. A solution that works for the leader because of its scale, brand, or audience specifics doesn't transfer when copied.
2. **"Copy from another category".** Patterns from consumer social networks (infinite feed, swipes, emoji reactions) get carried over into a work tool, where expectations are different. NN/g explicitly warns: mental models are formed from experience with **similar** systems [M19].
3. **"So, never innovate".** NN/g's position is softer: **"Sometimes innovation is needed, but it's best to do it only when the new approach is clearly superior to the old, well-known one"** [M19].

**What the law actually offers, and this is rarely cited**: a migration technique. "When making changes, reduce dissonance by letting users keep using the familiar version for a while" — the 2017 YouTube redesign case: a preview of the new interface, feedback collection, and **the option to go back to the old version** [M8] `[opinion]`.

**What to do instead**:
- Compile a list of conventions for **your own category** (admin panel, e-commerce, banking) and deviate from them only with a proven gain.
- Check for inertia: if users come from a specific system (replacing 1C, replacing Jira), their expectations are set by that very system.
- Always provide a transition period and a rollback option when changing a familiar mechanic.

---

## 12. Mistakes in applying Fitts's Law

**What's in the law** [M8]: the time to reach a target is a function of the **distance** to it and its **size**; fast movements toward small targets produce more errors.

**Three typical mistakes**:
1. **"It's enough to make the button big".** Distance is no less important. Tognazzini: "not only reduce distances and increase sizes, but also **reduce the number of targets** that need to be acquired" (Multiple Fitts) [M11]. In practice: an action button next to the row is better than a big button in the header.
2. **Ignoring edges and corners.** Edges "pin" the pointer and effectively make the target infinite in one dimension; corners are the fastest-to-reach points on the screen. **"Even a one-pixel border can cause a 20–30 % slowdown for tools along the edge"** [M11] `[opinion]`. Hence: sticky panels sitting flush against the window edge are faster than panels with a margin; on the web this is bounded by the browser window, not the screen.
3. **Carrying "mouse" conclusions over to touch without adjustment.** The law works on touch devices too (Fitts originally studied physical controls), **but edge "pinning" disappears** if the screen isn't recessed [M11]. Specific minimum target sizes are in `08-accessibility/` (WCAG 2.2) and `../ui-research/03-spacing-sizing/`.

**The opposite mistake, which the law also describes**: "use small objects for functions you would prefer the user **not** to perform" [M11]. That is, it's legitimate to make a rare destructive action less accessible — but not invisible (file 01 §4.5, discoverability).

---

## 13. "Users tell you what they need"

**Statement of the myth**: if you ask users what to improve and do it, the product will get better.

**Data** `[research]`:
- **The aesthetic-usability effect distorts self-reports.** An NN/g case: a participant ran into problems ranging from minor to serious on the FitBit site and completed the task with difficulty, yet in the post-test questionnaire gave a **high ease-of-use rating**, commenting only on the colors and photos: "It's the colors they used. Looks like the ocean, it's calm. Very good photographs" [M20].
- Three causes of "false praise" according to NN/g: the pressure of "I have to say something"; the desire to be polite (especially if the participant thinks the moderator built the site); the aesthetic effect itself [M20].
- **Complaints point to the symptom, not the cause.** Porter: users complain about the number of clicks, "but these complaints aren't really about clicks — they're complaints about not finding what they were looking for" [M2].
- Tidwell: **"users won't always tell you about repetitive tasks and often aren't aware of them themselves"** — they have to be discovered through observation [M21].
- NN/g on analytics: high page traffic doesn't mean the page is needed — "people may land there by mistake; analytics should be complemented with observational testing" [M22].

**What to do instead**:
- Look at **behavior**, not words: think-aloud, in-context observation, logs.
- In surveys, separate rating the visuals from rating the task; NN/g suggests neutral wording: "Do you have any comments on how easy or difficult it was to find this information?", "What made it easy or difficult to read?", "What would you change?" [M20].
- Don't push: "too much pressure will cause participants to make up answers" [M20].
- Remember the flip side: **beautiful design masks minor problems, but not major ones** [M20].

---

## 14. "A modal window grabs attention, so it works"

**Data** [M23] `[research]`:
- "Users have already grown used to hastily closing modal overlays, assuming nothing good will come of them".
- **"Don't show critical information in a pop-up, since people tend to close them without reading. Instead, use a visually emphasized element right on the page, in a contextually appropriate place."**
- Explicitly prohibited: a pop-up **before the main content loads** (except legally required notices), a pop-up **right after login**, asking for an e-mail before interaction, asking for a rating before anything has been done, interrupting a critical task, several pop-ups in a row.
- For GDPR and cookies — a **non-modal** overlay at the bottom or on the side.
- Plus the habituation mechanism [M21]: "if dialogs pop up constantly on intentional changes, clicking OK becomes a habitual response, and then, when it really matters, the dialog slips beneath conscious awareness".

**What to do instead**: communicate what's important **in the flow** — next to the object it relates to, with sufficient visual weight, with the ability to return to the message. Reserve modality for (a) truly blocking decisions and (b) focusing on a subtask (file 01 §4.5 on overlays and §14.4).

---

## 15. "Every application needs a dashboard"

`[opinion]`, a conclusion drawn from the sources read; no direct research on this claim was found.

Arguments against a default dashboard:
- **Posture**: in a sovereign application, the main screen is a workplace, not a showcase of metrics; the user comes there to continue working, not to look around [M12].
- **Micro-breaks and resumption**: a "where I left off" list and unfinished tasks are more useful than aggregated charts [M21] (prospective memory, §6.10 of file 01).
- **Cost of attention**: a dashboard that doesn't lead to action is pure excise on the way to work [M12].