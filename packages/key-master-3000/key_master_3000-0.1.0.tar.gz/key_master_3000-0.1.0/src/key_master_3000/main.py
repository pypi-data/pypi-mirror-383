import pyperclip
import sys
from InquirerPy import inquirer
from azure.identity import DefaultAzureCredential
from azure.mgmt.resource import SubscriptionClient
from azure.mgmt.keyvault import KeyVaultManagementClient
from azure.keyvault.secrets import SecretClient


def fuzzy_select(options: list[str], prompt: str) -> str | None:
    try:
        if not options:
            return None
        return inquirer.fuzzy(  # type:ignore
            message=prompt,
            choices=options,
            max_height="70%",
            default=None,
            multiselect=False,
        ).execute()
    except KeyboardInterrupt:
        print("❌ No selection made!")
        sys.exit(1)


def select_subscription() -> str:
    """List and select an Azure subscription."""
    credential = DefaultAzureCredential()
    client = SubscriptionClient(credential)

    subs = list(client.subscriptions.list())
    if not subs:
        print("❌ No subscriptions found.")
        sys.exit(1)

    lines = [f"{s.display_name} ({s.subscription_id})" for s in subs]
    selected = fuzzy_select(lines, "Select Azure subscription: ")

    if not selected:
        print("❌ No subscription selected.")
        sys.exit(1)

    selection: str | None = None
    for s in subs:
        if s.subscription_id is not None and s.subscription_id in selected:
            selection = s.subscription_id

    if selection is None:
        print("❌ No selection.")
        sys.exit(1)

    return selection


def select_keyvault(subscription_id: str) -> str:
    """List and select a Key Vault within a subscription."""
    credential = DefaultAzureCredential()
    client = KeyVaultManagementClient(credential, subscription_id)
    vaults = list(client.vaults.list())

    if not vaults:
        print("❌ No Key Vaults found in this subscription.")
        sys.exit(1)

    vault_lines = [f"{v.name} ({v.location})" for v in vaults]
    selected = fuzzy_select(vault_lines, "Select Key Vault: ")

    if not selected:
        print("❌ No Key Vault selected.")
        sys.exit(1)

    out: str | None = None
    for v in vaults:
        if v.name is not None and v.name in selected:
            out = v.name

    if out is None:
        print("❌ No Key Vault selected.")
        sys.exit(1)

    return out


def copy_secret_to_clipboard(vault_name: str) -> str | None:
    """List and select a secret within a Key Vault."""
    vault_url = f"https://{vault_name}.vault.azure.net"
    credential = DefaultAzureCredential()
    client = SecretClient(vault_url=vault_url, credential=credential)

    secrets = list(client.list_properties_of_secrets())
    if not secrets:
        print("❌ No secrets found in this vault.")
        sys.exit(1)

    secret_names = [s.name for s in secrets if s.name is not None]
    selected = fuzzy_select(secret_names, f"Select secret from {vault_name}: ")

    if not selected:
        print("❌ No secret selected.")
        sys.exit(1)

    secret = client.get_secret(selected)
    if secret.value is None:
        print("❌ Secret does not have a value")
        sys.exit(1)

    copy_to_clipboard(secret.value)
    print("✅ Selected secret copied to clipboard")


def copy_to_clipboard(text: str):
    pyperclip.copy(text)


def main():
    subscription_id = select_subscription()
    vault_name = select_keyvault(subscription_id)
    copy_secret_to_clipboard(vault_name)
