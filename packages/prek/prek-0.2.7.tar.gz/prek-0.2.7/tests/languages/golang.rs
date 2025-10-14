use assert_fs::assert::PathAssert;
use assert_fs::fixture::PathChild;
use constants::env_vars::EnvVars;

use crate::common::{TestContext, cmd_snapshot};

/// Test `language_version` parsing and installation for golang hooks.
/// We use `setup-go` action to install go 1.24 in CI, so go 1.23 will be auto downloaded.
#[test]
fn language_version() -> anyhow::Result<()> {
    if !EnvVars::is_set(EnvVars::CI) {
        // Skip when not running in CI, as we may have other go versions installed locally.
        return Ok(());
    }

    let context = TestContext::new();
    context.init_project();
    context.write_pre_commit_config(indoc::indoc! {r"
        repos:
          - repo: local
            hooks:
              - id: golang
                name: golang
                language: golang
                entry: go version
                language_version: '1.24'
                pass_filenames: false
                always_run: true
              - id: golang
                name: golang
                language: golang
                entry: go version
                language_version: go1.24
                always_run: true
                pass_filenames: false
              - id: golang
                name: golang
                language: golang
                entry: go version
                language_version: '1.23' # will auto download
                always_run: true
                pass_filenames: false
              - id: golang
                name: golang
                language: golang
                entry: go version
                language_version: go1.23
                always_run: true
                pass_filenames: false
              - id: golang
                name: golang
                language: golang
                entry: go version
                language_version: go1.23
                always_run: true
                pass_filenames: false
              - id: golang
                name: golang
                language: golang
                entry: go version
                language_version: '<1.25'
                always_run: true
                pass_filenames: false
    "});
    context.git_add(".");

    let go_dir = context.home_dir().child("tools").child("go");
    go_dir.assert(predicates::path::missing());

    let filters = [(
        r"go version (go1\.\d{1,2})\.\d{1,2} ([\w]+/[\w]+)",
        "go version $1.X [OS]/[ARCH]",
    )]
    .into_iter()
    .chain(context.filters())
    .collect::<Vec<_>>();

    cmd_snapshot!(filters, context.run().arg("-v"), @r#"
    success: true
    exit_code: 0
    ----- stdout -----
    golang...................................................................Passed
    - hook id: golang
    - duration: [TIME]
      go version go1.24.X [OS]/[ARCH]
    golang...................................................................Passed
    - hook id: golang
    - duration: [TIME]
      go version go1.24.X [OS]/[ARCH]
    golang...................................................................Passed
    - hook id: golang
    - duration: [TIME]
      go version go1.23.X [OS]/[ARCH]
    golang...................................................................Passed
    - hook id: golang
    - duration: [TIME]
      go version go1.23.X [OS]/[ARCH]
    golang...................................................................Passed
    - hook id: golang
    - duration: [TIME]
      go version go1.23.X [OS]/[ARCH]
    golang...................................................................Passed
    - hook id: golang
    - duration: [TIME]
      go version go1.24.X [OS]/[ARCH]

    ----- stderr -----
    "#);

    // Check that only go 1.23 is installed.
    let installed_versions = go_dir
        .read_dir()?
        .flatten()
        .filter_map(|d| {
            let filename = d.file_name().to_string_lossy().to_string();
            if filename.starts_with('.') {
                None
            } else {
                Some(filename)
            }
        })
        .collect::<Vec<_>>();

    assert_eq!(
        installed_versions.len(),
        1,
        "Expected only one Go version to be installed, but found: {installed_versions:?}"
    );
    assert!(
        installed_versions.iter().any(|v| v.contains("1.23")),
        "Expected Go 1.23 to be installed, but found: {installed_versions:?}"
    );

    Ok(())
}

/// Test a remote go hook.
#[test]
fn remote_hook() {
    let context = TestContext::new();
    context.init_project();

    // Test that `additional_dependencies` are installed correctly.
    context.write_pre_commit_config(indoc::indoc! {r#"
        repos:
          - repo: local
            hooks:
              - id: golang
                name: golang
                language: golang
                entry: gofumpt -h
                additional_dependencies: ["mvdan.cc/gofumpt@v0.8.0"]
                always_run: true
                verbose: true
                language_version: '1.23.11' # will auto download
                pass_filenames: false
    "#});
    context.git_add(".");

    cmd_snapshot!(context.filters(), context.run(), @r#"
    success: true
    exit_code: 0
    ----- stdout -----
    golang...................................................................Passed
    - hook id: golang
    - duration: [TIME]
      usage: gofumpt [flags] [path ...]
      	-version  show version and exit

      	-d        display diffs instead of rewriting files
      	-e        report all errors (not just the first 10 on different lines)
      	-l        list files whose formatting differs from gofumpt's
      	-w        write result to (source) file instead of stdout
      	-extra    enable extra rules which should be vetted by a human

      	-lang       str    target Go version in the form "go1.X" (default from go.mod)
      	-modpath    str    Go module path containing the source file (default from go.mod)

    ----- stderr -----
    "#);

    // Run hooks with newly downloaded go.
    context.write_pre_commit_config(indoc::indoc! {r"
        repos:
          - repo: https://github.com/prek-test-repos/golang-hooks
            rev: v1.0
            hooks:
              - id: echo
                verbose: true
                language_version: '1.23.11' # will auto download
        "});
    context.git_add(".");

    cmd_snapshot!(context.filters(), context.run(), @r"
    success: true
    exit_code: 0
    ----- stdout -----
    echo.....................................................................Passed
    - hook id: echo
    - duration: [TIME]
      .pre-commit-config.yaml

    ----- stderr -----
    ");

    // Run hooks with system found go.
    context.write_pre_commit_config(indoc::indoc! {r"
        repos:
          - repo: https://github.com/prek-test-repos/golang-hooks
            rev: v1.0
            hooks:
              - id: echo
                verbose: true
                language_version: '1.24.5'
        "});
    context.git_add(".");

    cmd_snapshot!(context.filters(), context.run(), @r"
    success: true
    exit_code: 0
    ----- stdout -----
    echo.....................................................................Passed
    - hook id: echo
    - duration: [TIME]
      .pre-commit-config.yaml

    ----- stderr -----
    ");
}
