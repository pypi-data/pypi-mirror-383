"""Framework detector modules."""

from .base import BaseDetector
from .java_spring import SpringBootDetector
from .java_micronaut import MicronautDetector
from .python_fastapi import FastAPIDetector
from .python_flask import FlaskDetector
from .dotnet import DotNetDetector

__all__ = [
    "BaseDetector",
    "SpringBootDetector",
    "MicronautDetector",
    "FastAPIDetector",
    "FlaskDetector",
    "DotNetDetector",
]

