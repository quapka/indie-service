{
  description = "Indistinguishability Service";

  inputs = {
    nixpkgs.url = "github:NixOS/nixpkgs/nixos-unstable";
    flake-utils.url = "github:numtide/flake-utils";
    custom-nixpkgs.url = "github:quapka/nixpkgs/customPkgs";
  };

  outputs =
    {
      self,
      nixpkgs,
      custom-nixpkgs,
      flake-utils,
      ...
    }:
    flake-utils.lib.eachDefaultSystem (
      system:
      let
        overlays = [ ];
        pkgs = import nixpkgs { inherit system overlays; };
        customPkgs = import custom-nixpkgs { inherit system overlays; };
      in
      with pkgs;
      {
        packages = rec { };
        devShells.default = mkShell {
          buildInputs =
            [ python312 ]
            ++ (with pkgs.python312Packages; [
              cryptography
              flake8
              mypy
              black
            ]);
        };
      }
    );
}
