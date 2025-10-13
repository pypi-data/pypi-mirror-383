from typing import TYPE_CHECKING

import jinja2.exceptions
from jinja2 import Environment
from pydantic import BaseModel, Field

from trano.elements.types import Axis, ContainerTypes

if TYPE_CHECKING:
    from trano.elements.base import BaseElement


class Figure(BaseModel):
    right_axis: Axis = Field(default=Axis(lines=[], label=""))
    left_axis: Axis = Field(default=Axis(lines=[], label=""))

    def render_key(self, element: "BaseElement") -> "Figure":
        environment = Environment(autoescape=True)
        for axis in self.right_axis.lines + self.left_axis.lines:
            template = environment.from_string(axis.template)
            try:
                axis.key = template.render(element=element)
            except jinja2.exceptions.UndefinedError:
                continue

        return self

    def modify_key_based_on_container(
        self, container: ContainerTypes, include_container: bool = True
    ) -> "Figure":
        if not include_container:
            return self
        for axis in self.right_axis.lines + self.left_axis.lines:
            if axis.key is not None:
                axis.key = f"building.{container}1.{axis.key}"
        return self


class NamedFigure(Figure):
    name: str
