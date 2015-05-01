#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import zipfile

from lxml import etree

from models import *

class XMLParser(object):

    def __init__(self, pathname):
        self.initialize()
        with self.getsource(pathname) as source:
            context = etree.iterparse(source, events=('start', 'end',))

            for event, element in context:
                methodname = "%s_%s" % (event, element.tag.replace('-', '_'))
                handler = getattr(self, methodname, self.defaulthandler)
                try:
                    handler(event, element)
                except:
                    print "Error data:", event, element.tag, element.attrib
                    raise
        self.finalize()

    def initialize(self):
        pass

    def finalize(self):
        pass

    def getsource(self, pathname):
        try:
            zip = zipfile.ZipFile(pathname)
            return zip.open(zip.namelist()[0])
        except zipfile.BadZipfile:
            return file(pathname)

    def debug_event(self, event, element):
        print event, element.tag, element.attrib        

    def defaulthandler(self, event, element):
        self.debug_event(event, element)
        raise Exception("Undefined handler %s_%s" % (event, element.tag))


class AreaParser(XMLParser):
    """ parser for alu_maa xml file """

    def initialize(self):
        self.areatypes = []
        self.areas = []
        self.current_area = None
        self.current_areatype = None
        self.joined_areas = []

    def finalize(self):
        print "Joined areas:"
        for (municipality, parent_id, joined_id) in self.joined_areas:
            parent = municipality.children.get(identifier=parent_id)
            joined = municipality.children.get(identifier=joined_id)
            print "%s: %s -> %s" % (municipality, parent, joined)
            joined.joined_to = parent

            joined.save()

    def start_data(self, event, element):
        pass

    def end_data(self, event, element):
        pass

    def start_election(self, event, element):
        pass

    def end_election(self, event, element):
        pass

    def start_country_data(self, event, element):
        self.start_electoral_area(event, element)

    def end_country_data(self, event, element):
        self.end_electoral_area(event, element)

    def start_electoral_area(self, event, element):
        self.areatypes.append(element)
        self.current_areatype = element
        if element.attrib.get('parent-area-identifier'):
            self.joined_areas.append((self.current_area, element.attrib.get('identifier'), element.attrib.get('parent-area-identifier')))


    def end_electoral_area(self, event, element):
        self.areatypes.pop()
        self.areas.pop()
        if self.areas:
            self.current_area = self.areas[-1]
        else:
            self.current_area = None

    def start_area_data(self, event, element):
        if self.current_areatype.attrib.get('area-type') == 'M':
            idnum = 1
        elif self.current_areatype.attrib.get('area-type') == 'V':
            idnum = 100 + int(self.current_areatype.attrib.get('identifier'))
        elif self.current_areatype.attrib.get('area-type') == 'K':
            idnum = 1000 + int(self.current_areatype.attrib.get('identifier'))
        elif self.current_areatype.attrib.get('area-type') == 'A':
            id_str = self.current_areatype.attrib.get('identifier')
            try:
                identifier = int(id_str)
            except ValueError:
                # 0123A type identifier
                identifier = int(id_str[:-1]) * 10 + ord(id_str[-1]) - ord('@')
            idnum = self.current_area.id*1000 + identifier
        
        (area, created) = Area.objects.update_or_create(
            id = idnum,
            defaults = dict(
                areatype = self.current_areatype.attrib.get('area-type'),
                identifier = self.current_areatype.attrib.get('identifier'),
                abbreviation = element.attrib.get('abbreviation'),
                name = element.attrib.get('name'),
                is_city = element.attrib.get('is-city', False),
                polling_districts = element.attrib.get('number-of-polling-districts'),
                parent = self.current_area
            )
        )
        print area
        self.areas.append(area)
        self.current_area = area

    def end_area_data(self, event, element):
        pass

    def start_basic_voting_data(self, event, element):
        self.current_voting_data = element
        if int(element.attrib.get('number-to-be-elected')):
            self.current_area.number_to_be_elected = int(element.attrib.get('number-to-be-elected'))
            self.current_area.save()

    def end_basic_voting_data(self, event, element):
        pass

    def start_supplemental_voting_data(self, event, element):
        (votingdata, created) = VotingData.objects.update_or_create(
            id = self.current_area.id,
            area = self.current_area,
            defaults = dict(
                areatxt = self.current_area.gentxt(),

                eligible_total = self.current_voting_data.attrib.get('eligible-voters-total'),
                eligible_men = self.current_voting_data.attrib.get('eligible-voters-men'),
                eligible_women = self.current_voting_data.attrib.get('eligible-voters-women'),

                eligible_finland_total = self.current_voting_data.attrib.get('eligible-voters-living-in-finland-total'),
                eligible_finland_men = self.current_voting_data.attrib.get('eligible-voters-living-in-finland-men'),
                eligible_finland_women = self.current_voting_data.attrib.get('eligible-voters-living-in-finland-women'),

                total_turnout = self.current_voting_data.attrib.get('total-voting-turnout'),
                advance_turnout = self.current_voting_data.attrib.get('advance-voting-turnout'),
                electionday_turnout = self.current_voting_data.attrib.get('election-day-voting-turnout'),

                total_finland_turnout = element.attrib.get('total-voting-turnout-living-in-finland'),
                advance_finland_turnout = element.attrib.get('advance-voting-turnout-living-in-finland'),
                electionday_finland_turnout = element.attrib.get('election-day-voting-turnout-living-in-finland'),
                
                total_abroad_turnout = element.attrib.get('total-voting-turnout-abroad'),
                advance_abroad_turnout = element.attrib.get('advance-voting-turnout-abroad'),
                electionday_abroad_turnout = element.attrib.get('election-day-voting-turnout-abroad'),
            
                total_votes = element.attrib.get('total-votes'),
                advance_votes = element.attrib.get('advance-votes'),
                electionday_votes = element.attrib.get('election-day-votes'),
            
                total_males_votes = element.attrib.get('total-votes-males'),
                advance_males_votes = element.attrib.get('advance-votes-males'),
                electionday_males_votes = element.attrib.get('election-day-votes-males'),
            
                total_finland_votes = element.attrib.get('total-votes-living-in-finland'),
                advance_finland_votes = element.attrib.get('advance-votes-living-in-finland'),
                electionday_finland_votes = element.attrib.get('election-day-votes-living-in-finland'),
            
                total_finland_males_votes = element.attrib.get('total-votes-living-in-finland-males'),
                advance_finland_males_votes = element.attrib.get('advance-votes-living-in-finland-males'),
                electionday_finland_males_votes = element.attrib.get('election-day-votes-living-in-finland-males'),

                total_abroad_votes = element.attrib.get('total-votes-abroad'),
                advance_abroad_votes = element.attrib.get('advance-votes-abroad'),
                electionday_abroad_votes = element.attrib.get('election-day-votes-abroad'),
            
                total_abroad_males_votes = element.attrib.get('total-votes-abroad-males'),
                advance_abroad_males_votes = element.attrib.get('advance-votes-abroad-males'),
                electionday_abroad_males_votes = element.attrib.get('election-day-votes-abroad-males'),

                total_approved_votes = element.attrib.get('approved-total-votes'),
                advance_approved_votes = element.attrib.get('approved-advance-votes'),
                electionday_approved_votes = element.attrib.get('approved-election-day-votes'),

                total_invalid_votes = element.attrib.get('invalid-total-votes'),
                advance_invalid_votes = element.attrib.get('invalid-advance-votes'),
                electionday_invalid_votes = element.attrib.get('invalid-election-day-votes')
            )
        )


    def end_supplemental_voting_data(self, event, element):
        pass

    def start_comparison_election(self, event, element):
        (comparison, created) = ComparisonElection.objects.get_or_create(
            abbreviation = element.attrib.get('election-event-name-abbreviation')
        )
        (votingcomparison, created) = VotingDataComparison.objects.update_or_create(
            comparison = comparison,
            area = self.current_area,
            defaults = dict(
                areatxt = self.current_area.gentxt(),
                comparisontxt = comparison.gentxt(),
                eligible_total = self.current_voting_data.attrib.get('eligible-voters-total'),
                eligible_men = self.current_voting_data.attrib.get('eligible-voters-men'),
                eligible_women = self.current_voting_data.attrib.get('eligible-voters-women'),

                eligible_finland_total = self.current_voting_data.attrib.get('eligible-voters-living-in-finland-total'),
                eligible_finland_men = self.current_voting_data.attrib.get('eligible-voters-living-in-finland-men'),
                eligible_finland_women = self.current_voting_data.attrib.get('eligible-voters-living-in-finland-women'),

                total_turnout = self.current_voting_data.attrib.get('total-voting-turnout'),
                advance_turnout = self.current_voting_data.attrib.get('advance-voting-turnout'),
                electionday_turnout = self.current_voting_data.attrib.get('election-day-voting-turnout'),

                total_approved_votes = element.attrib.get('approved-votes-total'),
                total_invalid_votes = element.attrib.get('invalid-votes-total'),
                
                number_to_be_elected = element.attrib.get('number-to-be-elected')
                
            )
        )
            
        

    def end_comparison_election(self, event, element):
        pass


