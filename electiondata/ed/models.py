# -*- coding: utf-8 -*-
from django.db import models


# Create your models here.


class PctField(models.DecimalField):

    def __init__(self, *args, **kwargs):
        kwargs['max_digits'] = 5
        kwargs['decimal_places'] = 1
        super(PctField, self).__init__(*args, **kwargs)


class XPctField(models.DecimalField):

    def __init__(self, *args, **kwargs):
        kwargs['max_digits'] = 8
        kwargs['decimal_places'] = 5
        super(XPctField, self).__init__(*args, **kwargs)


class Election(models.Model):
    EL_TYPES = (
        ('PV', 'Presidentinvaali'),
        ('E', 'Eduskuntavaalit'),
        ('K', 'Kunnallisvaalit'),
        ('EPV', 'Europarlamenttivaalit'),
        )
    electiontype = models.CharField(max_length=3, choices=EL_TYPES)
    timestamp = models.CharField(max_length=15)
    phase = models.CharField(max_length=5)
    

class ComparisonElection(models.Model):
    abbreviation = models.CharField(max_length=10)

    def gentxt(self):
        return self.abbreviation


class Area(models.Model):
    AREA_TYPES = (
        ('A', 'Äänestysalue'),
        ('K', 'Kunta'),
        ('V', 'Vaalipiiri'),
        ('M', 'Koko maa'),
        )
    LANGUAGE_TYPES = (
        ('1', 'Suomi'),
        ('2', 'Ruotsi'),
        ('3', 'Suomi+Ruotsi'),
        ('4', 'Ruotsi+Suomi'),
    )
    areatype = models.CharField(max_length=1, choices=AREA_TYPES)
    identifier = models.CharField(max_length=4)
    abbreviation = models.CharField(max_length=3)
    name = models.CharField(max_length=40)
    is_city = models.BooleanField(default=False)
    languages = models.CharField(max_length=1, choices=LANGUAGE_TYPES, null=True)
    joined_to = models.ForeignKey('Area', related_name='joined_areas', null=True)
    parent = models.ForeignKey('Area', related_name='children', null=True)
    polling_districts = models.IntegerField(default=0)
    number_to_be_elected = models.IntegerField(null=True)

    def gentxt(self):
        if self.areatype == 'A':
            return u"%s: %s (%s/%s)" % (self.areatype, self.name, self.parent.name, self.abbreviation)

        elif self.areatype == 'K':
            return u"%s: %s (%s)" % (self.areatype, self.name, self.abbreviation)

        return u"%s: %s" % (self.areatype, self.name)


    @classmethod
    def genid(cls, areatype, identifier):
        if areatype == 'M':
            idnum = 1
        elif areatype == 'V':
            idnum = 100 + int(identifier)
        elif areatype == 'K':
            idnum = 1000 + int(identifier)
        elif areatype == 'A':
            id_str = identifier
            try:
                id_int = int(id_str)
            except ValueError:
                # 0123A type identifier
                id_int = int(id_str[:-1]) * 10 + ord(id_str[-1]) - ord('@')
            idnum = self.current_area.id*1000 + id_int
        return idnum

    def __unicode__(self):
        return u"%s: %s" % (self.id, self.name)


class Nominator(models.Model):
    identifier = models.CharField(max_length=4)
    name = models.CharField(max_length=120)
    abbreviation = models.CharField(max_length=10)
    

    total_votes = models.IntegerField(null=True)
    advance_votes = models.IntegerField(null=True)
    electionday_votes = models.IntegerField(null=True)
    total_pct = PctField(null=True)
    advance_pct = PctField(null=True)
    electionday_pct = PctField(null=True)
    seats = models.IntegerField(null=True)

    def gentxt(self):
        return self.abbreviation
    
    @classmethod
    def genid(cls, partyid, partynum):
        if str(partyid) != '99':
            return int(partyid)
        else:
            return 9900000 + int(partynum)

    def __unicode__(self):
        return u"%s: %s" % (self.id, self.name)


