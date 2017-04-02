# -*- coding: utf-8 -*-


from electiondata.ed.models import *
from csvparser import PartyParser, CandidateParser


districts = {
    '01': "Helsinki",
    '02': "Uusimaa",
    '03': "Varsinais-Suomi",
    '04': "Satakunta",
    '06': "Häme",
    '07': "Pirkanmaa",
    '08': "Kaakkois-Suomi",
    '09': "Savo-Karjala",
    '10': "Vaasa",
    '11': "Keski-Suomi",
    '12': "Oulu",
    '13': "Lappi",
}


class PartyHandler(PartyParser):
    
    def handle(self, values):
        
        (country, created) = Area.objects.update_or_create(
            id = Area.genid('M', 1),
            defaults = dict(
                areatype = 'M',
                identifier = 1,
                abbreviation = '',
                name = 'Koko maa',
                parent = None,
            )
        )

        (district, created) = Area.objects.update_or_create(
            id = Area.genid('V', values.district),
            defaults = dict(
                areatype = 'V',
                identifier = values.district,
                abbreviation = values.district_short,
                name = districts[values.district],
                parent = country,
            )
        )

        (municipality, created) = Area.objects.update_or_create(
            id = Area.genid(values.areatype, values.areaid),
            defaults = dict(
                areatype = values.areatype,
                identifier = values.areaid,
                abbreviation = '',
                name = values.areaname,
                parent = district
            )
        )

        (nominator, created) = Nominator.objects.update_or_create(
            id = Nominator.genid(values.partyid, values.permanent_partyid),
            defaults = dict(
                identifier = values.partyid,
                abbreviation = values.partyshort,
                name = values.partyname,
            )
        )
        if values.listname:
            (alliance, created) = Alliance.objects.update_or_create(
                id = Alliance.genid(municipality, values.listnumber),
                defaults = dict(
                    area = municipality,
                    areatxt = municipality.gentxt(),
                    name = values.listname,
                )
            )
        else:
            alliance = None

        (nominatorarea, created) = NominatorArea.objects.update_or_create(
            area = municipality,
            nominator = nominator,
            defaults = dict(
                areatxt = municipality.gentxt(),
                nominatortxt = nominator.gentxt(),
                candidates=int(values.candidateend)-int(values.candidatestart)+1,
                numberstart=int(values.candidatestart),
                numberend=int(values.candidateend),
                number=int(values.listnumber),
                alliance=alliance,
                alliancetxt=values.listname,
            )
        )
        
            
            
        
        

    
class CandidateHandler(CandidateParser):
    
    def handle(self, values):
        area = Area.objects.get(
            id = Area.genid(values.areatype, values.areaid)
        )
        nominator = Nominator.objects.get(
            id = Nominator.genid(values.partyid, values.permanent_partyid),
        )

        try:
            home_municipality = Area.objects.get(
                areatype='K',
                identifier=values.homemunicipalityid,
            )
        except Area.DoesNotExist:
            home_municipality = None

        (candidate, created) = Candidate.objects.update_or_create(
            id = Candidate.genid(area, values.candidatenumber),
            defaults = dict(
                candidate_number = values.candidatenumber,
                area = area,
                areatxt = area.gentxt(),
                nominator = nominator,
                nominatortxt = nominator.gentxt(),
                first_name = values.firstname,
                last_name = values.lastname,
                gender = values.gender,
                age = values.age,
                occupation = values.title,
                language = values.language,
                home_municipality = home_municipality,
                home_municipality_name = values.homemunicipality,
            )
        )


    

def update_alliances():
    for alliance in Alliance.objects.all():
        for nomtxt in alliance.name.split('+'):
            nominator = Nominator.objects.get(abbreviation=nomtxt)
            (alliancenominator, created) = AllianceNominator.objects.get_or_create(
                alliance = alliance,
                nominator = nominator
            )


def loaddata(datatype, path):
    if datatype == 'party':
        p = PartyHandler(path)
    elif datatype == 'candidate':
        p = CandidateHandler(path)
    elif datatype == 'alliances':
        update_alliances()
    
