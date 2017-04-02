#!/usr/bin/env python

from django.core.management.base import BaseCommand

from electiondata.ed.dataloader import loaddata


class Command(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument('--type',
                            dest='datatype',
                            default=None)
        
        parser.add_argument('path', nargs='?', type=str)

    def handle(self, *args, **kwargs):
        loaddata(kwargs['datatype'], kwargs['path'])
