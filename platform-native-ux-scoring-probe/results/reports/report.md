# Platform-Native UX Probe Report

Generated at: 2025-11-20T01:36:36.814Z
Default base URL: https://ajfisher.me/

## Score meanings & weights
- **Routing** (25%): Prefers document navigations and semantic click targets; penalises heavy client-router hints.
- **Forms** (25%): Presence of native forms and constrained controls; penalises faux click targets acting as controls. If no forms are found, this score is omitted and the remaining weights are renormalised.
- **Data fetching** (20%): Rewards cached or server-driven flows; penalises duplicate or uncached XHR/fetch calls.
- **Progressive enhancement** (20%): Ratio of steps succeeding with JavaScript disabled.
- **Semantics & a11y** (10%): Semantic landmarks and labelled controls; penalises role misuse and non-semantic clickables.

The **Platform-native total** is a weighted average of available categories; unavailable scores (e.g., no forms detected) are dropped and remaining weights are reapplied.

## Flow summary
| Flow | Base URL | Routing | Forms | Data fetching | PE (no-JS) | Semantics/a11y | Platform-native total |
| --- | --- | --- | --- | --- | --- | --- | --- |
| ajfisher-strategy-article | https://ajfisher.me/ | 100 | — | 100 | 100 | 30 | **91** |
| amazon-search-results | https://www.amazon.com/ | 100 | 40 | 80 | 50 | 0 | **61** |
| wikipedia-browser-topic | https://en.wikipedia.org/ | 100 | 40 | 80 | 100 | 54 | **76** |
| mozilla-firefox-download | https://www.mozilla.org/ | 100 | 50 | 80 | 100 | 56 | **79** |

## Flow details
### ajfisher-strategy-article
Base URL: https://ajfisher.me/ · No-JS replay enabled
Homepage to strategy tag to AI strategy article

Scores:
- Routing: 100, Forms: —, Data fetching: 100, PE: 100, Semantics & a11y: 30, **Platform-native total: 91**

Step metrics:
- Step 1 (goto): URL https://ajfisher.me/; anchors 56; forms 0; controls 1 (labelled 0); non-semantic clickables 0; semantic containers 10; network events 13
- Step 2 (goto): URL https://ajfisher.me/tagged/strategy/; anchors 50; forms 0; controls 1 (labelled 0); non-semantic clickables 0; semantic containers 10; network events 12
- Step 3 (goto): URL https://ajfisher.me/2025/11/05/strategy-ai/; anchors 47; forms 0; controls 1 (labelled 0); non-semantic clickables 0; semantic containers 11; network events 15

### amazon-search-results
Base URL: https://www.amazon.com/ · No-JS replay enabled
Home to a wireless mouse search results page

Scores:
- Routing: 100, Forms: 40, Data fetching: 80, PE: 50, Semantics & a11y: 0, **Platform-native total: 61**

Step metrics:
- Step 1 (goto): URL https://www.amazon.com/; anchors 2; forms 1; controls 4 (labelled 0); non-semantic clickables 0; semantic containers 0; network events 8
- Step 2 (goto): URL https://www.amazon.com/s?k=wireless+mouse; anchors 3; forms 1; controls 3 (labelled 0); non-semantic clickables 0; semantic containers 0; network events 4

### wikipedia-browser-topic
Base URL: https://en.wikipedia.org/ · No-JS replay enabled
Main page to browser-related article and accessibility topic

Scores:
- Routing: 100, Forms: 40, Data fetching: 80, PE: 100, Semantics & a11y: 54, **Platform-native total: 76**

Step metrics:
- Step 1 (goto): URL https://en.wikipedia.org/wiki/Main_Page; anchors 639; forms 2; controls 20 (labelled 7); non-semantic clickables 0; semantic containers 13; network events 33
- Step 2 (goto): URL https://en.wikipedia.org/wiki/Web_browser; anchors 1145; forms 5; controls 47 (labelled 17); non-semantic clickables 0; semantic containers 16; network events 48
- Step 3 (goto): URL https://en.wikipedia.org/wiki/Web_accessibility; anchors 867; forms 2; controls 28 (labelled 9); non-semantic clickables 0; semantic containers 16; network events 24

### mozilla-firefox-download
Base URL: https://www.mozilla.org/ · No-JS replay enabled
Mozilla landing page to Firefox download

Scores:
- Routing: 100, Forms: 50, Data fetching: 80, PE: 100, Semantics & a11y: 56, **Platform-native total: 79**

Step metrics:
- Step 1 (goto): URL https://www.mozilla.org/en-US/; anchors 79; forms 2; controls 14 (labelled 6); non-semantic clickables 0; semantic containers 32; network events 48
- Step 2 (goto): URL https://www.firefox.com/en-US/?redirect_source=mozilla-org; anchors 96; forms 1; controls 10 (labelled 3); non-semantic clickables 0; semantic containers 14; network events 41
