from dataclasses import dataclass, field
from functools import partial
from typing import List, Sequence, Optional, Union, Tuple, Callable, ContextManager

from . import go_token as tok


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
        yield self.type
        if self.annotation:
            yield self.annotation

    def __len__(self):
        return len([attr for attr in self])

    # Todo: Clean up significantly
    def __str__(self):
        ljust_name = self.name.ljust(self.type_position, " ")
        name_and_type = ljust_name + self.type
        if not self.annotation:
            return name_and_type
        ljust_name_and_type = name_and_type.ljust(self.annotation_position, " ")
        return "%s`%s`" % (ljust_name_and_type, self.annotation)


InitToField = Union[Field, Union[Tuple[str, str]], Tuple[str, str, Optional[str]]]


def to_field(seq: InitToField) -> Field:
    """Field factory-function. The sequence's
    first position represents the field's name,
    second position represents the field's type,
    and optional third position represents the field's annotation.

    The purpose of this function is merely to prompt the user of alternate ways
    to instantiate a Field."""
    return Field(*seq)


_file_writer = partial(open, mode="w")

@dataclass
class GoFile:
    filename: str
    package: str
    sections: List[Element] = field(default_factory=list)
    _writer: Callable = _file_writer

    generated_code_message = "GENERATED CODE"

    def add_element(self, element):
        self.sections.append(element)

    def write(self):
        with self._writer(self.filename) as w:
            w.write(f"package {self.package}\n\n")
            for section in self.sections:
                w.write(f"{to_line_comment(self.generated_code_message)}\n")
                w.write(str(section))
                w.write("\n\n")


def _to_line_comment(text):
    lines = text.splitlines()
    return "\n".join([f"{tok.COMMENT} {line}" for line in lines])

_to_line_comment.__repr__ = "_to_line_comment"


def _to_block_comment(text):
    lines = text.splitlines()
    return "\n".join([tok.LCOMMENT, *lines, tok.RCOMMENT])


@dataclass
class Comment(Element):
    _text: str
    _builder: Callable[[str], str] = _to_line_comment

    def __post_init__(self):
        self.text = self._builder(self._text)

    def __str__(self):
        return self.text


def to_line_comment(text: str) -> Comment:
    return Comment(text, _to_line_comment)


def to_block_comment(text: str) -> Comment:
    return Comment(text, _to_block_comment)


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
            fields = "\n\t" + "\n\t".join(str(f) for f in self.fields)
        return f"type {self.name} struct {{{fields}\n}}"


def fields_to_struct(name: str, fields: Sequence[InitToField]) -> Struct:
    """Creates a new struct by copying the name, type, and annotation values from a
    sequence of fields"""
    struct = Struct(name)
    for f in fields:
        struct.fields.append(Field(*f))
    struct.format_fields()
    return struct


@dataclass
class ImportStatement(Element):
    packages: Union[str, Sequence[str]]

    def __post_init__(self):
        if isinstance(self.packages, str):
            self.packages = [self.packages]

    def __iter__(self):
        for p in self.packages:
            yield p

    def __len__(self):
        return len([package for package in self])

    def __str__(self):
        if len(self) == 1:
            return f"import {self.packages[0]}"
        packages = "\n\t" + "\n\t".join(f'"{p}"' for p in self.packages)
        return f"import ({packages}\n)"


def to_import_statement(packages: Union[str, Sequence[str]]) -> ImportStatement:
    return ImportStatement(packages)

def snake_case_to_pascal(string: str) -> str:
    """Returns a copy of a snake_case string converted to PascalCase"""
    return "".join(s.title() for s in string.split("_"))

def snake_case_to_camel(string: str) -> str:
    """Returns a copy of a snake_case string converted to camelCase"""
    pascal = snake_case_to_pascal(string)
    return pascal[0].lower() + pascal[1:]
