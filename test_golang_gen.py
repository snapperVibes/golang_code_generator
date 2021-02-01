import pytest
from go_file import (
    to_line_comment,
    to_block_comment,
    Struct,
    Field,
    struct_from_fields,
)


def test_single_line_line_comment():
    comment = to_line_comment("This is a comment")
    assert comment.text == "// This is a comment"


def test_multi_line_line_comment():
    comment = to_line_comment("I have eaten\nthe plums\nthat were in\nthe icebox")
    assert (
        comment.text
        == """\
// I have eaten
// the plums
// that were in
// the icebox"""
    )


def test_single_line_block_comment():
    comment = to_block_comment("This is a comment")
    assert (
        str(comment)
        == """\
/*
This is a comment
*/"""
    )


def test_multi_line_block_comment():
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


class TestStruct:
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
        struct = struct_from_fields("SingleField", fields)
        assert (
            str(struct)
            == """\
type SingleField struct {
	X int
}"""
        )

    def test_single_tuple(self):
        fields = [("X", "int")]
        struct = struct_from_fields("SingleField", fields)
        assert (
            str(struct)
            == """\
type SingleField struct {
	X int
}"""
        )

    def test_with_multiple_fields(self):
        fields = [Field("Field1", "string"), Field("X", "time.Time")]
        struct = struct_from_fields("MultipleFields", fields)
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
        struct = struct_from_fields("Annotated", fields)
        assert (
            str(struct)
            == """\
type Annotated struct {
	Text                             string `json:"text"`
	MoreText                         string `json:"more_text"`
	ReallyLongNameThatIsNotAnnotated int
}"""
        )


if __name__ == "__main__":
    pytest.main()
