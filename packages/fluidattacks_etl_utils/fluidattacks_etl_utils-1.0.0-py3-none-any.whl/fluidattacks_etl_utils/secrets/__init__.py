from __future__ import (
    annotations,
)

import inspect
import tempfile
from collections.abc import (
    Callable,
)
from dataclasses import (
    dataclass,
)
from pathlib import (
    Path,
)

import requests
from fa_purity import (
    Cmd,
    FrozenList,
    PureIterFactory,
    Result,
    ResultE,
    ResultTransform,
)
from fa_purity.json import (
    JsonObj,
    JsonPrimitiveUnfolder,
    JsonUnfolder,
    Unfolder,
)

from fluidattacks_etl_utils.bug import (
    Bug,
)

from . import (
    _integrates,
    _snowflake,
    _zoho_leads,
)
from ._core import (
    GenericSecret,
    get_secrets,
)
from ._snowflake import (
    SnowflakeCredentials,
)
from ._zoho_leads import (
    ZohoCreds,
)


@dataclass(frozen=True)
class ObservesSecrets:
    zoho_creds: Cmd[ZohoCreds]
    snowflake_etl_access: Cmd[SnowflakeCredentials]
    integrates_fluid_org_id: Cmd[GenericSecret]
    get_secret: Callable[[str], Cmd[ResultE[GenericSecret]]]
    get_secrets: Callable[[FrozenList[str]], Cmd[ResultE[FrozenList[GenericSecret]]]]


def _fetch_secret_file() -> Cmd[ResultE[Path]]:
    def _fetch() -> ResultE[Path]:
        try:
            url = "https://raw.githubusercontent.com/fluidattacks/universe/trunk/observes/secrets/prod.yaml"
            response = requests.get(url, timeout=10)
            ok_status = 200
            if response.status_code == ok_status:
                with tempfile.NamedTemporaryFile(delete=False, suffix=".yaml") as file:
                    file.write(response.content)
                    return Result.success(Path(file.name))
            return Result.failure(ValueError("response.status_code"))
        except Exception as error:  # noqa: BLE001
            # catching all exceptions is intentional
            return Result.failure(error)

    return Cmd.wrap_impure(_fetch)


def _extract_secret(secrets: JsonObj, key: str) -> ResultE[GenericSecret]:
    return JsonUnfolder.require(
        secrets,
        key,
        lambda v: Unfolder.to_primitive(v).bind(JsonPrimitiveUnfolder.to_str).map(GenericSecret),
    )


def _standard_implementation(secrets: Path) -> ObservesSecrets:
    zoho_creds = (
        get_secrets(secrets)
        .map(lambda r: r.bind(lambda s: _zoho_leads.decode_zoho_creds(secrets, s)))
        .map(lambda r: Bug.assume_success("zoho_creds", inspect.currentframe(), (), r))
    )
    snowflake_etl_access = (
        get_secrets(secrets)
        .map(lambda r: r.bind(lambda s: _snowflake.decode_snowflake_creds(secrets, s)))
        .map(lambda r: Bug.assume_success("snowflake_etl_access", inspect.currentframe(), (), r))
    )
    integrates_fluid_org_id = (
        get_secrets(secrets)
        .map(lambda r: r.bind(lambda s: _integrates.decode_fluid_org_id(secrets, s)))
        .map(lambda r: Bug.assume_success("integrates_fluid_org_id", inspect.currentframe(), (), r))
    )
    return ObservesSecrets(
        zoho_creds=zoho_creds,
        snowflake_etl_access=snowflake_etl_access,
        integrates_fluid_org_id=integrates_fluid_org_id,
        get_secret=lambda k: get_secrets(secrets).map(
            lambda r: r.bind(
                lambda j: _extract_secret(j, k),
            ),
        ),
        get_secrets=lambda i: get_secrets(secrets).map(
            lambda r: r.bind(
                lambda j: ResultTransform.all_ok(
                    PureIterFactory.from_list(i).map(lambda k: _extract_secret(j, k)).to_list(),
                ),
            ),
        ),
    )


@dataclass(frozen=True)
class ObservesSecretsFactory:
    @staticmethod
    def new() -> Cmd[ResultE[ObservesSecrets]]:
        return _fetch_secret_file().map(lambda r: r.map(_standard_implementation))


__all__ = [
    "GenericSecret",
    "SnowflakeCredentials",
    "ZohoCreds",
]
