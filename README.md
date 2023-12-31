# README #

# General

This Git custom merge driver `keep_ours_paths_merge_driver` supports merging XML- and JSON-files.
It keeps configurable "ours" XPath's or JSON-path's values during a merge.
The primary use cases are merging Maven Pom files and NPM package.json files,
but the merge driver is not limited to these.

In the following chapters it is described as use cases

* how to configure the merge driver to keep XPath's and JSON-path's values,
* how to register the merge driver in `.gitattributes` or `.git/info/attributes`,
* how to define the merge driver in `.git/config`.

About the term "path": In the Git docs it means a file-path.
Regarding this merge driver it means XPath or JSON-path.

# Command line reference

    $ python -m keep_ours_paths_merge_driver -h
    usage: __main__.py [-h] -O BASE -A OURS -B THEIRS [-P PATH]
                       [-p MERGE-STRATEGY:PATH:PATTERN [MERGE-STRATEGY:PATH:PATTERN ...]] [-s SEPARATOR] [-o]
                       [-t {XML,JSON}] [-v] [-l {DEBUG,INFO,WARNING,ERROR,CRITICAL}]
    
    This Git custom merge driver supports merging XML- and JSON-files. It keeps configurable "ours"
    XPath's or JSON-path's values during a merge. The primary use cases are merging Maven Pom files and
    NPM package.json files, but the merge driver is not limited to these.
    
        Version: 1.0.0.dev
        More:    https://github.com/gldog/keep_ours_paths_merge_driver
    
    optional arguments:
      -h, --help            show this help message and exit
      -O BASE, --base BASE  Base version (ancestor's version). Set by Git in %O.
      -A OURS, --ours OURS  Ours version (current version). Set by Git in %A.
      -B THEIRS, --theirs THEIRS
                            Theirs version (other branches' version). Set by Git in %B
      -P PATH, --path PATH  The pathname in which the merged result will be stored. Set by Git in %P.
      -p MERGE-STRATEGY:PATH:PATTERN [MERGE-STRATEGY:PATH:PATTERN ...], --pathspatterns MERGE-STRATEGY:PATH:PATTERN [MERGE-STRATEGY:PATH:PATTERN ...]
                            List of paths with merge-strategy and and path-pattern, separated by ':'.
                            The path is mandatory, the merge-strategy and path-pattern are optional. The
                            merge-strategy is one of ['onconflict-ours', 'always-ours'] (defaults to
                            'onconflict-ours'). If the default separator ':' shall be used in the path
                            itself, a different separator can be defined in parameter -s/--separator.
      -s SEPARATOR, --separator SEPARATOR
                            Used to separate the parts MERGE-STRATEGY, PATH, PATTERN (defaults to ':')
      -o, --stdout          Print the prepared file 'theirs' to stdout.
      -t {XML,JSON}, --filetype {XML,JSON}
                            The file type to merge, one of ['XML', 'JSON']. Defaults to XML.
      -v, --version         show program's version number and exit
      -l {DEBUG,INFO,WARNING,ERROR,CRITICAL}, --loglevel {DEBUG,INFO,WARNING,ERROR,CRITICAL}
                            Log-level: ['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL']. Defaults to INFO.

# Use cases

## General

In this chapter some merge use cases are discussed.

* The terms `SOURCE_REF` and `DEST_BRANCH` are from the `git merge` point of view.
  (`SOURCE_REF` is more general named REF, not BRANCH, because the source for a merge can be a branch or tag or commit.
* The terms `base` (ancestor commit), `ours` and `theirs` are from the merge driver point of view.
* The terms `Parent` and `Child` means branches (not commits).
* The term `M` describes a merge commit.
* Regarding a merge driver there are (maybe confusing) terms:
  The merge driver _registration_ in `.gitattributes` or `.git/info/attributes`,
  the merge driver _definition_ in `.git/config` done with command `git config`,
  and the merge driver _executable_.
* When a server merges a pull request (Github, Bitbucket,...), no merge driver is involved!
* Simplifying the use cases the Pom XPath `/project/version` is used. It is just an example path.

## Use case: Maven pom.xml merge driver to keep the version on "ours" child branch

Imagine there is set a branch-specific version on the Child branch in the pom.xml in XPath `/project/version`.
When updating Child branch from Parent branch, A) no merge conflict occurs,
or B) a merge-conflict occurs in case the version on "theirs" Parent branch is different from the common base-version:

A)

