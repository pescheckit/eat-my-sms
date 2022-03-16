#!/usr/bin/env python3

import argparse
import logging
import re
import subprocess
import tempfile
import time

CONFIG_TEMPLATE = '''
[global]
port = /dev/ttyACM{}
model = AT
connection = serial
serial_baudrate = 57600
'''

class Modem:
	def __init__(self, port, pin='0000'):
		logging.info('Initializing modem at port {}'.format(port))

		self.pin = pin
		with tempfile.NamedTemporaryFile(mode='w+t', prefix='gnokii-', delete=False) as config:
			config.write(CONFIG_TEMPLATE.format(port))
			self.config = config.name
		logging.info('Wrote gnokii config to: {}'.format(self.config))

		# Check if a pin needs to be entered and do so
		logging.info('Checking if SIM is locked...')
		if self.is_locked():
			logging.info('SIM is locked, entering PIN...')
			self.enter_pin()
			if self.is_locked():
				raise Exception('SIM still not unlocked after entering pin')
		else:
			logging.info('SIM is unlocked')

		# Wait until connected to network, then print info
		while True:
			info = self.network_info()
			if re.match(r'undefined', info['Network code'], re.I):
				logging.info('Not connected to network yet, waiting to try again...')
				time.sleep(3)
			else:
				break
		logging.info('Network info: {}'.format(info))

		logging.info('Modem at port {} initialized'.format(port))

	def command(self, *args, input=None):
		if input:
			input = input.encode()

		cmd = subprocess.run(
			['gnokii', '--config', self.config, *args],
			input=input,
			stdout=subprocess.PIPE,
			stderr=subprocess.PIPE,
			timeout=10,
		)
		stdout = cmd.stdout.decode('utf-8')
		stderr = cmd.stderr.decode('utf-8')

		err = re.search(r'^error:(.*)$', stderr, re.M | re.I)
		if err:
			raise Exception('Error from gnokii', err.group(1).strip())

		return (stdout, stderr)

	def is_locked(self):
		cmd = self.command('--getsecuritycodestatus')

		status = re.search(r'^security code status:(.*)$', cmd[0], re.M | re.I)
		if status:
			msg = status.group(1).strip()
			if re.search(r'waiting for pin', msg, re.I):
				return True
			if re.search(r'nothing to enter', msg, re.I):
				return False
			else:
				raise Exception('Invalid security code status', msg)
		else:
			raise Exception('Could not read security code status')

	def enter_pin(self):
		cmd = self.command('--entersecuritycode', 'PIN', input=self.pin)

		status = re.search(r'^code ok', cmd[1], re.M | re.I)
		if status:
			logging.info('PIN accepted, SIM unlocked')
		else:
			raise Exception('PIN was not accepted', cmd[1])

	def network_info(self):
		cmd = self.command('--getnetworkinfo')

		info = {}
		for line in cmd[0].strip().split('\n'):
			match = re.match('^(.*):(.*)$', line)
			if match:
				info[match.group(1).strip()] = match.group(2).strip()
		return info

	def read_sms(self):
		cmd = self.command('--getsms', 'MT', '1', 'end')

		sms = []
		messages = re.split(r'\d+\. inbox message.*[\n]', cmd[0], flags=re.M | re.I)
		for msg in messages:
			if msg:
				date = re.search(r'^date/time:(.*)$', msg, re.M | re.I).group(1).strip()
				sender = re.search(r'^sender:\s+(\+\d+)', msg, re.M | re.I).group(1).strip()
				smsc = re.search(r'msg center:\s+(\+\d+)', msg, re.M | re.I).group(1).strip()
				body = re.split(r'^text:[\n]', msg, flags=re.M | re.I)[1].strip()
				sms.append({
					'date': date,
					'sender': sender,
					'smsc': smsc,
					'body': body,
				})

		return sms

def main():
	logging.basicConfig(format='%(asctime)s [%(levelname)s]: %(message)s', level=logging.INFO)

	parser = argparse.ArgumentParser(description='SMS reader')
	parser.add_argument('port', metavar='PORT', type=int, help='Number of the port to use (`ls /dev/ttyACM*`)')
	parser.add_argument('--pin', type=str, help='PIN to use when unlocking SIM')
	args = parser.parse_args()

	modem = Modem(args.port)

	logging.info('Start reading SMS...')
	while True:
		for sms in modem.read_sms():
			logging.info('SMS received: {}'.format(sms))
		time.sleep(3)

if __name__ == '__main__':
	main()
