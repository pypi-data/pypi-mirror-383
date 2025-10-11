import inspect
from dataclasses import (
    dataclass,
)
from pathlib import (
    Path,
)

from fa_purity import (
    ResultE,
)
from fa_purity.json import (
    JsonObj,
    JsonPrimitiveUnfolder,
    JsonUnfolder,
    JsonValueFactory,
    Unfolder,
)

from fluidattacks_etl_utils.bug import (
    Bug,
)


@dataclass(frozen=True)
class ZohoCreds:
    client_id: str
    client_secret: str
    refresh_token: str

    def __repr__(self) -> str:
        return "[MASKED]"

    def __str__(self) -> str:
        return "[MASKED]"


def _decode_zoho_creds_inner(creds: JsonObj) -> ResultE[ZohoCreds]:
    _client_id = JsonUnfolder.require(creds, "client_id", Unfolder.to_primitive).bind(
        JsonPrimitiveUnfolder.to_str,
    )
    _client_secret = JsonUnfolder.require(creds, "client_secret", Unfolder.to_primitive).bind(
        JsonPrimitiveUnfolder.to_str,
    )
    _refresh_token = JsonUnfolder.require(creds, "refresh_token", Unfolder.to_primitive).bind(
        JsonPrimitiveUnfolder.to_str,
    )
    return _client_id.bind(
        lambda client_id: _client_secret.bind(
            lambda client_secret: _refresh_token.map(
                lambda refresh_token: ZohoCreds(
                    client_id=client_id,
                    client_secret=client_secret,
                    refresh_token=refresh_token,
                ),
            ),
        ),
    )


def decode_zoho_creds(secrets: Path, raw: JsonObj) -> ResultE[ZohoCreds]:
    decoded = (
        JsonUnfolder.require(raw, "zoho_crm_etl_leads", Unfolder.to_primitive)
        .bind(JsonPrimitiveUnfolder.to_str)
        .bind(JsonValueFactory.loads)
        .bind(Unfolder.to_json)
        .bind(_decode_zoho_creds_inner)
    )
    return decoded.alt(
        lambda e: Bug.new("decode_zoho_creds", inspect.currentframe(), e, (str(secrets),)),
    )
