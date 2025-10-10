from typing import Any, Dict
from oocana import InputHandleDef, CredentialInput


def generate_credential_input(credential_path: str) -> CredentialInput | None:
    """Generate a CredentialInput from a credential path string.

    The credential path should be in the format `${{OO_CREDENTIAL:type,name,id}}`. If the format is incorrect,
    the function returns None.
    """

    if not (credential_path.startswith("${{OO_CREDENTIAL:") and credential_path.endswith("}}")):
        # logger warning("Credential path format is incorrect. Expected to start with '${{OO_CREDENTIAL:' and end with '}}'.")
        return None
    
    if credential_path.count(",") != 2:
        # logger warning("Credential path format is incorrect. Expected exactly two commas.")
        return None

    credential_path = credential_path.removeprefix("${{OO_CREDENTIAL:").removesuffix("}}")
    if credential_path:
        try:
            type, _name, id = credential_path.split(",", maxsplit=2)
            return CredentialInput(type, id)
        except ValueError:
            return None
    return None

def replace_credential(
    inputs: Any,
    input_def: Dict[str, InputHandleDef] | None = None,
) -> Any:
    if not isinstance(inputs, dict):
        return inputs

    assert isinstance(inputs, dict)

    for k, v in inputs.items():
        current_input_def = input_def.get(k) if input_def else None
        if current_input_def is None:
            continue
        if isinstance(v, str) and current_input_def.is_credential_handle():
            cred_input = generate_credential_input(v)
            inputs[k] = cred_input
    return inputs