The Parent branch hasn't a new version yet since the Child branch was created, it has still version `v1`.
No merge conflict occurs on the pom.xml `/project/version` XPath on `M`.
The Child branch's version is kept.
This scenario works without a merge driver, but you don't have control when the version on Parent branch gets updated.

      v1   (base)     
    --*------*--------------------------------------------  Parent, (theirs), SOURCE_REF
              \                  |
               \           merge |
                \                ↓
                 *---------------*------------------------  Child, (ours), DEST_BRANCH
               v3-SN          M: v3-SN

B)

The Parent branch got a new version `v2`.
This results in a merge conflict on the pom.xml `/project/version` path on `M` without merge driver.

      v1   (base)   v2
    --*------*------*-------------------------------------  Parent, (theirs), SOURCE_REF
              \                  |
               \           merge |
                \                ↓
                 *---------------*------------------------  Child, (ours), DEST_BRANCH
               v3-SN       M: conflict without merge driver
                           M: v3-SN with merge dirver "onconflict-ours"

The version on Child branch is kept and a merge-conflict is prevented using the merge driver with path merge
strategy `onconflict-ours`:

Set the `merge` attribute in `.gitattributes` for the (top-level) `pom.xml`:

    pom.xml merge=maven-pomxml-keep-ours-xpath-merge-driver

Define the merge driver for the repository clone:

    git config --local merge.maven-pomxml-keep-ours-xpath-merge-driver \
      "keep_ours_paths_merge_driver.pyz -O %O -A %A -B %B -P %P \
        -p './version' './parent/version' './properties/revision'"

(For XPath configurations, the root node "/project" must be given as `.`)

The above command results in the repo's .git/config as:

    [merge "maven-pomxml-keep-ours-xpath-merge-driver"]
        driver = keep_ours_paths_merge_driver.pyz -O %O -A %A -B %B -P %P -p './version' './parent/version' './properties/revision'

This example keeps not only the `./version` but also `./parent/version` and `./properties/revision` for
demonstration.
The path merge strategy `onconflict-ours` is the default and don't have to be given explicitly.

`maven-pomxml-keep-ours-xpath-merge-driver` is the logical name of the merge driver connecting the registration in
`.gitattributes` to the merge driver definition.
The name of the executable is `keep_ours_paths_merge_driver.pyz`.

"pyz" is a fully self-contained zipapp, see chapter "Create a fully self-contained executable zipapp".
In this example it is given without path, its location is given in `PATH`.

## Use case: Maven pom.xml merge driver to prevent version-conflicts when merging a child branch back to parent branch

Merging back the Child branch to the Parent branch, there are again two cases:

A)

The Parent branch hasn't a new version yet since the Child branch was created, is has still version `v1`.
No merge conflict occurs on the pom.xml `/project/version` XPath on `M`.

