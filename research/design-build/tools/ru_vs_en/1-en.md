## Digest for the agent

1. **Consistency is not sameness.** The goal: a person should not have to guess whether different words,
   situations, and actions mean the same thing. → §1 `[консенсус]`
2. **Two kinds: internal** (within a product and a product family) **and external** (conventions of the web,
   the platform, and the industry). Both are needed; in a conflict, the external one usually prevails. → §1.2
   `[консенсус]`
3. **The main mechanism is object representations.** One object looks the same in a list, card, search,
   select, notification, breadcrumb, and link. It is defined once in the object map and reused. → §2
   `[мнение]`
4. **The order of an object's first three attributes is not rearranged anywhere.** A violation is a
   shape-shifter. → §2.2 `[мнение]`
5. **Different object types are distinguishable “with an unfocused gaze”.** A violation is a masked object.
   → §2.3 `[мнение]`
6. **One primitive per need.** Two date pickers, two ways to choose from a list, two toasts — an inventory
   defect, not a stylistic one. → §3.1 `[консенсус]`
7. **One action — one name throughout the product**, including the past tense in the toast and in the log:
   button “Publish” → toast “Published”. → §3.2 `[система]`
8. **The same thing goes in the same place.** Button order, the position of the primary action, the location
   of filters, and the location of pagination are fixed once (WCAG 3.2.3 Consistent Navigation, 3.2.4
   Consistent Identification). → §3.3 `[консенсус]` + `[стандарт]`
9. **The same interactions and the same set of states** for a given component everywhere: if a row expands on
   one screen, it does not open a modal on another. → §3.4 `[консенсус]`
10. **A single glossary**: one word — one thing, one thing — one word. A symptom of neglect, measurable as a
    number: 14 different terms for the concept of “video” in a single project. → §3.5 `[практика]`
11. **Density is uniform within a zone, not across the product**: tables are dense, forms are medium, wizards
    are sparse — but the same on every screen. → §3.6 `[консенсус]`
12. **A single data format**: numbers, dates, money, long ID numbers, and empty values look the same
    everywhere. → §3.7 `[система]`
13. **Jakob's Law**: people spend most of their time on other sites and bring their expectations from there.
    Deviating from a convention adds cognitive load and requires justification. → §4 `[консенсус]`
14. **Named width ranges are a vocabulary of layout rearrangement rules, not a list of devices.** You need to
    test at arbitrary widths within a range. This resolves the contradiction between Frost and Material 3.
    → §4.3 `[спорно]`
15. **Deliberate difference is needed in four cases**: a destructive action, a critical warning, a mode
    change, a context change (organization, environment). Nowhere else. → §5 `[консенсус]`
16. **Difference is justified by the product's positioning, not by a desire to stand out.** → §5.3 `[мнение]`
17. **Repetition is complexity, not a safety net.** Duplicating a feature forces people to figure out whether
    it is new or old. → §6 `[исследование]`
18. **Only one kind of redundancy is good: alternative navigation paths** (cross-links), and their number is
    limited. → §6.2 `[исследование]`
19. **An interface inventory is an audit procedure**, not a document: collect all instances of each pattern,
    see the discrepancies, decide what to merge and what to kill. → §7 `[практика]`
20. **A vetted starter application (starter) is the main mechanism for consistency across generations**: the
    first screen and the first component set the palette, typography, buttons, and spacing for everything
    else. → §8.1 `[система]`
21. **The component inventory is compiled before generation**, not derived from it. → §8.2 `[практика]`
22. **Tokens are a contract, not styling**: arbitrary values are forbidden and checked by a linter. → §8.3
    `[система]`
23. **The grounding rule**: a component, prop, or token that cannot be confirmed by a source is not used.
    → §8.3 `[система]`
24. **The conformance check runs after the search for a solution, not instead of it.** Otherwise, the question
    “which solution is best” is replaced by the question “what can be assembled from what is available”.
    → §10.1 `[мнение]`
25. **Validity against the system ≠ quality**: a screen built entirely from system components can be a bad
    screen. → §10.1 `[практика]`
26. **Drift is measurable**: 17 different fonts on a single screen, four brand blues, six list styles — all of
    this is found by an audit and fixed by switching the library. → §11 `[данные]`
27. **Editing one screen breaks neighboring ones** (F8.4) — so visual regression is run across all routes
    after every edit. → §9 `[исследование]`
28. **The origin of a pattern (lineage)** must be known: what it contains and where it is included. Otherwise,
    after an edit, you don't know what to recheck. → §7.3 `[практика]`
29. **Consistency does not happen by itself**: even when a standard exists, people forget rarely used rules
    and interpret ambiguous ones differently. Regular reviews and a separate annual audit are needed. → §10
    `[мнение]`
30. **Habit is a working mechanism**: a suboptimal solution becomes “correct” if a person is accustomed to it.
    This is an argument against cosmetic rearrangements in a mature product. → §5.4 `[мнение]`

---