# cici config file format

This page is a reference for cici config file syntax. For a tutorial, see the [Getting started](getting-started.md) section of the site

## File

Top-level cici configuration object.

<table>
  <thead>
    <tr>
      <th>Field</th>
      <th>Default</th>
      <th>Description</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td><strong><code>name</code></strong>*<br/><em>string</em></td>
      <td>
        </td>
      <td>
        <p>Name of the component. All lower-case, hyphen-separated expected.</p><pre><code>crosstool-ng</code></pre>
        </td>
    </tr>
    <tr>
      <td><strong><code>repo_url</code></strong>*<br/><em>string</em></td>
      <td>
        </td>
      <td>
        <p>Web URL for the source repository for this component.</p><pre><code>https://gitlab.com/saferatday0/library/cxx</code></pre>
        </td>
    </tr>
    <tr>
      <td><strong><code>gitlab_project_path</code></strong>*<br/><em>string</em><br/><em>(deprecated)</em></td>
      <td>
        </td>
      <td>
        <p>Full project path for this component on Gitlab.</p><pre><code>saferatday0/library/python</code></pre>
        </td>
    </tr>
    <tr>
      <td><strong><code>brief</code></strong>*<br/><em>string</em></td>
      <td>
        </td>
      <td>
        <p>Short, one-line description of a component. Supports Markdown.</p></td>
    </tr>
    <tr>
      <td><strong><code>description</code></strong>*<br/><em>string</em></td>
      <td>
        </td>
      <td>
        <p>Multi-line description of a component. Supports Markdown.</p></td>
    </tr>
    <tr>
      <td><strong><code>groups</code></strong><br/><em><a href="#group">Group</a> array</em></td>
      <td>
        <code>[]</code></td>
      <td>
        <p>List of groups to declare.</p></td>
    </tr>
    <tr>
      <td><strong><code>targets</code></strong><br/><em><a href="#target">Target</a> array</em></td>
      <td>
        <code>[]</code></td>
      <td>
        <p>List of pipeline targets to declare.</p></td>
    </tr>
    <tr>
      <td><strong><code>variables</code></strong><br/><em>object</em></td>
      <td>
        <code>{}</code></td>
      <td>
        <p>Dictionary of input variables to declare.</p></td>
    </tr>
    </tbody>
</table>

## Container

Container runtime configuration for this target.

<table>
  <thead>
    <tr>
      <th>Field</th>
      <th>Default</th>
      <th>Description</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td><strong><code>image</code></strong>*<br/><em>string</em></td>
      <td>
        </td>
      <td>
        <p>Container image to use for this target.</p></td>
    </tr>
    <tr>
      <td><strong><code>entrypoint</code></strong><br/><em>string array</em></td>
      <td>
        <code>[]</code></td>
      <td>
        <p>Container entrypoint to use for this target.</p></td>
    </tr>
    </tbody>
</table>

## GitLabIncludeTarget

Custom name for a GitLab CI/CD Include target.

<table>
  <thead>
    <tr>
      <th>Field</th>
      <th>Default</th>
      <th>Description</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td><strong><code>name</code></strong>*<br/><em>string</em></td>
      <td>
        </td>
      <td>
        <p>Name of GitLab include target.</p></td>
    </tr>
    </tbody>
</table>

## Group

A logical set of pipeline targets.

<table>
  <thead>
    <tr>
      <th>Field</th>
      <th>Default</th>
      <th>Description</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td><strong><code>name</code></strong>*<br/><em>string</em></td>
      <td>
        </td>
      <td>
        <p>Name of this group.</p></td>
    </tr>
    <tr>
      <td><strong><code>brief</code></strong>*<br/><em>string</em></td>
      <td>
        </td>
      <td>
        <p>Short, one-line description of this group. Supports Markdown.</p></td>
    </tr>
    <tr>
      <td><strong><code>description</code></strong>*<br/><em>string</em></td>
      <td>
        </td>
      <td>
        <p>Multi-line, long-form description of this group. Supports Markdown.</p></td>
    </tr>
    </tbody>
</table>

## PreCommitHookTarget

Custom name for a pre-commit hook target.

<table>
  <thead>
    <tr>
      <th>Field</th>
      <th>Default</th>
      <th>Description</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td><strong><code>name</code></strong>*<br/><em>string</em></td>
      <td>
        </td>
      <td>
        <p>Name of pre-commit hook.</p></td>
    </tr>
    </tbody>
