{
  description = "PSET1: Demand Prediction Service";

  inputs = {
    nixpkgs.url = "github:NixOS/nixpkgs/nixos-unstable";
    flake-utils.url = "github:numtide/flake-utils";
    rust-overlay.url = "github:oxalica/rust-overlay";
    resources.url = "github:yuuhikaze/resources";
  };

  outputs =
    {
      nixpkgs,
      flake-utils,
      rust-overlay,
      resources,
      ...
    }:
    flake-utils.lib.eachDefaultSystem (
      system:
      let
        overlays = [ (import rust-overlay) ];
        pkgs = import nixpkgs { inherit system overlays; };

        pythonEnv = pkgs.python3.withPackages (
          ps: with ps; [
            fastapi
            streamlit
            uvicorn
            sqlalchemy
            pydantic
            pytest
            httpx
            requests
          ]
        );
      in
      {
        devShells.default = pkgs.mkShell {
          inputsFrom = [ resources.outputs.devShells.${system}.docs ];
          buildInputs = [
            pythonEnv
            pkgs.docker
            pkgs.docker-compose
            pkgs.git
          ];
          shellHook = ''
            echo "====== PSET1 Development Environment ======="
            echo "Python: $(python --version)"
            echo "Docker: $(docker --version)"
            echo "============================================"
          '';
        };
      }
    );
}
