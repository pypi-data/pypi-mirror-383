{ nixpkgs, pynix, src, }:
let
  deps = import ./deps { inherit nixpkgs pynix; };
  requirements = deps: {
    runtime_deps = with deps.python_pkgs;
      [
        fa-purity
        requests
        types-requests
        pathos
        python-dateutil
        types-python-dateutil
      ] ++ [ deps.nixpkgs.sops ];
    build_deps = with deps.python_pkgs; [ flit-core ];
    test_deps = with deps.python_pkgs; [
      arch-lint
      mypy
      pytest
      pytest-cov
      pytest-timeout
      ruff
    ];
  };
in {
  inherit src requirements;
  root_path = "observes/common/etl-utils";
  module_name = "fluidattacks_etl_utils";
  pypi_token_var = "ETL_UTILS_TOKEN";
  defaultDeps = deps;
  override = b: b;
}

