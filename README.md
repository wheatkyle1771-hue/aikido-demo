# Aikido demo kit

Stuff to connect to Aikido before the interview demo, so the trial account
actually has findings in it instead of a blank dashboard.

## Layout

- `app/` - a small vulnerable Flask app. Push it to a repo (fork or new)
  and connect that repo to Aikido. Covers SAST, SCA, secrets, IaC, and
  container scanning.
- `cloud/aws/` - deploys the app to Lambda plus a handful of other
  misconfigured resources (an admin IAM user, a public S3 bucket, an open
  security group, a couple of plaintext secrets) - five findings from
  `deploy.sh`. `ec2-deploy.sh` in the same folder adds a VM with its own
  set (admin instance profile, IMDSv1, open SSH, unencrypted volume,
  secret in user data) - separate script, run independently.
- `domain/` - checklist for getting domain/DNS findings (missing security
  headers, no SPF/DMARC, optionally a dangling subdomain), pointed at the
  Lambda Function URL. Needs a real domain, so it's not a script - see
  `domain/README.md`.

`app/` is worth doing regardless, since it's what covers the repo/image
side. `domain/` is optional and only worth the setup time if you actually
have a spare domain handy.

## Setup

1. Push `app/` to a new GitHub repo (or fork one) and connect it in Aikido
   as a code source.
2. Build and push the image somewhere Aikido can see it. Docker Hub is
   easiest since it doesn't need a cloud account:
   ```
   cd app
   docker build -t <your-dockerhub-username>/aikido-demo-app:latest .
   docker push <your-dockerhub-username>/aikido-demo-app:latest
   ```
3. Follow `cloud/aws/README.md` and connect the AWS account.
4. Give Aikido a few minutes to run its scans before you go live.

## Cheat sheet

- Repo -> SAST (SQL injection, command injection, insecure
  deserialization, and SSRF in `main.py` - all four reachable; the same
  four bugs again in `legacy_unused.py`, all unreachable), SCA (old
  Flask/PyYAML/Pillow/requests), secrets (fake AWS key pair + a hardcoded
  DB connection string), IaC (`infra/main.tf`: public S3, open security
  group, exposed RDS instance).
- Image -> container scan (old base image, runs as root).
- Cloud -> five AWS CSPM findings from `deploy.sh`, five more from
  `ec2-deploy.sh` - see `cloud/aws/README.md`.
- Domain (optional) -> missing security headers, missing/bad email auth
  records, maybe a dangling subdomain - see `domain/README.md`.

Two things worth pointing at directly if reachability comes up, since it's
Aikido's main pitch:

- `main.py` has four reachable bugs (`/users`, `/ping`, `/config`,
  `/fetch`), and `legacy_unused.py` has the exact same four, just dead -
  nothing calls them. Same CWEs, four times over, reachable vs. not.
- PyYAML's CVE is pinned in `requirements.txt` either way, but it's only
  actually reachable because `/config` calls `yaml.load()` on it. Pillow's
  CVE just sits there unused and should stay low - that contrast is on
  purpose.

If something still comes back lower than you'd expect, it's usually
because the scanner recognizes a known-placeholder pattern (that's what
happened with AWS's own example key) or the code path genuinely isn't
reachable. More detail on each finding in `app/README.md`.

## Before you connect anything real

- Use sandbox accounts for anything cloud-related, not ones with real
  stuff in them.
- Don't deploy `app/` anywhere - it's meant to be scanned from source, not
  hit over the network.
- Run `cloud/aws/cleanup.sh` (and `ec2-cleanup.sh` if you ran the EC2
  script) once the interview's done.
# aikido-demo
