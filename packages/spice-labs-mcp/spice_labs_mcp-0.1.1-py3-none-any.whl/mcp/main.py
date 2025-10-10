import os
import requests
from mcp.fastmcp import FastMCP

# Initialize FastMCP server
mcp = FastMCP("spice-labs-mcp")

# Constants
PUBLIC_API_BASE = "https://spicesalad.org/omnibor"
PRIVATE_API_BASE = "https://spicesalad.org/api/project/v1/omnibor"
ZAATAR_API_BASE = "https://zaatar.spice-labs.dev/api/package"

def _get_headers():
    token = os.getenv("SPICE_JWT_TOKEN")
    return {"Authorization": f"Bearer {token}"} if token else {}

@mcp.tool()
async def get_entry(identifier: str) -> dict:
    """Fetch the public ADG entry or alias for identifier.

        Args:
            identifier: 83 character ID
        """


    r = requests.get(f"{PUBLIC_API_BASE}/{identifier}")
    r.raise_for_status()
    return r.json()

@mcp.tool()
async def resolve_alias(identifier: str) -> dict:
    """Resolve identifier to its real ADG entry.

        Args:
            identifier: 83 character ID
        """
    r = requests.get(f"{PUBLIC_API_BASE}/aa/{identifier}")
    r.raise_for_status()
    return r.json()

@mcp.tool()
async def get_north(identifier: str) -> list:
    """Return ADG entries 'up' from identifier.

        Args:
            identifier: 83 character ID
        """
    r = requests.get(f"{PUBLIC_API_BASE}/north/{identifier}")
    r.raise_for_status()
    return r.json()

@mcp.tool()
async def get_north_purls(identifier: str) -> list:
    """Return all PURLs of nodes 'up' from identifier.

        Args:
            identifier: 83 character ID
        """
    r = requests.get(f"{PUBLIC_API_BASE}/north_purls/{identifier}")
    r.raise_for_status()
    return r.json()

@mcp.tool()
async def get_north_terminals(identifier: str) -> list:
    """Return high-level terminal nodes above identifier.

        Args:
            identifier: 83 character ID
        """
    r = requests.get(f"{PUBLIC_API_BASE}/north_terminals/{identifier}")
    r.raise_for_status()
    return r.json()

@mcp.tool()
async def bulk_lookup(identifiers: list) -> list:
    """Fetch ADG entries from identifiers.

        Args:
            identifiers: 83 character IDs in a list
        """
    r = requests.post(f"{PUBLIC_API_BASE}/bulk", json=identifiers)
    r.raise_for_status()
    return r.json()

@mcp.tool()
async def flatten(identifier: str) -> list:
    """Return all downstream nodes from identifier.

        Args:
            identifier: 83 character ID
        """
    r = requests.get(f"{PUBLIC_API_BASE}/flatten/{identifier}")
    r.raise_for_status()
    return r.json()

@mcp.tool()
async def flatten_source(identifier: str) -> list:
    """Return all downstream nodes via 'built:from' from identifier.

        Args:
            identifier: 83 character ID
        """
    r = requests.get(f"{PUBLIC_API_BASE}/flatten_source/{identifier}")
    r.raise_for_status()
    return r.json()

@mcp.tool()
async def find_package_salad(identifier: str) -> list:
    """Returns the all of the locations from a specific purl, using the Salad API

    Args:
        identifier: PURL
        """
    r = requests.get(f"{PUBLIC_API_BASE}/{identifier}")
    return r.json()

@mcp.tool()
async def find_package_zataar(purl, resolve=True, fresh_within_seconds=10, wait_seconds=10) -> list:
    """Uses Zaatar to return all of the locations of a package from a specific purl.
    Args:
        purl (str): The package URL (purl) to look up.
                    Example: "pkg:npm/marked@0.3.6"
        resolve (bool): Whether to resolve the package information.
        fresh_within_seconds (int): The desired data freshness in seconds.
        wait_seconds (int): The maximum time to wait for a response.
        """
    params = {
        "purl": purl,
        "resolve": str(resolve).lower(),
        "freshWithinSeconds": fresh_within_seconds,
        "waitSeconds": wait_seconds
    }
    r = requests.get(ZAATAR_API_BASE, params=params)
    r.raise_for_status()
    return r.json()


if __name__ == "__main__":
    mcp.run(transport='stdio')