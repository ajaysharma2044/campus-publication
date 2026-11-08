"""Provider adapters. Every adapter exposes capability() → Capability so the dashboard and
scheduler can state truthfully whether an integration is connected, unconnected, or disabled.
A stubbed or fixture response is never reported as connected."""
