from subprocess import check_output
import pandas as pd
import time
from urllib import request
import os

try:
	from inputimeout import inputimeout
except:
	print('inputtimeout not installed')

def check_connection(retry = 5):
	trys = 1
	while trys <= retry:
		print(f'Test internet #{trys}/{retry}')
		localoutput = check_output(["hostname", "-I"])
		try:
			local = localoutput.decode("utf-8").split()[0]
		except:
			local = None
			internet = False

		trys += 1
		time.sleep(1)

		#if locally connected, check if conneced to the internet
		if local is not None:
			try:
				request.urlopen('https://google.com', timeout=2)
				internet = True
				break
			except:
				internet = False

	if local is not None:
		print(f'found local ip address: {local}')
	else:
		print(f'Wifi not connected')
	if internet:
		print('Internet connected')
	else:
		print('No internet connection')

	return (local, internet)


def scan(retry = 10):
	trys = 1 #sometimes need to retry multiple times to have an output
	while trys <= retry:
		print(f'Scan #{trys}/{retry}')
		found_ssid = pd.DataFrame(columns=['level', 'ssid'])
		scanoutput = check_output(["iwlist","wlan0","scan"])
		#print(scanoutput)
		for line in scanoutput.split():
		#	print(line.decode("utf-8"))
			line = line.decode("utf-8")
		#	input(line)
			if line == "Cell":
				entry = {}
			if line.startswith("level"):
				entry['level'] = line.split("=")[1]
			if line.startswith("ESSID"):
				entry['ssid']  = line.split('"')[1]
				found_ssid = found_ssid.append(entry, ignore_index=True, sort = False)

		if len(found_ssid) > 0:
			break
		else:
			time.sleep(1)
			trys += 1

	return found_ssid.sort_values(by='level', ignore_index=True)

def write_wpa(ssid, pwd):
	pwd = pwd.strip()
	isin = False
	#wpaconf = '/home/math/Desktop/wpa_supplicant.conf'
	wpaconf = '/etc/wpa_supplicant/wpa_supplicant.conf'

	with open(wpaconf, 'r') as f:
		in_lines = f.readlines()

	out_lines = []
	for idx, line in enumerate(in_lines):
		if line.strip().startswith("ssid"):
			current_ssid = line.split('"')[1]
			if ssid == current_ssid:
				change_psk = True
				isin = True
			else:
				change_psk = False
			out_lines.append(line)
		elif line.strip().startswith("psk") and change_psk:
			out_lines.append(f'psk="{pwd}"')
			print(f'Changing pwd for {ssid}')
		else:
			out_lines.append(line)

	if not isin:
		out_lines.append('\n')
		out_lines.append('network={\n')
		out_lines.append(f'ssid="{ssid}"\n')
		out_lines.append(f'psk="{pwd}"\n')
		out_lines.append('key_mgmt=WPA-PSK\n')
		out_lines.append('}\n')
		print(f'Add {ssid} to wpa file')

	with open(wpaconf, 'w') as f:
		f.writelines(out_lines)


def main(waitforinput = False):

	while True:

		#first check the connection
		local, internet = check_connection()
		if internet:
			break

		if waitforinput:
			try:
				mess = 'Appuyer sur enter dans les 10 secondes pour choisir un réseau'
				inputimeout(mess, 10)
			except:
				break
		waitforinput = False

		#if no connection scan the networks
		scanr = scan()
		print(scanr)


		print("Sélectionner le numéro du réseau à ajouter")
		print("ou 'q' pour quitter, 's' pour rescanner")
		inp = input("réseau :")
		if inp in ['s', 'S']:
			continue
		elif inp in ['q','Q']:
			break
		elif inp.isdigit() and (int(inp) <= len(scanr)) and (int(inp) >= 0):
			ssid = scanr.loc[int(inp),'ssid']
			pwd = input(f'Enter password for {ssid}:')
			write_wpa(ssid,pwd)
			os.system('wpa_cli -i wlan0 reconfigure')
			time.sleep(10)
			check_connection()
			break
		else:
			print('wrong input')


if __name__=='__main__':
	main()
