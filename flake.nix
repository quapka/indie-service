{
  description = "Indistinguishability Service";

  inputs = {
    # nixpkgs.url = "github:NixOS/nixpkgs/nixos-unstable";
    nixpkgs.url = "github:NixOS/nixpkgs/24.05";
    flake-utils.url = "github:numtide/flake-utils";
    custom-nixpkgs.url = "github:quapka/nixpkgs/customPkgs";
  };

  outputs =
    {
      self,
      nixpkgs,
      # nixpkgs-24_05,
      custom-nixpkgs,
      flake-utils,
      ...
    }:
    flake-utils.lib.eachDefaultSystem (
      system:
      let
        overlays = [ ];
        pkgs = import nixpkgs { inherit system overlays; };
        # pkgs-24_05 = import nixpkgs-24_05 { inherit system overlays; };
        customPkgs = import custom-nixpkgs { inherit system overlays; };
        # pyscard-2_0_9 = pkgs-24_05.python312Packages.pyscard;
        # myPython = pkgs.python3;
        # pythonWithPkgs = myPython.withPackages (pythonPkgs: with pythonPkgs; [
        #     pytest
        #     # sage
        #     ipython
        #     pyscard
        #     # pyscard-2_0_9
        #   # ]);

        #   # buildInputs =
        #   #   [
        #   #     python312
        #   #   ]
        #   #   ++ (with pkgs.python312Packages; [
        #       cryptography
        #       # secp256k1
        #       fastecdsa
        #       flake8
        #       flask
        #       noiseprotocol
        #       pyjwt
        #       mypy
        #       black
        # ]);
      in
      with pkgs;
      {
        packages = rec { };
        devShells.default = mkShell {
          # python = python3;

          buildInputs = [
            # pythonWithPkgs
            # python3Packages.pyscard

            # nodejs
            # sage
          ]
          ++ (with python3Packages; [
            pytest
            # sage
            ipython
            pyscard
            # pyscard-2_0_9
          # ]);

          # buildInputs =
          #   [
          #     python312
          #   ]
          #   ++ (with pkgs.python312Packages; [
              cryptography
              # secp256k1
              fastecdsa
              flake8
              flask
              noiseprotocol
              pyjwt
              mypy
              black
            ]);
        };
      }
    );
}