class ResultsParser(XMLParser):

    def start_data(self, event, element):
        pass

    def end_data(self, event, element):
        pass

    def start_election(self, event, element):
        pass

    def end_election(self, event, element):
        pass

    def start_country_data(self, event, element):
        self.current_area = Area.objects.get(id = 1)

    def end_country_data(self, event, element):
        pass

    def start_electoral_area(self, event, element):
        if element.attrib.get('area-type') in ['V', 'K']:
            self.current_area = Area.objects.get(
                areatype = element.attrib.get('area-type'),
                identifier = element.attrib.get('identifier'),
            )
        elif element.attrib.get('area-type') == 'A':
            if self.current_area.areatype == 'A':
                self.current_area = self.current_area.parent.children.get(
                    identifier = element.attrib.get('identifier')
                )
            else:
                self.current_area = self.current_area.children.get(
                    identifier = element.attrib.get('identifier')
                )
        else:
            self.current_area = None
        print self.current_area


    def end_electoral_area(self, event, element):
        pass

    def start_area_data(self, event, element):
        pass

    def end_area_data(self, event, element):
        pass

    def get_nominator_id(self, element):
        if element.attrib.get('standard-party-number') != '99':
            return int(element.attrib.get('standard-party-number'))
        else:
            return 990000 + int(element.attrib.get('party-identifier'))


