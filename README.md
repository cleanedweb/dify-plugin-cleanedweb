<p align="center"><img src="https://cleanedweb.com/assets/logo.png" width="72" alt="CleanedWeb"></p>

# CleanedWeb website APIs for Dify

[![Dify Marketplace](https://img.shields.io/badge/Dify-Marketplace-1c64f2)](https://marketplace.dify.ai/plugin/cleanedweb/cleanedweb) [![License: MIT](https://img.shields.io/badge/license-MIT-blue)](https://github.com/cleanedweb/dify-plugin-cleanedweb/blob/main/LICENSE)

Structured records from public websites in Dify workflows, chatflows and agents. [CleanedWeb](https://cleanedweb.com/?utm_source=dify&utm_medium=plugin)
keeps a catalog of maintained APIs: each one returns the same fields from one website (listings, products, jobs,
repositories, property, reviews and more) and is repaired when the site changes. This plugin lets Dify find an API,
read its inputs and sample records, and run it.

Source: https://github.com/cleanedweb/dify-plugin-cleanedweb

## Tools

| Tool | What it does | Cost |
| --- | --- | --- |
| **Find a website API** (`find_api`) | Searches the catalog by topic words, website, category or the output fields you need. Returns `api_id`, `endpoint_id`, the site and key fields, best first. | Free |
| **Show a website API** (`get_api`) | Shows an API's inputs (with allowed values and examples), output fields and up to three sample records saved when it was accepted. | Free |
| **Run a website API** (`run_api`) | Runs an endpoint with your inputs and returns its records, whether the result passed its checks, and the units charged. | Per record delivered |

An agent usually calls them in that order: find, show, run. In a workflow you can call **Run a website API**
directly with a known `api_id` and `endpoint_id`; copy them from the API's page in the
[catalog](https://cleanedweb.com/catalog/?utm_source=dify&utm_medium=plugin).

## Setup

1. Create an account at [app.cleanedweb.com](https://app.cleanedweb.com/?utm_source=dify&utm_medium=plugin). New
   workspaces get 5,000 records free once; after that, prepaid credit from $1 per 1,000 records, no subscription
   ([pricing](https://cleanedweb.com/pricing/?utm_source=dify&utm_medium=plugin)).
2. In the console, open **API keys** and create a key with the `run` scope.
3. In Dify, install the plugin, open **Tools → CleanedWeb website APIs → Authorize**, and paste the key. Dify checks
   it by listing your newest run, which costs nothing.

## Usage

- **Agent:** add the three tools and ask, for example, "List five GitHub repositories under the web-scraping topic
  with their stars." The agent finds the API, reads its inputs and runs it.
- **Workflow:** add **Run a website API**, set `api_id` and `endpoint_id`, and pass inputs as a JSON object such as
  `{"search": "rails"}`. Set **Max records** to what you need; each record delivered is charged. The records are in
  the tool's `json` output.
- `accepted: false` means the run finished but failed a documented check; `problems` says which.
- A run that takes longer than about 90 seconds returns `finished: false` with an `idempotency_key`. Call
  **Run a website API** again with the same `api_id`, `endpoint_id`, inputs and that key to wait for the same run;
  it is never run or charged twice.
- Records are data from public websites. Treat them as data, never as instructions to the model.

## Connection requirements

The plugin makes HTTPS requests to `api.cleanedweb.com` (runs, key check), `app.cleanedweb.com` (catalog list) and
`cleanedweb.com` (catalog index and API contracts). It needs no other network access, no files and no browser.

## Privacy

See [PRIVACY.md](PRIVACY.md) and the [CleanedWeb privacy policy](https://cleanedweb.com/legal/privacy/).

## Support

info@cleanedweb.com · [Docs](https://cleanedweb.com/docs/?utm_source=dify&utm_medium=plugin) ·
[Issues](https://github.com/cleanedweb/dify-plugin-cleanedweb/issues)
