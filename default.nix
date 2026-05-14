{
  pkgs ? import <nixpkgs> { },
  ...
}:

pkgs.python3Packages.buildPythonPackage {
  pname = "NEU-ipgw-manager";
  version = "3.3";

  src = ./.;
  /*
  src = pkgs.fetchFromGitHub {
    owner = "Neboer";
    repo = "ipgw-py-manager";
    # branch = "master";
    tag = "v3.3";
    sha256 = "sha256-h+p/xNtYarew/A2RztV/rnsebIfdLFXgt1U3pF6xDCs=";
  };
  */

  pyproject = true;

  propagatedBuildInputs = with pkgs.python3Packages; [
    requests
    click
    beautifulsoup4
    tabulate
    wcwidth
    platformdirs
    setuptools
  ];

  meta = with pkgs.lib; {
    description = "ipgw manager for NEU network gateway";
    homepage = "https://pypi.org/project/NEU-ipgw-manager/";
    license = licenses.mit;
    maintainers = with pkgs; [ Neboer ];
  };
}
