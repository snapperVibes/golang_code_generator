from dataclasses import dataclass, field
from typing import List, Sequence, Optional, Union, Tuple

import go_token as tok

# Backslashes aren't allowed in fstrings
_newline_tab = "\n\t"


class Element:
    """ Represents a section of the Go file"""


@dataclass
class Field(Element):
    name: str
    type: str
    annotation: Optional[str] = None

    def __post_init__(self):
        self._type_position = self._calculate_type_position()
        self._annotation_position = self._calculate_annotation_position()

    @property
    def type_position(self):
        return self._type_position

    @type_position.setter
    def type_position(self, value):
        if value < self._calculate_type_position():
            raise ValueError(
                "The assigned value must be greater than what the type position "
                "would be by default ({}<{})".format(
                    value, self._calculate_annotation_position()
                )
            )
        self._type_position = value

    @property
    def annotation_position(self):
        return self._annotation_position

    @annotation_position.setter
    def annotation_position(self, value):
        if value < self._calculate_annotation_position():
            raise ValueError(
                "The assigned value must be greater than what the annotation position "
                "would be by default ({}<{})".format(
                    value, self._calculate_annotation_position()
                )
            )
        self._annotation_position = value

    def _calculate_type_position(self):
        return len(self.name) + 1

    def _calculate_annotation_position(self):
        return self.type_position + len(self.type) + 1

    def __iter__(self):
        yield self.name
        for attr in (self.name, self.type, self.annotation):
            yield attr

    # Todo: Clean up significantly
    def __str__(self):
        ljust_name = self.name.ljust(self.type_position, " ")
        name_and_type = ljust_name + self.type
        if not self.annotation:
            return name_and_type
        ljust_name_and_type = name_and_type.ljust(self.annotation_position, " ")
        return "%s`%s`" % (ljust_name_and_type, self.annotation)


InitToField = Union[Field, Union[Tuple[str, str]], Tuple[str, str, Optional[str]]]


def field_from_sequence(seq: InitToField) -> Field:
    """Field factory-function. The sequence's
    first position represents the field's name,
    second position represents the field's type,
    and optional third position represents the field's annotation.

    The purpose of this function is merely to prompt the user of alternate ways
    to instantiate a Field."""
    return Field(*seq)


@dataclass
class GoFile:
    filename: str
    sections: List[Element] = field(default_factory=list)

    generated_code_message = "GENERATED CODE"

    def add_element(self, element):
        self.sections.append(element)

    # def add_comment(self, comment):
    #     if isinstance(comment, Comment):
    #         self.sections.append(comment)
    #     else:
    #         self.sections.append(to_line_comment(comment))


@dataclass
class Comment(Element):
    text: str

    def __str__(self):
        return self.text


@dataclass()
class Struct(Element):
    name: str

    def __post_init__(self):
        self.fields = []

    def format_fields(self):
        """ Sets the proper spacing for each field """
        max_type_pos = 0
        max_annotated_name_len = 0
        for f in self.fields:
            if f.type_position > max_type_pos:
                max_type_pos = f.type_position
            if not f.annotation:
                continue
            if len(f.type) > max_annotated_name_len:
                max_annotated_name_len = len(f.type)
        for f in self.fields:
            f.type_position = max_type_pos
            if not f.annotation:
                continue
            f.annotation_position = max_type_pos + max_annotated_name_len + 1

    def __str__(self):
        fields = ""
        if self.fields:
            fields = _newline_tab + _newline_tab.join(str(f) for f in self.fields)
        return f"type {self.name} struct {{{fields}\n}}"


def struct_from_fields(name: str, fields: Sequence[InitToField]) -> Struct:
    struct = Struct(name)
    for f in fields:
        if isinstance(f, Field):
            struct.fields.append(f)
        else:
            struct.fields.append(Field(*f))
    struct.format_fields()
    return struct


def to_line_comment(text: str) -> Comment:
    lines = text.splitlines()
    return Comment("\n".join([f"{tok.COMMENT} {line}" for line in lines]))


def to_block_comment(text: str) -> Comment:
    lines = text.splitlines()
    return Comment("\n".join([tok.LCOMMENT, *lines, tok.RCOMMENT]))


def dict_to_struct():
    pass


def class_to_struct():
    pass


def obj_to_struct():
    pass
