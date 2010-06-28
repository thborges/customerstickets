#!/usr/bin/env python
# -*- coding: iso-8859-1 -*-

from setuptools import find_packages, setup

setup(
    name = 'TracCustomersTickets', version = '0.1',
    packages = find_packages(exclude=['*.tests*']),
    entry_points = """
        [trac.plugins]
        customerstickets = customerstickets
    """,
    package_data={'customerstickets': ['templates/*.html']},
)
