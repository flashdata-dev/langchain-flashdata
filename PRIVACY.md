# Data handling

The native tools send their validated query or video ID, selected parameters,
and an `X-API-Key` header directly to `https://data.flashdata.dev/v1/queries/realtime`.
They use a random request ID and a package version user agent. No other service
is contacted by this package's HTTP client, and it does not write query results
or credentials to disk.

FlashData handles requests according to its [privacy policy](https://flashdata.dev/legal/privacy).
Queries consume credits according to your account and the current pricing.

If you use the agent example, your question and tool results are also sent to
your configured model provider. LangChain tracing, callbacks, or application
logging can retain inputs/results if you enable them. Configure those services
according to your own data requirements. Credentials are excluded from tool
argument schemas and serialization; do not log your environment or raw HTTP headers.

The optional MCP example connects to `https://data.flashdata.dev/mcp` with the
same header. It only discovers tools and prints their names.

Support: support@flashdata.dev.