class NominatorParser(ResultsParser):

    def start_nominator(self, event, element):
        if self.current_area.areatype in ['M', 'V']:
            (self.current_nominator, created) = Nominator.objects.get_or_create(
                id = self.get_nominator_id(element),
                defaults = dict(
                    identifier = element.attrib.get('party-identifier'),
                    abbreviation = element.attrib.get('abbreviation'),
                    name = element.attrib.get('name'),
                    total_votes = element.attrib.get('total-votes'),
                    advance_votes = element.attrib.get('advance-votes'),
                    electionday_votes = element.attrib.get('election-day-votes'),
                    total_pct = element.attrib.get('total-votes-percent'),
                    advance_pct = element.attrib.get('advance-votes-percent'),
                    electionday_pct = element.attrib.get('election-day-votes-percent'),
                    seats = element.attrib.get('seats')
                )
            )
            if created:
                print self.current_nominator
        else:
            self.current_nominator = Nominator.objects.get(
                id = self.get_nominator_id(element)
            )


        if self.current_area.areatype == 'V':
            if element.attrib.get('electoral-alliance-name'):
                (alliance, created) = Alliance.objects.update_or_create(
                    id = self.current_area.id * 1000 + int(element.attrib.get('electoral-alliance-number')),
                    defaults = dict(
                        name = element.attrib.get('electoral-alliance-name'),
                        area = self.current_area
                    )
                )
                (alliancenominator, created) = AllianceNominator.objects.get_or_create(
                    alliance = alliance,
                    nominator = self.current_nominator
                )
                if created:
                    print alliance, alliancenominator

        (nominatorresults, created) = NominatorResults.objects.update_or_create(
            nominator = self.current_nominator,
            area = self.current_area,
            defaults = dict(
                areatxt = self.current_area.gentxt(),
                nominatortxt = self.current_nominator.gentxt(),
                total_votes = element.attrib.get('total-votes'),
                advance_votes = element.attrib.get('advance-votes'),
                electionday_votes = element.attrib.get('election-day-votes'),
                total_pct = element.attrib.get('total-votes-percent'),
                advance_pct = element.attrib.get('advance-votes-percent'),
                electionday_pct = element.attrib.get('election-day-votes-percent'),
                seats = element.attrib.get('seats')
            )
        )

    def end_nominator(self, event, element):
        pass
        
    def start_comparison_election(self, event, element):
        pass

    def end_comparison_election(self, event, element):
        pass


