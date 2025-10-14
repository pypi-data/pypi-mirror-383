# SPDX-FileCopyrightText: UL Research Institutes
# SPDX-License-Identifier: Apache-2.0

from typing import Any, Optional

from ruamel.yaml.scalarstring import (
    DoubleQuotedScalarString,
    FoldedScalarString,
    LiteralScalarString,
    PreservedScalarString,
)


# to force ruamel.yml to always emit double quoted strings """" and not single "''"
def always_double_quoted(dumper, data):
    return dumper.represent_scalar("tag:yaml.org,2002:str", data, style='"')


def wrap_if_long(s: str, width: int = 120) -> str:
    # Wrap long strings into multiple lines for YAML folding.
    if len(s) <= width:
        return s
    # break on spaces without splitting words
    parts = []
    while len(s) > width:
        split_at = s.rfind(" ", 0, width)
        if split_at == -1:
            split_at = width
        parts.append(s[:split_at].rstrip())
        s = s[split_at:].lstrip()
    parts.append(s)
    return "\n".join(parts)


# handling string literals
def make_scalar_string(line: str, quote: bool = False):
    # Return an appropriate YAML scalar string based on content.
    if not isinstance(line, str):
        return line

    unindented = line.lstrip()

    # Preserve explicit multiline blocks
    if "\n" in unindented:
        return PreservedScalarString(line)

    # fix extra - >- between lines accidentally created with echo commands
    if unindented.startswith("echo "):
        # inline if short and simple
        if len(unindented) < 100 and not any(
            sym in unindented for sym in ("&&", ";", "\\", "|")
        ):
            return unindented

        return FoldedScalarString(wrap_if_long(unindented))

    # Commands and long lines get folded
    if unindented.startswith(("docker ", "helm ", "tar ", "curl ")):
        return FoldedScalarString(wrap_if_long(unindented))

    # Multi-command sequences get folded
    if any(sym in unindented for sym in ("&&", ";", "\\")):
        return FoldedScalarString(wrap_if_long(unindented))

    # Long assignments get folded
    if (
        "=" in unindented
        and not unindented.startswith(("export ", "set ", "$"))
        and len(unindented) > 100
    ):
        return FoldedScalarString(wrap_if_long(unindented))

    # Explicit quoting when requested
    if quote:
        return DoubleQuotedScalarString(unindented)

    # Default: return plain string
    return unindented