class Alliance(models.Model):
    identifier = models.CharField(max_length=10, null=True)
    area = models.ForeignKey(Area, related_name='alliances')
    areatxt = models.CharField(max_length=80)
    name = models.CharField(max_length=80)

    @classmethod
    def genid(cls, area, listnumber):
        return area.id * 1000 + int(listnumber)

    def __unicode__(self):
        return u"Alliance: %s - %s" % (self.name, self.area)


class AllianceNominator(models.Model):
    alliance = models.ForeignKey(Alliance, related_name='nominators')
    nominator = models.ForeignKey(Nominator, related_name='alliances')

    def __unicode__(self):
        return u"%s in %s" % (self.nominator, self.alliance)


ELECTED_TYPES = (
    (1, 'Elected'),
    (2, 'Substitute'),
    (3, 'Not elected'),
)

class Candidate(models.Model):
    GENDER_TYPES = (
        ('1', 'Male'),
        ('2', 'Female'),
    )
    area = models.ForeignKey(Area, related_name='candidates')
    areatxt = models.CharField(max_length=80)
    nominator = models.ForeignKey(Nominator, related_name='candidates')
    nominatortxt = models.CharField(max_length=80)
    candidate_number = models.CharField(max_length=4)
    first_name = models.CharField(max_length=40)
    last_name = models.CharField(max_length=40)
    gender = models.CharField(max_length=1, choices=GENDER_TYPES)
    age = models.IntegerField()
    occupation = models.CharField(max_length=120, null=True)
    language = models.CharField(max_length=2, null=True)
    home_municipality = models.ForeignKey(Area, related_name='candidatesfrom', null=True)
    home_municipality_name = models.CharField(max_length=40, null=True)

    total_votes = models.IntegerField(null=True)
    advance_votes = models.IntegerField(null=True)
    electionday_votes = models.IntegerField(null=True)
    total_pct = PctField(null=True)
    advance_pct = PctField(null=True)
    electionday_pct = PctField(null=True)
    elected_information = models.IntegerField(choices=ELECTED_TYPES, null=True)
    comparative_index = models.DecimalField(max_digits=12, decimal_places=3, null=True)
    position = models.IntegerField(null=True)

    def gentxt(self):
        return "%s, %s (%s/%s)" % (self.last_name, self.first_name, self.nominator.abbreviation, self.area.abbreviation)

    @classmethod
    def genid(cls, area, candidatenumber):
        return area.id * 10000 + int(candidatenumber)


    def __unicode__(self):
        return u"%s: %s, %s (%s/%s)" % (self.id, self.last_name, self.first_name, self.nominator.abbreviation, self.area.abbreviation)


class Membership(models.Model):
    title = models.CharField(max_length=40)


class CandidateMembership(models.Model):
    candidate = models.ForeignKey(Candidate, related_name='memberships')
    membership = models.ForeignKey(Membership, related_name='candidates')


class NominatorArea(models.Model):
    area = models.ForeignKey(Area, related_name='nominatorareas')
    areatxt = models.CharField(max_length=80)
    nominator = models.ForeignKey(Nominator, related_name='nominatorareas')
    nominatortxt = models.CharField(max_length=80)

    candidates = models.IntegerField()
    number = models.IntegerField()
    numberstart = models.IntegerField()
    numberend = models.IntegerField()
    alliance = models.ForeignKey(Alliance, related_name='nominatorareas', null=True)
    alliancetxt = models.CharField(max_length=80, null=True)


class NominatorResults(models.Model):
    area = models.ForeignKey(Area, related_name='nominatorresults')
    areatxt = models.CharField(max_length=80)
    nominator = models.ForeignKey(Nominator, related_name='nominatorresults')
    nominatortxt = models.CharField(max_length=80)
    total_votes = models.IntegerField(null=True)
    advance_votes = models.IntegerField(null=True)
    electionday_votes = models.IntegerField(null=True)
    total_pct = PctField(null=True)
    advance_pct = PctField(null=True)
    electionday_pct = PctField(null=True)
    seats = models.IntegerField(null=True)



