# Security Policy

## Scope

SynthFHIR generates synthetic data locally. It has no user accounts, stores no
data, and by default makes no outbound network connections. The data it produces
is fabricated and contains no real personal information.

## Reporting a vulnerability

If you find a security issue, please report it privately rather than opening a
public issue. Use GitHub's private vulnerability reporting on the repository, or
contact the maintainer listed in the repository metadata.

Please include:

- A description of the issue and its impact
- Steps to reproduce
- Any relevant version or environment details

We will acknowledge your report, investigate, and keep you informed of progress.
Please give us a reasonable time to address the issue before any public
disclosure.

## Deployment considerations

- CORS is open by default because the tool is intended for local and internal
  use. Restrict `allow_origins` in `main.py` if you expose it more widely.
- There is no authentication. If you place the service on a shared network,
  gate it at a reverse proxy.
- The service is stateless and returns only synthetic data, so it does not
  process or expose sensitive information.

## Supported versions

Security fixes target the latest released version on the `main` branch.
