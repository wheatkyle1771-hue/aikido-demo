# Demo app

Small Flask app with intentional issues across every category Aikido
scans - SAST, SCA, secrets, container, IaC - so the trial account has
something real to show instead of an empty findings list.

Don't deploy this anywhere. Repo and image scanning both work on source
and image content, they don't need the app actually running. Push it to
GitHub, optionally build and push the image, and stop there.

## What's here

- `requirements.txt` - old Flask, PyYAML, Pillow, and requests, all with
  real CVEs. PyYAML's is actually triggered by `/config` below, so it
  should come back as a critical, reachable finding. Pillow's just sits in
  the manifest unused - same category, opposite result, on purpose.

- `main.py` - a fake AWS key pair and a hardcoded DB connection string.
  The AWS key isn't AWS's own docs placeholder (`AKIAIOSFODNN7EXAMPLE`) -
  most scanners already know that one and ignore it. Also four routes
  with real bugs:
  - `/users` - SQL injection
  - `/ping` - command injection
  - `/config` - unsafe `yaml.load()`, which is what makes the PyYAML CVE
    above actually reachable instead of just sitting in a manifest
  - `/fetch` - SSRF, fetches whatever URL you give it. Worth mentioning
    next to the cloud folders - this is the classic way an app bug turns
    into stolen cloud credentials via the metadata endpoint.

  All four are hit directly from a route, so they should come back as
  reachable/exploitable rather than theoretical.

- `legacy_unused.py` - dead code. One function per route above (SQL
  injection, command injection, insecure deserialization, SSRF), same
  bugs, just nothing calls any of them. Four matched reachable/unreachable
  pairs, same CWEs - the cleanest possible example if reachability
  analysis comes up.

- `Dockerfile` - `python:3.8-slim` (past EOL), no `USER`, runs as root.

- `infra/main.tf` - Terraform, not meant to be applied. A public
  read+write S3 bucket, a wide-open security group, and an RDS instance
  that's public, unencrypted, and has a hardcoded password all at once.

## If everything comes back low

It usually means the finding is present but not reachable or exposed - a
CVE sitting in a manifest nothing calls, or a secret pattern the scanner
already recognizes as a placeholder. That's basically the whole point of
this repo: PyYAML's CVE went from manifest-only to reachable via
`/config`, the AWS key stopped being AWS's own example, the S3 bucket got
write access added, the RDS instance stacks three problems at once.
Pillow's left alone on purpose as the case that should stay low.

## Notes

- Every secret in here (the AWS key, the DB URL, the RDS password) is
  fake and doesn't point at anything real. Don't swap in real values.
- `/ping`, `/users`, `/config`, and `/fetch` are real, working bugs. Don't
  deploy this app anywhere reachable, especially not `/fetch`.
- Don't run `terraform apply` on `infra/main.tf` - the RDS instance would
  be real, billable, and public. Use `../cloud/aws` if you want a live
  cloud finding instead.
