{
  description = "Common ETL utils";

  inputs = {
    observes_flake_builder = {
      url =
        "github:fluidattacks/universe/551d13f4a2ced648f05de7a2b43172f499e7af1f?shallow=1&dir=observes/common/std_flake";
    };
  };

  outputs = { self, ... }@inputs:
    let
      build_args = { system, python_version, nixpkgs, pynix }:
        import ./build {
          inherit nixpkgs pynix;
          src = import ./build/filter.nix nixpkgs.nix-filter self;
        };
    in { packages = inputs.observes_flake_builder.outputs.build build_args; };
}
