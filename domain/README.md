# Domain issues

This one's not a script - domain/attack-surface scanning needs a real
domain pointed at something, so it's a checklist instead. Pointed at the
Lambda Function URL from `../cloud/aws`.

AWS doesn't have a one-command domain mapping like some platforms do, so
this takes a few more steps: put CloudFront in front of the Function URL,
then point DNS at CloudFront.

## What you need

A domain you control. If you don't have one, a cheap throwaway (a few
bucks for a .com or .xyz) is enough. Don't use your actual personal or
work domain for this.

## 1. Get a certificate (has to be in us-east-1 for CloudFront)

```
aws acm request-certificate \
  --domain-name app.yourdomain.com \
  --validation-method DNS \
  --region us-east-1
```

That gives you back a certificate ARN and a CNAME record to add at your
registrar for validation. Add it, then check status until it flips to
issued:

```
aws acm describe-certificate --certificate-arn <arn-from-above> \
  --region us-east-1 --query 'Certificate.Status'
```

Usually takes a few minutes.

## 2. Put CloudFront in front of the Function URL

Grab your Function URL's hostname - the part after `https://`, no
trailing slash, something like `abc123xyz.lambda-url.us-east-1.on.aws`.

```
aws cloudfront create-distribution --distribution-config '{
  "CallerReference": "aikido-demo-'"$(date +%s)"'",
  "Comment": "aikido demo domain",
  "Enabled": true,
  "Aliases": {"Quantity": 1, "Items": ["app.yourdomain.com"]},
  "ViewerCertificate": {
    "ACMCertificateArn": "<cert-arn-from-step-1>",
    "SSLSupportMethod": "sni-only",
    "MinimumProtocolVersion": "TLSv1.2_2021"
  },
  "Origins": {
    "Quantity": 1,
    "Items": [{
      "Id": "lambda-url-origin",
      "DomainName": "<your-function-url-hostname>",
      "CustomOriginConfig": {
        "HTTPPort": 80,
        "HTTPSPort": 443,
        "OriginProtocolPolicy": "https-only"
      }
    }]
  },
  "DefaultCacheBehavior": {
    "TargetOriginId": "lambda-url-origin",
    "ViewerProtocolPolicy": "redirect-to-https",
    "CachePolicyId": "4135ea2d-6df8-44a3-9df3-4b5a84be39ad"
  }
}'
```

(That `CachePolicyId` is AWS's managed "CachingDisabled" policy - you
don't want CloudFront caching responses from a demo app.)

The response includes a `DomainName` like `d123abc456.cloudfront.net`.
Point your domain at that:

```
CNAME   app.yourdomain.com   d123abc456.cloudfront.net
```

CloudFront takes 15-30 minutes to finish deploying (status goes from
`InProgress` to `Deployed`). Once that's done and DNS resolves,
`app.yourdomain.com` serves the same Lambda function as the raw Function
URL.

The handler in `lambda_function.py` doesn't set any security headers, so
this alone should get you: missing HSTS, missing CSP, missing
X-Content-Type-Options, missing X-Frame-Options.

## 3. Skip the email auth records, or make them worse than missing

Don't add SPF/DKIM/DMARC TXT records for the domain - most scanners flag
a domain with none of those as a spoofing risk on its own. If you want it
to read as a deliberate misconfig rather than "just never set up," use an
overly permissive SPF record instead:

```
TXT   yourdomain.com   "v=spf1 +all"
```

`+all` means anyone can send mail as your domain - a real problem, not
just an absence of one.

## 4. Dangling subdomain / takeover (optional, and riskier)

Point a subdomain at a cloud resource that doesn't exist yet - a CNAME to
an S3 bucket name or GitHub Pages site nobody's claimed. That's a
textbook subdomain takeover: whoever claims that resource first can serve
whatever they want under your domain. Real finding, good story, but also
a live weakness for as long as it's up. If you do this, use a random
subdomain name and pull the DNS record the moment the demo's over.

## Not worth doing

TLS/cipher-strength findings are hard to fake here too - CloudFront
terminates TLS with a modern config you don't get to weaken. Not worth
extra infrastructure for one finding.

## Cleanup

CloudFront distributions have to be disabled before they can be deleted,
so it's a two-step teardown:

```
aws cloudfront get-distribution-config --id <dist-id>
# take the ETag and config from that output, set "Enabled": false in the
# config, save it as disabled-config.json, then:
aws cloudfront update-distribution --id <dist-id> \
  --if-match <etag> --distribution-config file://disabled-config.json
# wait for it to finish redeploying as disabled (status: Deployed), then:
aws cloudfront delete-distribution --id <dist-id> --if-match <new-etag>
aws acm delete-certificate --certificate-arn <cert-arn> --region us-east-1
```

Also remove whatever DNS records you added, especially the dangling one
from #4 if you did it. If you bought the domain just for this, let it
lapse or keep it if you'll reuse it.