* WARNING 1: The Child branch's version `v3-SN` wins on `M` not using the merge driver!
* WARNING 2: **Git calls merge drivers only in case of a 3-way-merge.**
  If no change has been made on the file on Parent, without any further action Git won't call the
  merge driver, but will fast-forward Child's file to Parent. So Child wins, what is not expected 
  using "always-ours" on Parent.
  There are examples for "touch file on dest-branch if unchanged" in tests of
  [gldog/keep_ours_paths_merge_driver](https://github.com/gldog/keep_ours_paths_merge_driver/blob/master/tests/integration/test_xml.py)
  and a script
  in [gldog/concurrent_git_merge](https://github.com/gldog/concurrent_git_merge/blob/master/example-scripts/my/clone_repos_and_install_mergedrivers.sh)
  .

                             M: v3-SN without merge driver
        v1   (base)          M: v2 with merge driver "always-ours"
      --*------*-------------------*------------------------  Parent, (ours), DEST_BRANCH
                \                  ↑
                 \           merge |
                  \                |
                   *----------------------------------------  Child, (theirs), SOURCE_REF
                 v3-SN

B)

The Parent branch got a new version `v2`.
This results in a merge conflict on the pom.xml `/project/version` path on `M` not using the merge driver.

                           M: conflict merge driver
      v1   (base)   v2     M: v2 with merge driver "always-ours"
    --*------*------*------------*------------------------  Parent, (ours), DEST_BRANCH
              \                  ↑
               \           merge |
                \                |
                 *----------------------------------------  Child, (theirs), SOURCE_REF
               v3-SN      

Using the merge driver it doesn't matter if `v2` is already on Parent branch or not,
as the merge driver is configured with path merge strategy `always-ours`.

The merge driver's default path merge strategy is `onconflict-ours`.
But from the point of the Parent branch, its branch version shall be kept _always_:
E.g. a release-version must not be overridden nor provoke a merge conflict by a temporary version used on the
Child branch.
Therefore, the merge driver provides the merge-strategy `always-ours`.
The merge-strategy is part of `-p` option, separated by colon (or the value given in `-s/--separator`):

    -p 'always-ours:./version' 'always-ours:./parent/version' 'always-ours:./properties/revision'

The merge-strategy is given per path, and there is not yet an "all path's default" configuration option.

Set the `merge` attribute in `.gitattributes` for the top-level `pom.xml`:

    pom.xml merge=maven-pomxml-keep-ours-xpath-merge-driver

Define the merge driver for the repository:

    git config --local merge.maven-pomxml-keep-ours-xpath-merge-driver.driver \
      "keep_ours_paths_merge_driver.pyz -O %O -A %A -B %B -P %P \
        -p 'always-ours:./version' 'always-ours:./parent/version' 'always-ours:./properties/revision'"

## Problem: One registration in .gitattributes, but two use cases

The previous two use cases showed different demands for the same file `pom.xml`: 1. `onconflict-ours` for a "down" merge
from Parent branch to Child branch, and 2. `always-ours` for an "up" merge back.
It could be someone is responsible for both directions. How to configure the merge driver registration and definition?

You can work around this by the facts

- the merge driver _registration_ can be done in either the checked-in `.gitattributes`,
  or the repo-local setting in `.git/info/attributes`, and
- the _definition_ of a merge driver is a repo-local configuration (`git config --local ...`), and
- you can use two repos.

These allow variants.

The most felxible solution I think is the local registration in `.git/info/attributes` and local definition of the merge
driver:

prepare_merge.sh (simplified):

    # Register merge driver:
    cd my-repo
    # Simplified for demonstration:
    echo "pom.xml merge=maven-pomxml-keep-ours-xpath-merge-driver >> .git/info/attributes
    
    # Define merge driver:
    # "onconflict-ours" is the default, but just to make it obvious.
    : "${MERGE_STRATEGY:=onconflict-ours}"
    git config --local merge.maven-pomxml-keep-ours-xpath-merge-driver.driver \
      "keep_ours_paths_merge_driver.pyz -O %O -A %A -B %B -P %P \
        -p '${MERGE_STRATEGY}:./version' '${MERGE_STRATEGY}:./parent/version' '${MERGE_STRATEGY}:./properties/revision'"

Call for "down" direction:

    prepare_merge.sh

Call for "up" direction:

    MERGE_STRATEGY=always-ours prepare_merge.sh

A variation of this is to define two merge drivers "down" and "up" with different names,
and switch the registration in `.git/info/attributes` dependent on the merge direction.

Or use different clones.

More about Git attributes, from [gitattributes - Defining attributes per path](https://git-scm.com/docs/gitattributes):

Note:

* Here _path_ means file-path.
* GIT_DIR is `.git`.

> When deciding what attributes are assigned to a path, Git consults $GIT_DIR/info/attributes file (which has the
> highest
> precedence), .gitattributes file in the same directory as the path in question, and its parent directories up to the
> toplevel of the work tree (the further the directory that contains .gitattributes is from the path in question, the
> lower its precedence). Finally global and system-wide files are considered (they have the lowest precedence).

The format of the `merge` attribute is the same in `.gitattributes` and `.git/info/attributes`:

    pom.xml merge=maven-pom-xpaths-merge-driver

By this you can override the registration in `.gitattributes` for one direction, or omit `.gitattributes` at all.
But you still have to define the merge driver locally.

Don't define the merge driver globally, as this can afffect merges in complete other repos.

An example how to automatically set up the merge driver is given
in [concurrent_git_merge](https://github.com/gldog/concurrent_git_merge) > example-scripts/my.

## Use case: NPM package.json merge driver to keep the version on "ours" child branch

Register the `merge` attribute in `.gitattributes` for the `package.json`:

    package.json merge=node-packagejson-jsonpaths-merge-driver

Define the merge driver for the repository:

    git config --local merge.node-packagejson-jsonpaths-merge-driver.driver \
      "keep_ours_paths_merge_driver.pyz -O %O -A %A -B %B -P %P -t JSON \
        -p version"

The default is to parse a file as XML. For JSON add the `-t JSON`.

The above command results in the repo's `.git/config` as:

    [merge "node-packagejson-jsonpaths-merge-driver"]
        driver = keep_ours_paths_merge_driver.pyz -O %O -A %A -B %B -P %P -t JSON -p version

# Keep paths by pattern

Paths can be kept by patterns given as regular expressions.
Regular expressions are given as patterns separated by colon (or the value given in `-s/--separator`).

Simplifed pom.xml

    <project>
      ...
      <properties>
        <revision>1.0.0-SNAPSHOT</revision>
        <app1.version>1.2.3</app1.version>    <!-- Keep -->
        <app2.version>4.5.6</app1.version>    <!-- Keep -->
        <app3.version>7.8.9</app1.version>
      <properties>
    </project>

Example: Keep version-properties for app1 and app2 in pom.xml:

    -p './properties/:(app1|app2)[.]version'

Example: Keep all version-properties in pom.xml:

    -p './properties/:.+[.]version'

Example: Keep all dependencies of `@mycompany` in package.json:

    -p 'dependencies.*:@mycompany/.+'

# Merge strategies

The merge driver has the two path merge strategies `onconflict-ours` (default) and `always-ours`.
A strategy is given in path-parameter `-p` in addition to the path separated by colon (or the value given in
`-s/--separator`).

About the term "path": In the Git docs it means a file-path.
Regarding this merge driver it means XPath or JSON-path.

Strategy `onconflict-ours` is the default and is similar to the git merge
strategy [ort with option ours](https://git-scm.com/docs/git-merge#Documentation/git-merge.txt-ort), but only for the
XPath or JSON-path.

From the git docs [git-merge](https://git-scm.com/docs/git-merge#Documentation/git-merge.txt-ours):

> This option forces conflicting hunks to be auto-resolved cleanly by favoring our version. Changes from the other tree
> that do not conflict with our side are reflected in the merge result.

Mode `always-ours` is similar to the git merge
strategy [ours](https://git-scm.com/docs/git-merge#Documentation/git-merge.txt-ours-1).

From the git docs [git-merge](https://git-scm.com/docs/git-merge#Documentation/git-merge.txt-ours-1):

> The resulting tree of the merge is always that of the current branch head, effectively ignoring all changes from all
> other branches.

Examples:

Given explicitly:

    `-p 'onconflict-ours:./some/path:some-pattern'`

Given explicitly:

    `-p 'always-ours:./some/path:some-pattern'`

Without, default:

    `-p './some/path:some-pattern'`

# About leaf- and non-leaf-nodes

The merge driver works only on paths to leaf-nodes, not to objects/lists.
This is because it works text-based, not structure-based.
And non-leaf-nodes would have to be serialised back to text after processing,
but that could re-format the file.
If a path matches a non-leaf-node, the merge driver logs a warning.

Example: The path `./properties` points to the node itself (which is an object), not to the children:

    -p './properties:(app1|app2)[.]version'

WARNING: Base/Ours/Theirs file's XPath '/project/properties' is not a leaf-node. The merge driver works only on
leaf-nodes. This path is ignored.

Adding a trailing slash fixes this:

    -p './properties/:(app1|app2)[.]version'

# About paths, hunks, structures, and formatting

A merge driver is called by `git merge` in general if a 3-way-merge is needed,
not only on files with conflicted lines/hunks.
Git provides the three file-versions ancestor (base), ours, and theirs to a merge driver.
The merge driver can make something with that files, and signal Git back with exit code
0 it has completed the merge, or with exit code >0 Git shall continue the merge with the three file-versions
possibly modified by the merge driver.

The `keep_ours_paths_merge_driver` reads the paths given in `-p`, writes their values to "theirs",
calls `git merge-file ours base theirs`, return that exit code back to Git, and let Git decide how to continue.
The result regarding the matching lines to the paths in `-p` is "ours", because those are present to
`git merge-file` in "theirs" _and_ "ours", and so isn't a conflicted line.

`keep_ours_paths_merge_driver` processes the file-versions base/ours/theirs as text, not as structures.
So it works only on less changed files.
It will not work on files where the paths given in `-p` are restructured in the three file-versions.
In that way it is as robust or weak as Git itself.
Fortunately restructuring XML or JSON is a rare case (I think).

Processing the file-versions as text is a design decision to keep a user's file-formatting.
It would be possible to parse the XML- or JSON-files to a structure, prepare "theirs" in that structure,
and write back the result as text using some formatter existing in Python.
But the resulting outgoing format to "theirs" would probably not match the incoming format.
To achieve proper formatting to not confusing Git's merge, an external formatter must be used to generate back the
incoming format of "theirs": The same formatter that was used to format the three file-versions before check-in.

I experimented with parsing. But unfortunately working with structures rather than text was not as robust as I expected.
There would be an advantage at less restructuring. But heavy restructuring can confuse parsers.

# Create a fully self-contained executable zipapp with shiv

## Create the zipapp

You can create a fully self-contained executable zipapp `keep_ours_paths_merge_driver.pyz` with all dependencies bundled
into it.
This allows simple distribution without letting the users install dependencies.
The zipapp contains the platform-dependent library lxml.
Therefore, a zipapp for each platform has to be built.

The steps are the same for each platform, but the commands differ slightly.

Create zipapp in and for Linux or macOS:

    python3 -m venv venv
    source venv/bin/activate
    pip install -r requirements.txt
    shiv -c keep_ours_paths_merge_driver -o keep_ours_paths_merge_driver.pyz .

Create zipapp in and for Windows Gitbash

    python -m venv venv
    source venv/Scripts/activate
    pip install -r requirements.txt
    shiv -c keep_ours_paths_merge_driver -p python -o keep_ours_paths_merge_driver.pyz .

Without `-p python`, shiv creates the Shebang `#!/usr/bin/env python3`.
But the Python binary shipped with the Windows Python installer is just `python.exe`, not `python3.exe`.
The zipapp won't start.

Setting `-p '/usr/bin/env python'` (python without "3") does weird things issued in
[shiv generates invalid shebang line in git bash (windows/mingw) #168](https://github.com/linkedin/shiv/issues/168),
(still in shiv version 1.0.4).

If you experiment with `-p` and you see `cannot execute: required file not found`, have a look into the zipapp at the
first line to see what shiv has created as Shebang:

    # Test:
    $ ./keep_ours_path_merge_driver.pyz
    bash: ./keep_ours_path_merge_driver.pyz: cannot execute: required file not found
    # Look into the zipapp:
    head -1 keep_ours_path_merge_driver.pyz
    ...

Interestingly, Windows CMD creates `-p '/usr/bin/env python'` as expected:

    (venv) D:\prj\keep_ours_path_merge_driver>shiv -c src -p "/usr/bin/env python" -o keep_ours_path_merge_driver.pyz .
    ...
    (venv) D:\prj\keep_ours_paths_merge_driver>head -1 keep_ours_paths_merge_driver
    #!/usr/bin/env python

And that is executable in Gitbash!

Create zipapp in and for CMD (Windows)

    python -m venv venv
    venv\Scripts\activate.bat
    pip install -r requirements.txt
    shiv -c keep_ours_paths_merge_driver -o keep_ours_paths_merge_driver.pyz .

## About running the zipapp: Temp-dir .shiv

Once executed, for each version of the merge driver (not for each run) an entry in the `.shiv` directory will exist.
This is where Python extracts the zipapp for execution.
You can delete its contents at any time.
The next execution will take a second for extraction.
Dependent on the OS its path is:

* Linux, macOS: `~/.shiv`.
* Windows and Gitbash: `C:\Users\<user>\.shiv`

## Related Links

* [gitattributes - Defining attributes per path](https://git-scm.com/docs/gitattributes)
* [gitrepository-layout - Git Repository Layout](https://git-scm.com/docs/gitrepository-layout)

# Credits

https://github.com/ralfth/pom-merge-driver