</table>

## Target

Defines a target pipeline to be generated.

<table>
  <thead>
    <tr>
      <th>Field</th>
      <th>Default</th>
      <th>Description</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td><strong><code>name</code></strong>*<br/><em>string</em></td>
      <td>
        </td>
      <td>
        <p>Name of a pipeline target. All lower-case, hyphen-separated (<code>kebab-case</code>) is expected.</p></td>
    </tr>
    <tr>
      <td><strong><code>brief</code></strong>*<br/><em>string</em></td>
      <td>
        </td>
      <td>
        <p>Short, one-line description of a pipeline target. Supports Markdown.</p></td>
    </tr>
    <tr>
      <td><strong><code>description</code></strong>*<br/><em>string</em></td>
      <td>
        </td>
      <td>
        <p>Multi-line, long-form description of a pipeline target. Supports Markdown.</p></td>
    </tr>
    <tr>
      <td><strong><code>groups</code></strong><br/><em>string array</em></td>
      <td>
        <code>[]</code></td>
      <td>
        <p>Denote a logical grouping of pipeline targets.</p></td>
    </tr>
    <tr>
      <td><strong><code>tags</code></strong><br/><em>string array</em></td>
      <td>
        <code>[]</code></td>
      <td>
        <p>Tags for curating jobs according to their purpose.</p></td>
    </tr>
    <tr>
      <td><strong><code>container</code></strong><br/><em><a href="#container">Container</a></em></td>
      <td>
        <code>None</code></td>
      <td>
        <p>Container runtime configuration for this pipeline target.</p></td>
    </tr>
    <tr>
      <td><strong><code>precommit_hook</code></strong><br/><em><a href="#precommithooktarget">PreCommitHookTarget</a></em><br/><em>(deprecated)</em></td>
      <td>
        <code>None</code></td>
      <td>
        <p>Configuration for the pre-commit hook.</p></td>
    </tr>
    <tr>
      <td><strong><code>gitlab_include</code></strong><br/><em><a href="#gitlabincludetarget">GitLabIncludeTarget</a></em><br/><em>(deprecated)</em></td>
      <td>
        <code>None</code></td>
      <td>
        <p>Configuration for the GitLab CI/CD include.</p></td>
    </tr>
    </tbody>
</table>

## Variable

Defines a variable to be consumed by the target.

<table>
  <thead>
    <tr>
      <th>Field</th>
      <th>Default</th>
      <th>Description</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td><strong><code>name</code></strong>*<br/><em>string</em></td>
      <td>
        </td>
      <td>
        <p>Name of a variable.</p><pre><code>PYTHON_VERSION</code></pre>
        </td>
    </tr>
    <tr>
      <td><strong><code>brief</code></strong>*<br/><em>string</em></td>
      <td>
        </td>
      <td>
        <p>Short, one-line description of a variable. Supports Markdown.</p></td>
    </tr>
    <tr>
      <td><strong><code>default</code></strong>*<br/><em>string</em></td>
      <td>
        </td>
      <td>
        <p>Default value for this variable.</p></td>
    </tr>
    <tr>
      <td><strong><code>description</code></strong>*<br/><em>string</em></td>
      <td>
        </td>
      <td>
        <p>Multi-line, long-form description of this variable. Support Markdown.</p></td>
    </tr>
    <tr>
      <td><strong><code>required</code></strong><br/><em>boolean</em></td>
      <td>
        <code>False</code></td>
      <td>
        <p>Is this variable required to use the pipeline?</p></td>
    </tr>
    <tr>
      <td><strong><code>examples</code></strong><br/><em><a href="#variableexample">VariableExample</a> array</em></td>
      <td>
        <code>[]</code></td>
      <td>
        <p>List of examples to demonstrate this variable.</p></td>
    </tr>
    </tbody>
</table>

## VariableExample

An example of how the provided variable should be used.

<table>
  <thead>
    <tr>
      <th>Field</th>
      <th>Default</th>
      <th>Description</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td><strong><code>value</code></strong>*<br/><em>string</em></td>
      <td>
        </td>
      <td>
        <p>Example value for the variable.</p></td>
    </tr>
    <tr>
      <td><strong><code>brief</code></strong>*<br/><em>string</em></td>
      <td>
        </td>
      <td>
        <p>Short, one-line description of a variable example.</p></td>
    </tr>
    </tbody>
</table>
