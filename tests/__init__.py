# This file makes the tests directory a Python package 
# add modules to fix import errors under /tests, no module named 'card'
import card
import dice
import portfolio

__all__ = ["card", "dice", "portfolio"]
