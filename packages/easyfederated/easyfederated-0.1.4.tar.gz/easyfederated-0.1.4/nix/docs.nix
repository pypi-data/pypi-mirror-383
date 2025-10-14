{
  inputs,
  ...
}: {
  imports = [
    inputs.mkdocs-flake.flakeModules.default
    # inputs.nix-mkdocs.flakeModule
  ];
  perSystem = { config, self', inputs', pkgs, system, ... }: {
    documentation.mkdocs-root = ../docs;
    # docs.easyfed.config = {
    #     path = ../docs ;
    #     deps = pp: [
    #       pp.mkdocs-material
    #     ];
    #     config = {
    #       site_name = "EasyFed";
    #       theme.name = "material";
    #       nav = [
    #         { Home = "index.md"; }
    #         { "Getting Started" = "getting-started.md"; }
    #         { "CLI" = "cli.md"; }
    #         { "Library" = "library.md"; }
    #       ];
    #       markdown_extensions = [
    #         "admonition"
    #         "pymdownx.highlight"
    #         "pymdownx.superfences"
    #       ];
    #     };
    #   };
  };
}
