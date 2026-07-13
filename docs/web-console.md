# Web console

The web console is a single-page application served by the API at
`http://localhost:8000/`. It has no build step and no external dependencies. It
talks to the same-origin REST API.

## Opening it

Start the server and open the root URL:

```bash
uvicorn main:app --reload
# then visit http://localhost:8000/
```

The status pill in the header shows whether the API is reachable and its
response time.

## Configuring a dataset

The Configuration panel groups the options:

- Dataset: number of patients and FHIR version (R4 or R5).
- Demographics: minimum and maximum age.
- Clinical: a condition focus (every patient receives it plus plausible
  comorbidities) and the years of clinical history.
- Care network: the number of practitioners and organizations shared across the
  cohort.
- Output: bundle or NDJSON, collection or transaction bundle, and the base or
  US Core profile.
- Seed: optional, for reproducible output.

Select Generate to run the request.

## Reading the result

The result panel has three tabs:

- Summary: the total resource count and a breakdown per resource type, with a
  proportional bar for each type.
- Preview: the full response, pretty-printed and syntax highlighted. Very large
  responses are shown without highlighting to stay responsive.
- Resources: each resource as a collapsible entry you can expand to inspect.

The toolbar reports the HTTP status, the round-trip time, the response size, and
the resource count. Use Copy to put the response on the clipboard, or Download
to save it as `synthfhir-cohort.json` or `synthfhir-cohort.ndjson`.

## Theme

The console follows your system light or dark preference and has a manual toggle
in the header. Your choice is remembered in the browser.

## Using a different API origin

If you open the page from a different origin than the API, expand Advanced and
set the API base URL. Leave it empty to use the page's own origin.

## Accessibility

The console uses semantic HTML with labelled controls, visible focus states, and
keyboard-operable tabs and toggles. It works without a pointer.
