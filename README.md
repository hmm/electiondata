Django Project for reading official Finnish Parliament election result data
to a database.

I have written this project basically just for my own use but I am sharing 
it in case it turns out to be useful to someone else.

You are free to use and modify the code but I'd appreciate if you'd mention my
name as the author.

Markku Hänninen, markku.hanninen@iki.fi, twitter: @markkuhanninen


Short instructions for use:

1. set up Django DB access settings in electiondata/local_settings.py

2. run manage.py syncdb --noinput

3. download XML result data from vaalit.fi

4. read area data ./manage.py xmlreader areas e-2015_alu_maa.xml.zip

5. read nominator (i.e. party) data: ./manage.py xmlreader nominators e-2015_puo_maa.xml.zip

6. read candidate data: ./manage.py xmlreader candidates e-2015_ehd_maa.xml.zip



-----------------

Addition for handling Finnish Municipal election data in 2017. Currently supports reading the csv nominator & candidate data provided at http://tulospalvelu.vaalit.fi/KV-2017/fi/ladattavat_tiedostot_ehd.html

Please ask instructions by email or twitter if you are interested in using the data.



