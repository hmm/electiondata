#!/usr/bin/env python


from django.core.management.base import BaseCommand

from electiondata.ed.xmlparser import *

class Command(BaseCommand):

    parsers = dict(
        areas=AreaParser,
        nominators=NominatorParser,
        candidates=CandidateParser,
    )
    

    def add_arguments(self, parser):
        parser.add_argument('xmltype', nargs='?', choices = self.parsers.keys(), type=str)
        parser.add_argument('xmlpath', nargs='?', type=str)

    def handle(self, *args, **kwargs):
        parser = self.parsers[kwargs['xmltype']]

        parser(kwargs['xmlpath'])

