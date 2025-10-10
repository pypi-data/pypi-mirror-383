from __future__ import annotations


from codegen.models import PredefinedFn, Program, expr, stmt

from sera.models import (
    Enum,
    Package,
    Schema,
)


def make_typescript_enums(schema: Schema, target_pkg: Package):
    """Make typescript enum for the schema"""
    enum_pkg = target_pkg.pkg("enums")

    for enum in schema.enums.values():
        make_enum(enum, enum_pkg)

    program = Program()
    for enum in schema.enums.values():
        program.import_(f"@.models.enums.{enum.get_tsmodule_name()}.{enum.name}", True)
        program.import_(
            f"@.models.enums.{enum.get_tsmodule_name()}.{enum.name}Label", True
        )
        program.import_(
            f"@.models.enums.{enum.get_tsmodule_name()}.{enum.name}Description", True
        )

    program.root(
        stmt.LineBreak(),
        stmt.TypescriptStatement(
            "export { "
            + ", ".join([enum.name for enum in schema.enums.values()])
            + ","
            + ", ".join([enum.name + "Label" for enum in schema.enums.values()])
            + ","
            + ", ".join([enum.name + "Description" for enum in schema.enums.values()])
            + "};"
        ),
    )
    enum_pkg.module("index").write(program)


def make_enum(enum: Enum, pkg: Package):
    program = Program()
    program.root(
        stmt.LineBreak(),
        lambda ast: ast.class_like("enum", enum.name)(
            *[
                stmt.DefEnumValueStatement(
                    name=value.name,
                    value=expr.ExprConstant(value.value),
                )
                for value in enum.values.values()
            ]
        ),
        stmt.LineBreak(),
        stmt.TypescriptStatement(
            f"export const {enum.name}Label = "
            + PredefinedFn.dict(
                [
                    (
                        expr.ExprConstant(value.value),
                        expr.ExprConstant(value.label.to_dict()),
                    )
                    for value in enum.values.values()
                ]
            ).to_typescript()
        ),
        stmt.LineBreak(),
        stmt.TypescriptStatement(
            f"export const {enum.name}Description = "
            + PredefinedFn.dict(
                [
                    (
                        expr.ExprConstant(value.value),
                        expr.ExprConstant(value.description.to_dict()),
                    )
                    for value in enum.values.values()
                ]
            ).to_typescript()
        ),
    )
    pkg.module(enum.get_tsmodule_name()).write(program)