class CandidateParser(ResultsParser):
    

    def start_nominator(self, event, element):
        self.current_nominator = Nominator.objects.get(
            id = self.get_nominator_id(element)
        )
            

    def end_nominator(self, event, element):
        pass
        
    def start_candidate(self, event, element):
        if self.current_area.areatype == 'V':
            try:
                home_municipality = Area.objects.get(
                    areatype='K',
                    identifier=element.attrib.get('home-municipality-code')
                )
            except Area.DoesNotExist:
                home_municipality = None

            (candidate, created) = Candidate.objects.update_or_create(
                id = self.current_area.id * 1000 + int(element.attrib.get('candidate-number')),
                defaults = dict(
                    candidate_number = element.attrib.get('candidate-number'),
                    area = self.current_area,
                    areatxt = self.current_area.gentxt(),
                    nominator = self.current_nominator,
                    nominatortxt = self.current_nominator.gentxt(),
                    first_name = element.attrib.get('first-name'),
                    last_name = element.attrib.get('last-name'),
                    gender = element.attrib.get('gender'),
                    age = element.attrib.get('age'),
                    occupation = element.attrib.get('occupation'),
                    language = element.attrib.get('language'),
                    home_municipality = home_municipality,
                    home_municipality_name = element.attrib.get('home-municipality'),
                    total_votes = element.attrib.get('total-votes'),
                    advance_votes = element.attrib.get('advance-votes'),
                    electionday_votes = element.attrib.get('election-day-votes'),
                    total_pct = element.attrib.get('total-vote-percent'),
                    advance_pct = element.attrib.get('advance-votes-percent'),
                    electionday_pct = element.attrib.get('election-day-percent'),
                    elected_information = element.attrib.get('elected-information'),
                    comparative_index = element.attrib.get('comparative-index'),
                    position = element.attrib.get('position')
                )
            )
            self.current_candidate = candidate
            if created:
                print candidate
        elif self.current_area.areatype == 'K':
            self.current_candidate = Candidate.objects.get(
                id = self.current_area.parent.id * 1000 + int(element.attrib.get('candidate-number')))
        else:
            self.current_candidate = Candidate.objects.get(
                id = self.current_area.parent.parent.id * 1000 + int(element.attrib.get('candidate-number')))
            
        (candidateresults, created) = CandidateResults.objects.update_or_create(
            candidate = self.current_candidate,
            nominator = self.current_candidate.nominator,
            area = self.current_area,
            defaults = dict(
                areatxt = self.current_area.gentxt(),
                candidatetxt = self.current_candidate.gentxt(),
                nominatortxt = self.current_candidate.nominator.gentxt(),
                total_votes = element.attrib.get('total-votes'),
                advance_votes = element.attrib.get('advance-votes'),
                electionday_votes = element.attrib.get('election-day-votes'),
                total_pct = element.attrib.get('total-vote-percent'),
                advance_pct = element.attrib.get('advance-votes-percent'),
                electionday_pct = element.attrib.get('election-day-percent'),
                elected_information = element.attrib.get('elected-information'),
                comparative_index = element.attrib.get('comparative-index'),
                position = element.attrib.get('position')
            )
        )
                

    def end_candidate(self, event, element):
        pass

    def start_membership(self, event, element):
        (membership, created) = Membership.objects.get_or_create(
            title = element.attrib.get('title')
        )
        (cm, created) = CandidateMembership.objects.get_or_create(
            membership = membership,
            candidate = self.current_candidate
        )

    def end_membership(self, event, element):
        pass

    def start_comparison_election(self, event, element):
        pass

    def end_comparison_election(self, event, element):
        pass