class CandidateResults(models.Model):
    area = models.ForeignKey(Area, related_name='candidateresults')
    areatxt = models.CharField(max_length=80)
    nominator = models.ForeignKey(Nominator, related_name='candidateresults')
    nominatortxt = models.CharField(max_length=80)
    candidate = models.ForeignKey(Candidate, related_name='candidateresults')
    candidatetxt = models.CharField(max_length=80)
    total_votes = models.IntegerField()
    advance_votes = models.IntegerField()
    electionday_votes = models.IntegerField()
    total_pct = PctField()
    advance_pct = PctField()
    electionday_pct = PctField()
    elected_information = models.IntegerField(choices=ELECTED_TYPES, null=True)
    comparative_index = models.DecimalField(max_digits=12, decimal_places=3, null=True)
    position = models.IntegerField(null=True)

class VotingData(models.Model):

    area = models.ForeignKey(Area, related_name='votingdata')
    areatxt = models.CharField(max_length=80)

    eligible_total = models.IntegerField()
    eligible_men = models.IntegerField()
    eligible_women = models.IntegerField()

    eligible_finland_total = models.IntegerField()
    eligible_finland_men = models.IntegerField()
    eligible_finland_women = models.IntegerField()

    total_turnout = PctField()
    advance_turnout = PctField()
    electionday_turnout = PctField()

    total_finland_turnout = XPctField()
    advance_finland_turnout = XPctField()
    electionday_finland_turnout = XPctField()

    total_abroad_turnout = XPctField()
    advance_abroad_turnout = XPctField()
    electionday_abroad_turnout = XPctField()

    total_votes = models.IntegerField()
    advance_votes = models.IntegerField()
    electionday_votes = models.IntegerField()

    total_males_votes = models.IntegerField()
    advance_males_votes = models.IntegerField()
    electionday_males_votes = models.IntegerField()

    total_finland_votes = models.IntegerField()
    advance_finland_votes = models.IntegerField()
    electionday_finland_votes = models.IntegerField()

    total_finland_males_votes = models.IntegerField()
    advance_finland_males_votes = models.IntegerField()
    electionday_finland_males_votes = models.IntegerField()

    total_abroad_votes = models.IntegerField()
    advance_abroad_votes = models.IntegerField()
    electionday_abroad_votes = models.IntegerField()

    total_abroad_males_votes = models.IntegerField()
    advance_abroad_males_votes = models.IntegerField()
    electionday_abroad_males_votes = models.IntegerField()
    
    total_approved_votes = models.IntegerField()
    advance_approved_votes = models.IntegerField()
    electionday_approved_votes = models.IntegerField()

    total_invalid_votes = models.IntegerField()
    advance_invalid_votes = models.IntegerField()
    electionday_invalid_votes = models.IntegerField()
    

class VotingDataComparison(models.Model):

    area = models.ForeignKey(Area, related_name='votingdatacomparison')
    areatxt = models.CharField(max_length=80)
    comparison = models.ForeignKey(ComparisonElection, related_name='votingdatacomparison')
    comparisontxt = models.CharField(max_length=80)

    eligible_total = models.IntegerField()
    eligible_men = models.IntegerField()
    eligible_women = models.IntegerField()

    eligible_finland_total = models.IntegerField()
    eligible_finland_men = models.IntegerField()
    eligible_finland_women = models.IntegerField()

    total_turnout = XPctField()
    advance_turnout = XPctField()
    electionday_turnout = XPctField()

    total_approved_votes = models.IntegerField()
    total_invalid_votes = models.IntegerField()

    number_to_be_elected = models.IntegerField(null=True)
    
