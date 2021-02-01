from collections import OrderedDict

import pytest
from golang_code_gen.go_file import (
    to_line_comment,
    to_block_comment,
    Struct,
    Field,
    fields_to_struct,
    Comment,
    ImportStatement,
    to_import_statement,
)


class TestImport:
    def test_constructor(self):
        _import = ImportStatement("fmt")
        assert str(_import) == "import fmt"

    def test_multi_constructor(self):
        _import = ImportStatement(["fmt", "time"])
        assert (
            str(_import)
            == """\
import (
	"fmt"
	"time"
)"""
        )

    def test_to_import_statement(self):
        _import = to_import_statement("fmt")
        assert str(_import) == "import fmt"

    def test_multi_to_import_statement(self):
        _import = to_import_statement(["fmt", "time"])
        assert (
            str(_import)
            == """\
import (
	"fmt"
	"time"
)"""
        )


class TestComment:
    def test_constructor(self):
        comment = Comment("Hello, world!")
        assert comment.text == "// Hello, world!"

    def test_to_line_comment(self):
        comment = to_line_comment("This is a comment")
        assert comment.text == "// This is a comment"

    def test_multi_to_line_comment(self):
        comment = to_line_comment("I have eaten\nthe plums\nthat were in\nthe icebox")
        assert (
            comment.text
            == """\
// I have eaten
// the plums
// that were in
// the icebox"""
        )

    def test_block_comment(self):
        comment = to_block_comment("This is a comment")
        assert (
            str(comment)
            == """\
/*
This is a comment
*/"""
        )

    def test_multi_line_block_comment(self):
        comment = to_block_comment("I have eaten\nthe plums\nthat were in\nthe icebox")
        assert (
            str(comment)
            == """\
/*
I have eaten
the plums
that were in
the icebox
*/"""
        )


class TestStructAndField:
    # Normally you'd want your unit tests to cover a single class
    # However, the Field class is tightly coupled to Structs, so they're tested together

    # Please note: The examples tested against have tabs instead of spaces
    def test_empty(self):
        struct = Struct("Sentinel")
        assert (
            str(struct)
            == """\
type Sentinel struct {
}"""
        )

    def test_single_field(self):
        fields = [Field("X", "int")]
        struct = fields_to_struct("SingleField", fields)
        assert (
            str(struct)
            == """\
type SingleField struct {
	X int
}"""
        )

    def test_single_tuple(self):
        fields = [("X", "int")]
        struct = fields_to_struct("SingleField", fields)
        assert (
            str(struct)
            == """\
type SingleField struct {
	X int
}"""
        )

    def test_with_multiple_fields(self):
        fields = [Field("Field1", "string"), Field("X", "time.Time")]
        struct = fields_to_struct("MultipleFields", fields)
        assert (
            str(struct)
            == """\
type MultipleFields struct {
	Field1 string
	X      time.Time
}"""
        )

    def test_annotated(self):
        fields = [
            Field("Text", "string", 'json:"text"'),
            Field("MoreText", "string", 'json:"more_text"'),
            Field("ReallyLongNameThatIsNotAnnotated", "int"),
        ]
        struct = fields_to_struct("Annotated", fields)
        assert (
            str(struct)
            == """\
type Annotated struct {
	Text                             string `json:"text"`
	MoreText                         string `json:"more_text"`
	ReallyLongNameThatIsNotAnnotated int
}"""
        )

    # Todo: Talk to people about testing.
    #   Should you test unintended uses of the API?
    def test_from_dict(self):
        # Please, do not use the API like this
        fields = [OrderedDict({"X": None, "int": None})]
        struct = fields_to_struct("Oof", fields)
        assert (
            str(struct)
            == """\
type Oof struct {
	X int
}"""
        )


if __name__ == "__main__":
    pytest.main()
