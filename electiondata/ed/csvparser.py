#!/usr/bin/env python

import sys, json


class Values(dict):

    def __getattr__(self, attrname):
        return self[attrname]


class Parser(object):

    def __init__(self, path):

        for values in self.parser(path):
            self.handlecolumn(values)


    def parser(self, path):

        with file(path) as fp:
            for l in fp:
                parts = l.split(";")
                idx = 1
                values = []
                for w in parts:
                    columns = "{0}-{1}".format(idx, idx+len(w)-1)
                    value = w.strip().decode('iso8859')
                    idx += len(w)+1
                    values.append((columns, value))
                yield values
                    
                    
class DataParser(Parser):

    
    def handlecolumn(self, columnvalues):
        values = Values()
        for (column, value) in columnvalues:
            try:
                attr = self.columns[column]
            except KeyError:
                raise Exception("Missing %s: %s" % (column, value))
            if attr:
                values[attr] = value

        self.handle(values)

    def handle(self, values):
        print json.dumps(values, sort_keys=True)


class PartyParser(DataParser):

    columns = {
        '1-4': 'electiontype',
        '6-7': 'district',
        '9-11': 'areaid',
        '13-13': 'areatype',
        '15-18': 'subareaid',
        '20-22': 'district_short',
        '24-26': '', # areaparent_short_swe
        '28-33': 'permanent_partyid', # (36)
        '35-36': 'partyid', # (14)
        '38-39': 'partynumber', # (01)
        '41-46': 'partyshort', # (FP)
        '48-53': '', #  partyshort_swe (FP)
        '55-60': '', #  partyshort_eng (FP)
        '62-101': 'areaname', # (Helsinki)
        '103-142': '', # areaname_swe (Helsingfors)
        '144-243': 'partyname', # (Feministinen puolue)
        '245-344': '', # partyname_swe (Feministiska partiet)
        '346-445': '', # partyname_eng (Feministinen puolue)
        '447-450': 'candidatestart', # (0002)
        '452-455': 'candidateend', # (0025)
        '457-458': 'listnumber', # (01)
        '460-499': 'listname', # ()
        '501-540': '', # ()
        '542-551': '', # (KV-2012)
        '553-559': '', # (0000000)
        '561-567': '', # (0000000)
        '569-575': '', # (0000000)
        '577-580': '', # (0000)
        '582-585': '', # (0000)
        '587-590': '', # (0000)
        '592-596': '', # (00000)
        '598-607': '', # (E-2015)
        '609-615': '', # (0000000)
        '617-623': '', # (0000000)
        '625-631': '', # (0000000)
        '633-636': '', # (0000)
        '638-641': '', # (0000)
        '643-646': '', # (0000)
        '648-654': '', # (0000000)
        '656-662': '', # (0000000)
        '664-670': '', # (0000000)
        '672-675': '', # (0000)
        '677-680': '', # (0000)
        '682-685': '', # (0000)
        '687-691': '', # (00000)
        '693-700': '', # (+0000000)
        '702-706': '', # (+0000)
        '708-713': '', # (+00000)
        '715-722': '', # (+0000000)
        '724-728': '', # (+0000)
        '730-730': '', # ()
        '732-732': '', # (A)
        '734-747': '', # (20170328153909)
        '749-749': '', # ()
    }
        
        
            
class CandidateParser(DataParser):

    columns = {
        '1-4': 'electiontype', # (K)
        '6-7': 'district', # (01)
        '9-11': 'areaid', # (091)
        '13-13': 'areatype', # (K)
        '15-18': 'areaid2', # (****)
        '20-22': 'areashort', # (HEL)
        '24-26': '', # areashort_swe (HEL)
        '28-33': 'permanent_partyid', # (36)
        '35-36': 'partyid', # (14)
        '38-39': 'listnumber', # (01)
        '41-42': '', # (01)
        '44-49': 'partyshort', # (FP)
        '51-56': '', # (FP)
        '58-63': '', # (FP)
        '65-68': 'candidatenumber', # (0002)
        '70-109': 'areaname', # (Helsinki)
        '111-150': '', # (Helsingfors)
        '152-201': 'firstname', # (Heidi)
        '203-252': 'lastname', # (Ahola)
        '254-254': 'gender', # (2)
        '256-258': 'age', # (026)
        '260-459': 'title', # (valtiotieteiden ylioppilas)
        '461-463': 'homemunicipalityid', # (091)
        '465-504': 'homemunicipality', # (Helsinki)
        '506-545': '', # (Helsingfors)
        '547-548': 'language', # (FI)
        '550-550': 'mep', # ()
        '552-552': 'mp', # ()
        '554-554': 'kv', # ()
        '556-556': '', # ()
        '558-567': '', # (KV-2012)
        '569-575': '', # (0000000)
        '577-583': '', # (0000000)
        '585-591': '', # (0000000)
        '593-599': '', # (0000000)
        '601-604': '', # (0000)
        '606-609': '', # (0000)
        '611-614': '', # (0000)
        '616-616': '', # (0)
        '618-627': '', # (0000000000)
        '629-632': '', # (0000)
        '634-637': '', # (0000)
        '639-639': '', # ()
        '641-641': '', # (A)
        '643-656': '', # (20170328153909)
        '658-658': '', # ()
    }
    

                
class Generator(Parser):
    def handlecolumn(self, columnvalues):
        for (column, value) in columnvalues:
            print u"        '{0}': '', # ({1})".format(column, value)

        sys.exit(0)
    
            
if __name__ == "__main__":
    if sys.argv[1] == 'party':
        p = PartyParser(sys.argv[2])
    elif sys.argv[1] == 'candidate':
        p = CandidateParser(sys.argv[2])
    elif sys.argv[1] == 'generator':
        p = Generator(sys.argv[2])
    
