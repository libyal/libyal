#!/usr/bin/env python3
# pylint: disable=invalid-name
"""Script to format autotools m4 scripts."""

import argparse
import json
import logging
import os
import sys

import ply.lex as lex
import ply.yacc as yacc

from typing import Dict, Any, List


class AutotoolsM4Lexer:
    """Autotools m4 script lexer."""

    states = (
        ("macroarg", "exclusive"),
        ("quoted", "exclusive"),
    )

    tokens = [
        "COMMA",
        "DNL_COMMENT",
        "LBRACKET",
        "LPAREN",
        "MACRO_NAME",
        "RBRACKET",
        "RPAREN",
        "TEXT",
    ]

    def __init__(self):
        """Initializes a lexer."""
        super().__init__()
        self.paren_depth = 0
        self.bracket_depth = 0
        self.lexer = lex.lex(module=self)

    def input(self, data: str):
        """Sets the input."""
        self.paren_depth = 0
        self.bracket_depth = 0
        self.lexer.lineno = 1
        self.lexer.input(data)

    def token(self):
        """Retrieves a token."""
        return self.lexer.token()

    def t_ANY_dnl(self, token):
        r"dnl[^\n]*\n"
        token.lexer.lineno += 1
        token.type = "DNL_COMMENT"
        token.value = token.value.rstrip("\n")
        return token

    def t_ANY_newline(self, token):
        r"\n+"
        token.lexer.lineno += len(token.value)
        token.type = "TEXT"
        return token

    def t_MACRO_NAME(self, token):
        r"[a-zA-Z_][a-zA-Z0-9_]*"
        try:
            next_char = token.lexer.lexdata[token.lexer.lexpos]
        except IndexError:
            next_char = ""
        if next_char == "(":
            return token
        token.type = "TEXT"
        return token

    def t_LBRACKET(self, token):
        r"\["
        self.bracket_depth = 1
        token.lexer.begin("quoted")
        return token

    def t_LPAREN(self, token):
        r"\("
        self.paren_depth = 1
        token.lexer.begin("macroarg")
        return token

    t_ignore = ""
    t_TEXT = r"[^\[\(\n]+"

    def t_macroarg_MACRO_NAME(self, token):
        r"[a-zA-Z_][a-zA-Z0-9_]*"
        try:
            next_char = token.lexer.lexdata[token.lexer.lexpos]
        except IndexError:
            next_char = ""

        if next_char == "(":
            return token

        token.type = "TEXT"
        return token

    def t_macroarg_LPAREN(self, token):
        r"\("
        self.paren_depth += 1
        token.type = "TEXT"
        return token

    def t_macroarg_RPAREN(self, token):
        r"\)"
        self.paren_depth -= 1
        if self.paren_depth == 0:
            token.lexer.begin("INITIAL")
            return token

        token.type = "TEXT"
        return token

    def t_macroarg_COMMA(self, token):
        r","
        if self.paren_depth == 1:
            return token

        token.type = "TEXT"
        return token

    def t_macroarg_LBRACKET(self, token):
        r"\["
        self.bracket_depth = 1
        token.lexer.begin("quoted")
        return token

    t_macroarg_ignore = ""

    def t_macroarg_TEXT(self, token):
        r"(?:(?!dnl)[^\[\(\),\n\t ]+)+|[\t ]+"
        return token

    def t_quoted_LBRACKET(self, token):
        r"\["
        self.bracket_depth += 1
        token.type = "TEXT"
        return token

    def t_quoted_RBRACKET(self, token):
        r"\]"
        self.bracket_depth -= 1
        if self.bracket_depth == 0:
            if self.paren_depth > 0:
                token.lexer.begin("macroarg")
            else:
                token.lexer.begin("INITIAL")
            return token

        token.type = "TEXT"
        return token

    t_quoted_ignore = ""

    def t_quoted_TEXT(self, token):
        r"(?:(?!dnl)[^\[\]\n\t ]+)+|[\t ]+"
        return token

    def t_ANY_error(self, token):
        logging.error(
            f"Unsupported character: '{token.value:s}' on line: {token.lineno:d}",
        )
        token.lexer.skip(1)


