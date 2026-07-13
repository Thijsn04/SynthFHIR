# Command-line interface

Installing the package puts a `synthfhir` command on your path:

```bash
pip install -e .
synthfhir --help
```

Every subcommand has its own `--help`.

## `synthfhir generate`

Generate a cohort and write it to a file or standard output.

```bash
synthfhir generate --count 20 --condition diabetes --seed 42 -o cohort.json
synthfhir generate --count 100 --format ndjson -o cohort.ndjson
synthfhir generate --count 5 --version R5 --profile us-core
```

| Option | Default | Description |
|---|---|---|
| `--count` | 10 | Number of patients |
| `--version` | R4 | FHIR version (`R4` or `R5`) |
| `--age-min` | 0 | Minimum patient age |
| `--age-max` | 80 | Maximum patient age |
| `--condition` | none | Condition key or partial name |
| `--years` | 2 | Years of clinical history |
| `--practitioners` | 3 | Practitioner pool size |
| `--organizations` | 1 | Organization pool size |
| `--profile` | base | `base` or `us-core` |
| `--bundle-type` | collection | `collection` or `transaction` |
| `--format` | bundle | `bundle` or `ndjson` |
| `--seed` | none | Seed for reproducible output |
| `-o`, `--output` | `-` | Output file, or `-` for stdout |

## `synthfhir validate`

Validate a FHIR Bundle file, or read from stdin with `-`. Exit code is 0 when
the bundle is valid and 1 when it is not, which makes it convenient in CI.

```bash
synthfhir validate cohort.json
synthfhir generate --count 5 --seed 1 | synthfhir validate -
synthfhir validate cohort.json --json
```

## `synthfhir conditions`

List the condition catalog. Add `--json` for machine-readable output.

```bash
synthfhir conditions
synthfhir conditions --json
```

## `synthfhir observations`

List the observation catalog. Add `--json` for machine-readable output.

## `synthfhir serve`

Run the REST API with uvicorn.

```bash
synthfhir serve --host 0.0.0.0 --port 8000 --reload
```

| Option | Default | Description |
|---|---|---|
| `--host` | 127.0.0.1 | Bind host |
| `--port` | 8000 | Bind port |
| `--reload` | off | Auto-reload on code changes |

## Piping and composition

Because `generate` writes to stdout and `validate` reads from stdin, the two
compose cleanly:

```bash
synthfhir generate --count 50 --seed 3 | synthfhir validate -
```

Output is streamed, so `generate` interoperates with standard tools such as
`jq`:

```bash
synthfhir generate --count 3 --seed 1 | jq '.entry | length'
```
