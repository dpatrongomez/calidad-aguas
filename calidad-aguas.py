import csv
import sys
import urllib2

from BeautifulSoup import BeautifulSoup

beaches = []

# We know the number of beaches.
for i in range(1, 10):
  # Get the beach info.
  data_soup = BeautifulSoup(urllib2.urlopen('http://nayade.msc.es/Splayas/ciudadano/ciudadanoVerZonaAction.do?codZona=' + str(i)).read())
  # Get the beach samples.
  tomas_soup = BeautifulSoup(urllib2.urlopen('http://nayade.msc.es/Splayas/ciudadano/ciudadanoVerZonaAction.do?pestanya=3&codZona=' + str(i)).read())

  # This is ugly as hell, but I'm not used to BeautifulSoup.
  data_values = data_soup.findAll('td', {'class' : 'valorCampoI'})

  # Check is this a valid ID. There are some keys that are not present, in that case, we continue                                                                       
  if data_values[5].string == None:
    continue

  x = data_soup.find(text="Coordenadas UTM");
  geo = x.parent.parent.findAll('td', {'class':'valorCampoI'})
  tomas_values = tomas_soup.findAll('td', {'class' : 'valorCampoI'})

  # Generate the beach structure as it will be written in csv columns.
  beach = { 
    'Comunidad': data_values[0].string,
    'Provincia': data_values[1].string,
    'Municipio': data_values[2].string,
    'Nombre': data_values[5].string,
    'punto_muestreo': data_values[18].string,
    'adoptada_por': 'penyaskito (scrapping)',
    'utm_x': geo[0].string,
    'utm_y': geo[1].string,
    'fecha_toma': tomas_values[0].string,
    'escherichia_coli': tomas_values[1].string,
    'enterococo': tomas_values[2].string,
    'observaciones': tomas_values[3].string,
  }
  # Normalize data. We need to strip bad chars that could act as separators and fix the encoding.
  for key, value in beach.iteritems():
    if value is None:
      print key
    else:
      beach[key] = value.strip().encode("utf-8")
  # Some user feedback, we should be doing this on batches.
  print 'Data obtained for' , beach['Nombre']
  beaches.append(beach)

# Got the data, let's write it using the template.
with open('templates/calidad-aguas.template.csv', 'r') as template:
  template_reader = csv.DictReader(template)
  with open('data/calidad-aguas.csv', 'wb') as csvfile:
    writer = csv.DictWriter(csvfile, delimiter=';', quotechar='|', fieldnames = template_reader.fieldnames)
    writer.writeheader()
    for beach in beaches:
      writer.writerow(beach)
    csvfile.close()
  template.close()