class AutotoolsM4Parser:
    """Autotools m4 script parser."""

    def __init__(self):
        """Initializes a parser."""
        super().__init__()
        # Note that self.tokens must be set before self.parser
        self.tokens = AutotoolsM4Lexer.tokens
        self.parser = yacc.yacc(module=self, debug=False, write_tables=False)

    def parse(self, data: str) -> Dict[str, Any]:
        """Parses a string."""
        lexer_instance = AutotoolsM4Lexer()
        return self.parser.parse(data, lexer=lexer_instance.lexer)

    def parse_file(self, file_path: str, encoding: str = "utf-8") -> Dict[str, Any]:
        """Parses a file."""
        with open(file_path, encoding=encoding) as file_object:
            file_content = file_object.read()
        return self.parse(file_content)

    def p_script(self, p):
        """script : expressions_opt"""
        p[0] = {"type": "Script", "body": p[1]}

    def p_expressions_opt(self, p):
        """expressions_opt : expressions
        | empty"""
        p[0] = p[1] if p[1] is not None else []

    def p_expressions(self, p):
        """expressions : expressions expression
        | expression"""
        if len(p) == 3:
            p[0] = p[1] + [p[2]]
        else:
            p[0] = [p[1]]

    def p_expression(self, p):
        """expression : macro_call
        | quoted_block
        | TEXT
        | DNL_COMMENT"""
        if isinstance(p[1], dict):
            p[0] = p[1]
        elif p.slice[1].type == "DNL_COMMENT":
            p[0] = {"type": "CommentBlock", "value": p[1]}
        else:
            p[0] = {"type": "TextLiteral", "value": p[1]}

    def p_macro_call(self, p):
        """macro_call : MACRO_NAME LPAREN arguments_opt RPAREN"""
        p[0] = {"type": "MacroCall", "name": p[1], "arguments": p[3]}

    def p_arguments_opt(self, p):
        """arguments_opt : arguments
        | empty"""
        p[0] = p[1] if p[1] is not None else [[]]

    def p_arguments(self, p):
        """arguments : arguments COMMA argument
        | argument"""
        if len(p) == 4:
            p[0] = p[1] + [p[3]]
        else:
            p[0] = [p[1]]

    def p_argument(self, p):
        """argument : expressions_opt"""
        p[0] = p[1]

    def p_quoted_block(self, p):
        """quoted_block : LBRACKET expressions_opt RBRACKET"""
        p[0] = {"type": "QuotedBlock", "body": p[2]}

    def p_empty(self, p):
        "empty :"
        p[0] = None

    def p_error(self, p):
        if not p:
            message = "Unexpected end of file"
        else:
            message = (
                f"Syntax error at token: '{p.value:s}' (Type: {p.type:s}) on line: "
                f"{p.lineno:d}"
            )

        raise SyntaxError("Unexpected end of file")


class AutotoolsM4Generator:
    """Generates autotools m4 script from an abstract syntax tree."""

    @staticmethod
    def generate(node: Dict[str, Any]) -> str:
        """Generates m4 script."""
        if not node:
            return ""

        node_type = node.get("type")

        if node_type == "CommentBlock":
            comment = node.get("value", "")
            return f"{comment:s}\n"

        if node_type == "MacroCall":
            macro_name = node.get("name", "")
            ast_arguments: List[List[Dict[str, Any]]] = node.get("arguments", [])

            m4_arguments = []
            for ast_argument in ast_arguments:
                m4_argument = "".join(
                    AutotoolsM4Generator.generate(token) for token in ast_argument
                )
                m4_arguments.append(m4_argument)

            if not m4_arguments or (len(m4_arguments) == 1 and m4_arguments[0] == ""):
                return macro_name

            arguments_string = ",".join(m4_arguments)
            return f"{macro_name:s}({arguments_string:s})"

        if node_type == "Script":
            return "".join(
                AutotoolsM4Generator.generate(sub_node)
                for sub_node in node.get("body", [])
            )

        if node_type == "QuotedBlock":
            block_content = "".join(
                AutotoolsM4Generator.generate(sub_node)
                for sub_node in node.get("body", [])
            )
            return f"[{block_content:s}]"

        if node_type == "TextLiteral":
            value = node.get("value", "")
            return value

        return ""


def Main():
    """Entry point of console script to extract events.

    Returns:
      int: exit code that is provided to sys.exit().
    """
    argument_parser = argparse.ArgumentParser(
        description="Formats autotools m4 scripts."
    )
    argument_parser.add_argument(
        "-f",
        "--format",
        dest="output_format",
        action="store",
        metavar="FORMAT",
        choices=["json", "m4"],
        default="m4",
        help="output format.",
    )
    argument_parser.add_argument(
        "-i",
        "--in-place",
        "--in_place",
        dest="in_place",
        action="store_true",
        default=False,
        help="in place update the m4 script file.",
    )
    argument_parser.add_argument("-o", "--output", help="Path to the output file.")
    argument_parser.add_argument(
        "m4_script_file",
        action="store",
        metavar="PATH",
        default="script.m4",
        help="path of the m4 script file.",
    )
    options = argument_parser.parse_args()

    if not options.m4_script_file:
        print("M4 script file missing.")
        print("")
        argument_parser.print_help()
        print("")
        return 1

    if not os.path.exists(options.m4_script_file):
        print(f"No such m4 script file: {options.m4_script_file:s}")
        print("")
        return 1

    try:
        compiler = AutotoolsM4Parser()
        abstract_syntax_tree = compiler.parse_file(options.m4_script_file)

        if options.in_place or options.output_format == "m4":
            output = AutotoolsM4Generator.generate(abstract_syntax_tree)
        else:
            output = json.dumps(abstract_syntax_tree, indent=4)

        if options.in_place:
            output_path = options.m4_script_file
        else:
            output_path = options.output

        if not output_path:
            print(output)
        else:
            with open(output_path, "w", encoding="utf-8") as file_object:
                file_object.write(output)

    except SyntaxError as exception:
        print(f"{exception!s}")
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(Main())
