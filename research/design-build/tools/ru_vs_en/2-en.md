## Digest for the agent

1. **One typeface for the entire app plus one monospace.** A second text typeface in an app is a marker of
   marketing. Apple: “Minimize the number of typefaces you use… Mixing too many different typefaces can
   obscure your information hierarchy” `[S4]`; Untitled UI: “limit your designs to using just one
   typeface… If you absolutely need to, use a maximum of two” `[S32]`. → §6 `[консенсус]`
2. **If the product is in Russian, choose a font by the quality of its Cyrillic, not by popularity.**
   Experts at type.today explicitly do not recommend the Cyrillic of Inter, Roboto, Manrope, Fira Sans,
   Source Sans 3, Open Sans (bold weights), Overpass, Oswald, Arimo and Alumni Sans `[S13]`, `[S14]`.
   → §3 `[исследование]`
3. **Safe choices for Russian: Golos Text, IBM Plex Sans, PT Sans, Commissioner.** Experts rated the Cyrillic
   of all four as suitable `[S13]`, `[S14]`; all are licensed under the OFL. → §3.3
4. **No Cyrillic at all** (verified against Google Fonts metadata `[S20]`): Poppins, Public Sans, Lato,
   DM Sans, Space Grotesk, Outfit, Sora, Figtree, Instrument Sans, Albert Sans, Schibsted Grotesk, Gabarito,
   Bricolage Grotesque. Plus Jakarta Sans and Hanken Grotesk have only `cyrillic-ext` without the base
   `cyrillic` — they are unsuitable for Russian. → §3.4 `[система]`
5. **UI suitability criteria, in descending order of importance**: x-height ≥ 0.52 em, distinguishable `Il1`
   and `0O`, availability of weights 400/500/600, tabular figures or the `tnum` feature, Cyrillic support,
   variable format, OFL license. → §2
6. **Check `tnum` before you put a font into tables.** Commissioner and Wix Madefor Text have proportional
   figures and no `tnum` feature — numbers in a column will jump around `[S24]`. → §2.4 `[исследование]`
7. **The system font stack is the free and instant option**, chosen by Radix Themes, Ant Design, Mantine and
   Tailwind v4 `[S18]`, `[S35]`, `[S37]`, `[S9]`. The downside: the interface looks different on Windows,
   macOS and Android, and the vertical metrics vary. → §4 `[система]`
8. **Load the web font with `font-display: swap` and a metric-adjusted fallback** (`size-adjust`,
   `ascent-override`, `descent-override`, `line-gap-override`), otherwise you'll get a layout shift when the
   font is swapped `[S25]`. → §5.2 `[консенсус]`
9. **Subset Cyrillic with a separate `unicode-range`**: Latin and Cyrillic in one file double the file size.
   → §5.3 `[консенсус]`
10. **A variable font pays off starting at three weights.** A single InterVariable file replaces 3–5 static
    ones; plus you get access to intermediate weights, which Polaris takes advantage of (450/550/650) `[S6]`.
    → §2.6 `[система]`
11. **Set the monospace font 1–2 px smaller than the body text** on the same line: Radix sets
    `--code-font-size-adjust: 0.95` `[S18]`, Atlassian — inline code ≈ 12.25 px in a 14 px container `[S10]`.
    → §7 `[консенсус]`
12. **Turn off ligatures in the monospace font for code and identifiers.** Geist Mono 1.7.0 deliberately
    moved programming ligatures from `calt` to `ss11` because they broke monospacing `[S19]`. → §7.2 `[система]`
13. **Serif in the interface — only for an “editorial” mode**: article body, notes, long-form reading.
    Butterick: “on today's screens, serif fonts look equally good” — the argument “on screen, sans-serif
    only” is outdated `[S26]`. → §6.3 `[мнение]`
14. **Don't pick a font in weights 100–300 for the interface.** Apple: “avoid Ultralight, Thin, and Light
    font weights, which can be difficult to see, especially when text is small” `[S4]`. → §2.5 `[консенсус]`
15. **Test the font on the string `Шхуна «Ёж» ждёт: 0O Il1 — №5 ₽1 234,56`** — it exposes Cyrillic, ё,
    guillemets, glyph distinguishability, the dash, the numero sign, the ruble sign and digit group
    separators. → §3.5
16. **The words Caption, Text, Subhead, Display in a typeface name denote the recommended point size, not decoration.**
    “Display is a shop window, not a monitor” (Alexandra Korolkova, ParaType) `[V15]`. → §8.1 `[мнение]`
17. **A condensed font saves about 6 % of text capacity, no more** (Korolkova's experiment `[V15]`): a
    typeface's width affects the mood of a layout more than its capacity. → §8.1 `[исследование]`
18. **The number of styles is an indirect indicator of typeface quality**: 8 styles per Schoger `[V02]`,
    5+ weights per Refactoring UI `[S40]` and Untitled UI `[S32]`. → §8.2 `[консенсус]`

---