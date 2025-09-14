import json


def read_from_vault(website_name: str, vault_location: str) -> list[str]:
    """Get list of unscraped news links based on news platform from vault

    Args:
        website_name (str): the name of the news platform
        vault_location (str): the system location of the vault

    Returns:
        list[str]: the list of unscraped news links
    """
    with open(vault_location, "r") as f:
        data: dict[str, list[str]] = json.load(f)
    return data[website_name]


def save_to_vault(website_name: str, vault_location: str, link_list: list[str]) -> None:
    """Save list of unscraped news links based on news platform to vault

    Args:
        website_name (str): the name of the news platform
        vault_location (str): the system location of the vault
        link_list (list[str]): the list of unscraped news links
    """
    with open(vault_location, "r") as f:
        data: dict[str, list[str]] = json.load(f)

    data[website_name].extend(link_list)

    with open(vault_location, "w") as f:
        json.dump(data, f)


def clear_from_vault(website_name: str, vault_location: str) -> None:
    """Clear the list of unscraped news links based on news platform from vault

    Args:
        website_name (str): the name of the news platform
        vault_location (str): the system location of the vault
    """
    with open(vault_location, "r") as f:
        data: dict[str, list[str]] = json.load(f)

    data[website_name] = []

    with open(vault_location, "w") as f:
        json.dump(data, f)
