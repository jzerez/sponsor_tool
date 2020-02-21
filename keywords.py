"""
Spring 2020
Jonathan Zerez

This file contains definitions for keywords to look for, and the categories that
those keywords belong to. The categories are:
- educational keywords: suggest the company supports educational development

- electrical keywords: suggest the company deals with electronic stuff

- mechanical keywords: suggest the company deals with mechanical stuff
"""
categories = {
    'edu_keywords' : ['educational', 'education', 'learning',
                      'sponsor', 'sponsorship', 'student',
                      'foster', 'students', 'university',
                      'college', 'school', 'donation',
                      'partnership', 'support', 'donations'],

    'electrical_keywords' : ['PCB', 'circuit', 'connector',
                             'electronics', 'battery', 'batteries',
                             'cable'],

    'mechanical_keywords' : ['machining', 'tolerance', 'precise',
                             'fabrication', 'industrial', 'industry',
                             'milling', 'mill', 'lathe', 'CNC', 'machine',
                             'shop', 'stock', 'prototype', 'rapid',
                             '3D Printing', 'CAD', 'CAM', 'CAD/CAM', 'CAM/CAD',
                             'manufacture', 'manufacturing', 'Additive',
                             '5-axis', '3-axis', 'axis', 'SLS', 'Weld',
                             'Welding']
}

# Inverse the dictionary:
# each keyword should be a key whose value is the category it belongs to
keywords = {}
for category in categories.keys():
    words = categories[category]
    for word in words:
        keywords[word] = category
