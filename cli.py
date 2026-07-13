"""SynthFHIR command-line interface.

Examples:
    synthfhir generate --count 20 --condition diabetes --seed 42 -o cohort.json
    synthfhir generate --count 100 --format ndjson -o cohort.ndjson
    synthfhir validate cohort.json
    synthfhir conditions
    synthfhir serve --port 8000

Run `synthfhir <command> --help` for the options of each command.
"""
from __future__ import annotations

import argparse
import json
import sys

import synthfhir


def _add_generate_args(p: argparse.ArgumentParser) -> None:
    p.add_argument("--count", type=int, default=10, help="Number of patients (default 10)")
    p.add_argument("--version", choices=["R4", "R5"], default="R4", help="FHIR version")
    p.add_argument("--age-min", type=int, default=0, help="Minimum patient age")
    p.add_argument("--age-max", type=int, default=80, help="Maximum patient age")
    p.add_argument("--condition", default=None, help="Condition key or partial name")
    p.add_argument("--years", type=int, default=2, help="Years of clinical history")
    p.add_argument("--practitioners", type=int, default=3, help="Practitioner pool size")
    p.add_argument("--organizations", type=int, default=1, help="Organization pool size")
    p.add_argument("--profile", choices=["base", "us-core"], default="base", help="Profile set")
    p.add_argument(
        "--bundle-type", choices=["collection", "transaction"], default="collection",
        help="Bundle type (ignored for ndjson)",
    )
    p.add_argument("--format", choices=["bundle", "ndjson"], default="bundle", help="Output format")
    p.add_argument("--seed", type=int, default=None, help="Seed for reproducible output")
    p.add_argument(
        "-o", "--output", default="-",
        help="Output file, or '-' for stdout (default)",
    )


def _cmd_generate(args: argparse.Namespace) -> int:
    if args.format == "ndjson":
        text = synthfhir.generate_cohort_ndjson(
            count=args.count,
            version=args.version,
            age_min=args.age_min,
            age_max=args.age_max,
            condition=args.condition,
            years=args.years,
            num_practitioners=args.practitioners,
            num_organizations=args.organizations,
            profile=args.profile,
            seed=args.seed,
        )
    else:
        bundle = synthfhir.generate_cohort_bundle(
            count=args.count,
            version=args.version,
            age_min=args.age_min,
            age_max=args.age_max,
            condition=args.condition,
            years=args.years,
            num_practitioners=args.practitioners,
            num_organizations=args.organizations,
            profile=args.profile,
            bundle_type=args.bundle_type,
            seed=args.seed,
        )
        text = json.dumps(bundle, indent=2)

    _write(text, args.output)
    return 0


def _cmd_validate(args: argparse.Namespace) -> int:
    raw = sys.stdin.read() if args.file == "-" else open(args.file, encoding="utf-8").read()
    try:
        bundle = json.loads(raw)
    except json.JSONDecodeError as exc:
        print(f"error: input is not valid JSON: {exc}", file=sys.stderr)
        return 2

    report = synthfhir.validate_bundle(bundle)
    if args.json:
        print(json.dumps(report.to_dict(), indent=2))
    else:
        status = "VALID" if report.valid else "INVALID"
        print(f"{status}: {report.resource_count} resources, "
              f"{len(report.errors)} errors, {len(report.warnings)} warnings")
        for issue in report.errors + report.warnings:
            print(f"  [{issue.severity}] {issue.path}: {issue.message}")
    return 0 if report.valid else 1


def _cmd_conditions(args: argparse.Namespace) -> int:
    rows = [
        {
            "key": c.key,
            "display": c.display,
            "snomed_code": c.snomed_code,
            "icd10_code": c.icd10_code,
            "typical_age_min": c.typical_age_min,
        }
        for c in synthfhir.CONDITIONS
    ]
    if args.json:
        print(json.dumps(rows, indent=2))
    else:
        for r in rows:
            print(f"{r['key']:26} {r['display']}")
    return 0


def _cmd_observations(args: argparse.Namespace) -> int:
    rows = [
        {"key": o.key, "loinc_code": o.loinc_code, "display": o.display, "unit": o.unit}
        for o in synthfhir.OBSERVATIONS.values()
    ]
    if args.json:
        print(json.dumps(rows, indent=2))
    else:
        for r in rows:
            print(f"{r['key']:20} {r['loinc_code']:12} {r['display']}")
    return 0


def _cmd_serve(args: argparse.Namespace) -> int:
    try:
        import uvicorn
    except ImportError:
        print("error: uvicorn is not installed. Install with: pip install 'synthfhir[serve]'",
              file=sys.stderr)
        return 2
    uvicorn.run("main:app", host=args.host, port=args.port, reload=args.reload)
    return 0


def _write(text: str, output: str) -> None:
    if output == "-":
        sys.stdout.write(text)
        if not text.endswith("\n"):
            sys.stdout.write("\n")
    else:
        with open(output, "w", encoding="utf-8") as fh:
            fh.write(text)
        print(f"wrote {output}", file=sys.stderr)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="synthfhir", description=__doc__.split("\n")[0])
    parser.add_argument("--version", action="version", version=f"synthfhir {synthfhir.__version__}")
    sub = parser.add_subparsers(dest="command", required=True)

    gen = sub.add_parser("generate", help="Generate a synthetic cohort")
    _add_generate_args(gen)
    gen.set_defaults(func=_cmd_generate)

    val = sub.add_parser("validate", help="Validate a FHIR Bundle file")
    val.add_argument("file", help="Bundle JSON file, or '-' for stdin")
    val.add_argument("--json", action="store_true", help="Emit the report as JSON")
    val.set_defaults(func=_cmd_validate)

    cond = sub.add_parser("conditions", help="List the condition catalog")
    cond.add_argument("--json", action="store_true", help="Emit as JSON")
    cond.set_defaults(func=_cmd_conditions)

    obs = sub.add_parser("observations", help="List the observation catalog")
    obs.add_argument("--json", action="store_true", help="Emit as JSON")
    obs.set_defaults(func=_cmd_observations)

    serve = sub.add_parser("serve", help="Run the REST API with uvicorn")
    serve.add_argument("--host", default="127.0.0.1", help="Bind host")
    serve.add_argument("--port", type=int, default=8000, help="Bind port")
    serve.add_argument("--reload", action="store_true", help="Auto-reload on code changes")
    serve.set_defaults(func=_cmd_serve)

    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        return args.func(args)
    except BrokenPipeError:
        # A downstream reader (for example `head`) closed the pipe early.
        try:
            sys.stdout.close()
        except OSError:
            pass
        return 0
    except KeyboardInterrupt:
        return 130


if __name__ == "__main__":
    raise SystemExit(main())