# Rule engine for how YAML should look when written back out
# recursively walk through a Python structure and apply the rules defined
def style_scalars(
    obj: Any, *, quote_keys: Optional[set[str]] = None, parent_key: Optional[str] = None
) -> Any:
    # Default: keys that often need quoting in GitLab CI

    # DEBUGGING:
    # if parent_key == "opentofu-production-trivy":
    #     print("*****DEBUG****** job keys:", list(obj.keys()))

    if quote_keys is None:
        quote_keys = {"variables", "image", "services", "script", "before_script"}

    # if it is a dict, process each key/value recursively
    if isinstance(obj, dict):
        styled: dict[str, Any] = {}

        for k, v in list(obj.items()):
            v = obj[k]
            # 1. keep GitLab workflow 'if' rules unquoted
            if k == "if" and isinstance(v, str):
                styled[k] = v

            # 2. for image, only quote if contains ":" or starts with '$' (i.e. tag or env)
            elif k == "image" and isinstance(v, str):
                # removes any leading or trailing whitespace
                stripped = v.strip()
                if (
                    ":" in stripped
                    or stripped.startswith("$")
                    or stripped.startswith("${")
                ):
                    styled[k] = DoubleQuotedScalarString(v)
                else:
                    styled[k] = v

            # 3. ensures service names like
            # ${CONTAINER_PROXY}docker:28-dind
            # becomes
            # "${CONTAINER_PROXY}docker:28-dind"
            elif k == "services" and isinstance(v, list):
                styled_services = []

                for service in v:
                    if isinstance(service, dict):
                        styled_service = {}
                        for service_key, service_val in service.items():
                            if isinstance(service_val, str):
                                stripped = service_val.strip()
                                if (
                                    stripped.startswith("$")
                                    or stripped.startswith("${")
                                    or ":" in stripped
                                ):
                                    styled_service[service_key] = (
                                        DoubleQuotedScalarString(stripped)
                                    )
                                else:
                                    styled_service[service_key] = stripped  # type: ignore[assignment]
                            else:
                                styled_service[service_key] = style_scalars(
                                    service_val, quote_keys=quote_keys, parent_key=k
                                )
                        styled_services.append(styled_service)
                    else:
                        styled_services.append(
                            style_scalars(service, quote_keys=quote_keys)
                        )

                styled[k] = styled_services

            # 4. always emit description as '|-' block style
            elif k == "description" and isinstance(v, str):
                styled[k] = PreservedScalarString(v)

            # 5. for value, only quote if it looks like plain text, not env vars
            elif k == "value" and isinstance(v, str):
                stripped = v.strip()
                # (NEW) explicitly double-quote empty strings so ruamel emits ""
                if stripped == "":
                    styled[k] = DoubleQuotedScalarString("")
                # always double-quote env variables or any string starting with $
                elif stripped.startswith("$") or stripped.startswith("${"):
                    styled[k] = DoubleQuotedScalarString(stripped)
                # quote if there are dots or dashes
                elif "." in stripped or "-" in stripped:
                    styled[k] = DoubleQuotedScalarString(stripped)
                # otherwise leave it plain
                else:
                    styled[k] = stripped

            # 6. if we are INSIDE variables block, double quote all the strings
            elif k == "variables" and isinstance(v, dict):
                styled_vars: dict[str, Any] = {}

                for var_name, var_val in v.items():
                    # need to flatten the dicts into simple strings so:

                    # variable:
                    #   VARIABLE_HERE:
                    #     value: "$VARIABLE_VALUE"

                    # needs to become

                    # variable:
                    #   VARIABLE_HERE: "$VARIABLE_VALUE"
                    if (
                        isinstance(var_val, dict)
                        and "value" in var_val
                        and len(var_val) == 1
                    ):
                        var_val = var_val["value"]

                    if isinstance(var_val, str):
                        stripped = var_val.strip()

                        # quote env vars ($VAR)
                        if stripped.startswith("$") or stripped.startswith("${"):
                            styled_vars[var_name] = DoubleQuotedScalarString(stripped)

                        # quote ".", "-", or anything with "." in it
                        # also where dealing with /certs to become "/certs"
                        elif stripped in {"."} or any(
                            c in stripped for c in [".", "-", "_", "/"]
                        ):
                            styled_vars[var_name] = DoubleQuotedScalarString(stripped)

                        # quote numeric-looking values for example:

                        # variables:
                        #   GIT_DEPTH: '1'

                        # becomes

                        # variables:
                        #   GIT_DEPTH: "1"
                        elif (
                            stripped.isdigit() or stripped.replace(".", "", 1).isdigit()
                        ):
                            styled_vars[var_name] = DoubleQuotedScalarString(stripped)

                        # leave everything else plain
                        else:
                            styled_vars[var_name] = stripped

                    else:
                        styled_vars[var_name] = style_scalars(
                            var_val, quote_keys=quote_keys, parent_key=parent_key
                        )
                styled[k] = styled_vars

            # 7. in the environment block, preserve both name and action

            #   environment:
            #       name: $OPENTOFU_STATE_NAME/apply
            #       action: stop
            elif k == "environment" and isinstance(v, dict):
                styled_env = {}
                for env_key, env_val in v.items():
                    if isinstance(env_val, str):
                        styled_env[env_key] = DoubleQuotedScalarString(env_val)
                    else:
                        styled_env[env_key] = style_scalars(
                            env_val, quote_keys=quote_keys, parent_key=k
                        )
                styled[k] = styled_env

            # 8. quote values inside of id_tokens so things like sigstore in id_tokens becomes "sigstore"
            elif k == "id_tokens" and isinstance(v, dict):
                styled_tokens = {}
                for token_name, token_val in v.items():
                    if isinstance(token_val, dict):
                        styled_tokens[token_name] = {
                            tk: (
                                DoubleQuotedScalarString(tv)
                                if isinstance(tv, str)
                                else tv
                            )
                            for tk, tv in token_val.items()
                        }
                    else:
                        styled_tokens[token_name] = token_val
                styled[k] = styled_tokens

            # 9. everything else, recurse normally
            else:
                styled[k] = style_scalars(v, quote_keys=quote_keys, parent_key=k)

        # reinsert any keys skipped during iteration ie dependencies
        for k, v in obj.items():
            if k not in styled:
                styled[k] = v

        return styled

    # flatten nested lists, preserve literal strings (>-)
    elif isinstance(obj, list):
        flat: list[Any] = []
        for i in obj:
            flat.extend(i if isinstance(i, list) else [i])

        styled_list = []
        for item in flat:
            if isinstance(item, str):
                # multi-line shell to literal block
                if "\n" in item:
                    styled_list.append(LiteralScalarString(item))

                # if we are in a shell-life section, format line nicely
                elif parent_key in {"script", "before_script", "after_script"}:
                    stripped_item = item.strip()

                    # keep raw shell assignements in plain text (avoid escaping inside quotes)
                    if "=" in stripped_item.split()[0] and not stripped_item.startswith(
                        "$"
                    ):
                        styled_list.append(stripped_item)  # type: ignore[arg-type]
                    else:
                        styled_list.append(
                            make_scalar_string(
                                item if len(item) > 10 else stripped_item
                            )
                        )

                else:
                    styled_list.append(
                        style_scalars(
                            item, quote_keys=quote_keys, parent_key=parent_key
                        )
                    )
            else:
                styled_list.append(
                    style_scalars(item, quote_keys=quote_keys, parent_key=parent_key)
                )
        return styled_list or obj

    # handle plain strings
    elif isinstance(obj, str):
        stripped = obj.strip()

        # 1. don't quote variables or expressions
        if stripped.startswith("$") or stripped.startswith("${"):
            return stripped

        # 2. no quotes for "."
        if stripped == ".":
            return stripped

        # 3. don't quote well-known CI/CD keywords or literal identifiers
        UNQUOTED_KEYWORDS = {
            "test",
            "build",
            "deploy",
            "never",
            "always",
            "true",
            "false",
            "on_success",
            "on_failure",
            "manual",
            "cobertura",  # :white_check_mark: coverage format
            "sigstore",
        }
        if stripped in UNQUOTED_KEYWORDS:
            return stripped

        # 4
        if "/" in stripped or "." in stripped or "-" in stripped or "_" in stripped:
            return DoubleQuotedScalarString(stripped)

        # 5. everything else stays plain
        return stripped

    return obj
