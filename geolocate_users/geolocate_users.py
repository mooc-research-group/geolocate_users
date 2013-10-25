#    Copyright (C) 2013  Eric Koo <erickoo@umich.edu>
#    USE Lab, Digital Media Commons, University of Michigan Library
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see [http://www.gnu.org/licenses/].

import csv
import glob
import os
import re

def get_index(value, array):
  length = len(array)
  for i in range(0,length):
    if array[i]==value:
      return i

def get_valid_ip(last_access_ip):
  # clean entries in last_access_ip and return only good ip addresses
  valid_ip_address = None
  if last_access_ip.find(','):
    ip_list = last_access_ip.split(',')
    for ip in ip_list:
      ip = ip.strip()
      ip_re = re.search(r'[0-9]+\.[0-9]+\.[0-9]+\.[0-9]+',ip)
      if ip_re:
        valid_ip_address = ip
        break
  else:
    ip_re = re.search(r'[0-9]+\.[0-9]+\.[0-9]+\.[0-9]+',last_access_ip)
    if ip_re:
      valid_ip_address = last_access_ip
      
  return valid_ip_address

def address_to_int(address):
  # calculate the integer value of an IPv4 address
  [o1,o2,o3,o4] = address.split('.')
  integer_ip = 16777216*int(o1) + 65536*int(o2) + 256*int(o3) + int(o4)
  return integer_ip

def int_to_address(integer_ip):
  # turn an integer back into an IPv4 address
  o1 = int(integer_ip/16777216)%256
  o2 = int(integer_ip/65536)%256
  o3 = int(integer_ip/256)%256
  o4 = int(integer_ip)%256
  address = str(o1)+'.'+str(o2)+'.'+str(o3)+'.'+str(o4)
  return address

print 'Geolocating users on IP address...'
print ''

input_file = 'users.csv'        # <-- Specify input .csv file here
output_file = 'users_ip.csv'    # <-- Specify output .csv filename here

# Fetch IP address mappings
print 'Loading MaxMind GeoIP databases...'
GeoIPCountryWhois = []
file_name = 'GeoIP/GeoIPCountryWhois.csv'
print '   Reading file: '+file_name
with open(file_name,'rU') as IN:
  reader = csv.reader(IN)
  for row_num, row in enumerate(reader):
    GeoIPCountryWhois.append(row)
print '   Done. ('+str(row_num+1)+' rows)'
print ''

GeoLiteCityBlocks = []
file_name = 'GeoIP/GeoLiteCity-Blocks.csv'
print '   Reading file: '+file_name
with open(file_name,'rU') as IN:
  reader = csv.reader(IN)
  reader.next()
  header = reader.next()
  for row_num, row in enumerate(reader):
    GeoLiteCityBlocks.append(row)
print '   Done. ('+str(row_num+1)+' rows)'
print ''

GeoLiteCityLocation = {}
file_name = 'GeoIP/GeoLiteCity-Location.csv'
print '   Reading file: '+file_name
with open(file_name,'rU') as IN:
  reader = csv.reader(IN)
  reader.next()
  GeoLiteCityLocation_header = reader.next()
  for row_num, row in enumerate(reader):
    GeoLiteCityLocation[row[0]] = row
print '   Done. ('+str(row_num+1)+' rows)'
print ''

# Sort list by IP address (if "tmpfile.csv" already generated, then skip this step)
tmpfile = glob.glob('tmpfile.csv')
if tmpfile:
  tmpfile = tmpfile[0]
else:
  users = []
  print 'Sorting by last_access_ip...'
  file_name = input_file
  print 'Reading file: '+file_name
  with open(file_name,'rU') as IN:
    reader = csv.reader(IN)
    users_header = reader.next()
    last_access_ip_index = get_index('last_access_ip',users_header)
    last_access_ip_num = 0
    for user_num, row in enumerate(reader):
      last_access_ip = get_valid_ip(row[last_access_ip_index])
      if last_access_ip is not None:
        users.append(row + [address_to_int(last_access_ip)])
        last_access_ip_num += 1
      else:
        users.append(row + [None])
  users.sort(key=lambda x: x[-1])

  tmpfile = 'tmpfile.csv'
  with open(tmpfile,'wb') as OUT:
    writer = csv.writer(OUT,delimiter=',')
    writer.writerow(users_header)
    for row in users:
      writer.writerow(row[:-1])
  del users

  print 'Done. ('+str(user_num+1)+' rows, '+str(last_access_ip_num)+' IP addresses)'
  print ''

# Geolocate users on IP address
print 'Fetching IP address geolocation matches...'
file_name = output_file
with open(tmpfile,'rU') as IN:
  reader = csv.reader(IN)
  header = reader.next()
  last_access_ip_index = get_index('last_access_ip',header)
  geolocation_num = 0
  with open(file_name,'wb') as OUT:
    print 'Writing to file: '+file_name
    writer = csv.writer(OUT,delimiter=',')
    writer.writerow(header[:last_access_ip_index+1]+['countryName']+GeoLiteCityLocation_header+header[last_access_ip_index+1:])
    GeoIPCountryWhois_last = 0
    GeoLiteCityBlocks_last = 0
    for row_num, row in enumerate(reader):
      last_access_ip = get_valid_ip(row[last_access_ip_index])
      countryName = None
      locId = None
      if last_access_ip is not None:
        last_access_ip = address_to_int(last_access_ip)
        for IpNum in GeoIPCountryWhois[GeoIPCountryWhois_last:]:
          if last_access_ip >= int(IpNum[2]) and last_access_ip <= int(IpNum[3]):
            countryName = IpNum[5]
            break
          elif last_access_ip > int(IpNum[3]):
            GeoIPCountryWhois_last += 1
          else:
            break
            
        for IpNum in GeoLiteCityBlocks[GeoLiteCityBlocks_last:]:  
          if last_access_ip >= int(IpNum[0]) and last_access_ip <= int(IpNum[1]):
            locId = IpNum[2]
            geolocation_num += 1
            break
          elif last_access_ip > int(IpNum[1]):
            GeoLiteCityBlocks_last += 1
          else:
            break
            
      if locId is not None:
        writer.writerow(row[:last_access_ip_index+1]+[countryName]+GeoLiteCityLocation[locId]+row[last_access_ip_index+1:])
      else:
        writer.writerow(row[:last_access_ip_index+1]+[countryName]+[None,None,None,None,None,None,None,None,None]+row[last_access_ip_index+1:])
      if row_num == 0:
        print '   Processing...'
      elif row_num%1000 == 0:
        print '   '+str(row_num)+' rows processed...'
        
os.remove('tmpfile.csv')   # Comment out this line to keep "tmpfile.csv"

print 'Done. ('+str(row_num+1)+' rows, '+str(geolocation_num)+' geolocations)'
print ''
print ''
close = raw_input('Press any key to close this window.')

