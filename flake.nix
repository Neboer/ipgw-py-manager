{
  description = "NEU ipgw manager";

  inputs = {
    nixpkgs = {
      url = "github:NixOS/nixpkgs/nixos-unstable";
    };
    flake-utils = {
      url = "github:numtide/flake-utils";
    };
  };

  outputs = { self, nixpkgs, flake-utils }:
    flake-utils.lib.eachDefaultSystem (system:
      let
        pkgs = import nixpkgs {
          inherit system;
        };
      in
      {
        packages.default = import ./default.nix { inherit pkgs; };
        
        apps.default = {
          type = "app";
          program = "${self.packages.${system}.default}/bin/ipgw";
        };

        devShells.default = pkgs.mkShell {
          packages = with pkgs; [
            python3
            python3Packages.requests
            python3Packages.click
            python3Packages.beautifulsoup4
            python3Packages.tabulate
            python3Packages.wcwidth
            python3Packages.platformdirs
            python3Packages.setuptools
            python3Packages.setupmeta
          ];
        };
      }
    );
}
