# Indistinguishability service

After installing the requirements, run with:
```bash
$ flask --app indie_service --port {NUM}
```

This service supports the following endpoint that, upon receiving a valid JWT via POST, returns a salt.
The JWT is assumed to signed by this [OIDC provider](https://github.com/crocs-muni/indie-oidc-provider).

## `/get-salt`

The simplest, software-only, example of salt derivation as a SHA256 hash.

## `/get-salt-e2e`

Similarly to `/get-salt`, but the request is end-to-end encrypted using Noise channel.

## `/get-salt-jcardsim`

Similarly to `/get-salt`, but the salt is derived inside a simulated JavaCard.
