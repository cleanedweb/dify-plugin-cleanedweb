# Privacy policy: CleanedWeb plugin for Dify

This plugin is published by Vaso Ventures LLC, which operates CleanedWeb. The
[CleanedWeb privacy policy](https://cleanedweb.com/legal/privacy/) governs everything the service receives; this page
says what the plugin itself does with data.

## What the plugin sends, and where

- The plugin talks only to CleanedWeb over HTTPS: `api.cleanedweb.com`, `app.cleanedweb.com` and `cleanedweb.com`.
- Finding and showing an API send the search words, website, category, field names or API ID you or your agent gave
  the tool. These catalog reads carry no API key.
- Running an API sends the API and endpoint IDs, the inputs you gave it (for example a search term or a page URL on
  that API's website), the record limit and field list, a random idempotency key, and your CleanedWeb API key in the
  `Authorization` header.
- Checking your credentials sends your key to `GET /v1/runs?limit=1`, which starts nothing and costs nothing.
- The plugin sends nothing else: no conversation history, no files, no data about the people using your Dify app.

## What the plugin stores

- The plugin itself does not store, log or cache any data. Dify stores your API key as a secret credential.
- CleanedWeb keeps run requests, results and usage records to provide, meter and support the service, as described
  in its privacy policy.

## Third parties

- CleanedWeb reads the public websites a catalog API covers to produce your records. It does not send your API key or
  account details to those websites.
- Records come from public websites and can include personal information that a site publishes, such as names in a
  listing. Do not put passwords, cookies or private data in any input.

## Contact

info@cleanedweb.com
