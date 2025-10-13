from django.http import HttpRequest

from pydantic import BaseModel
from .base import Text
from typing import Literal


type TextAlign = Literal["left"] | Literal["center"] | Literal["right"]


class TitleContext(BaseModel):
    title: str
    text_size: str
    align: TextAlign


class Title(Text):
    template_name: str = "text/title"
    title: str
    text_size: str = "3xl"
    align: TextAlign = "left"
    

    def update_title(self, new_title: str) -> None:
        self.title = new_title

    def _build(self, request: HttpRequest) -> TitleContext:
        return TitleContext(
            title=self.title, text_size=self.text_size, align=self.align
        )


class SubTitle(Title):
    text_size: str = "2xl"
