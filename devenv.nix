{
  pkgs,
  lib,
  config,
  ...
}:

{
  # https://devenv.sh/languages/
  languages.python = {
    enable = true;
    poetry.enable = true;
    # To automatically install packages from requirements.txt or pyproject.toml:
    # uv.sync.enable = true;
  };

  # https://devenv.sh/packages/
  # Provides libpq for psycopg2, which is typically listed in your project's requirements
  packages = [
    pkgs.postgresql
    # pkgs.python3Packages.setuptools # Required for building
    # pkgs.python3Packages.wheel # Required for wheel-based installs
    # pkgs.python3Packages.alembic # Required for wheel-based installs
    pkgs.libpq
    pkgs.openssl

  ];

  # https://devenv.sh/services/
  services.postgres.enable = true;

  # See full reference at https://devenv.sh/reference/options/
}
