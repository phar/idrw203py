#!/usr/bin/python

#import usb.core
#import usb.util
import json
import struct
import hid

#https://github.com/merbanan/rfid_app/
#https://www.digchip.com/datasheets/parts/datasheet/147/EM4100-pdf.php
#http://ww1.microchip.com/downloads/en/DeviceDoc/ATA5577C-Read-Write-LF-RFID-IDIC-100-to-150-kHz-Data-Sheet-DS70005357B.pdf
#https://www.emmicroelectronic.com/sites/default/files/products/datasheets/4205-4305-DS-01.pdf

CLIENT_TO_DEVICE_MARKER = 0x03
DEVICE_TO_CLIENT_MARKER = 0x05
MESSAGE_END_MARKER = 0x04
MESSAGE_START_MARKER = 0x01

COMMAND_IDX = {
	0x00:"GetSupport",
	0x01:"TestDevice",
	0x03:"Buzzer",
	0x10:"Em4100read",
	0x12:"T5577",
	0x13:"Em4305",
	0x14:"Carrier",
#	0x20:"mifare_reset",
}


CMD_GET_SUPPORT = 0x00
CMD_TEST_DEVICE = 0x01
CMD_CMDTWO		= 0x02
CMD_BUZZER		= 0x03
CMD_EM4100_READ = 0x10
CMD_T5577		= 0x12
CMD_EM4305		= 0x13
CMD_CARRIER		= 0x14 # takes arg 0=4


CMD_UNK_40 		= 0x40
CMD_UNK_41 		= 0x41
CMD_UNK_42 		= 0x42
CMD_UNK_43 		= 0x43

CMD_UNK_50 		= 0x50 #returns tag type
CMD_UNK_51 		= 0x51
CMD_UNK_52 		= 0x52
CMD_UNK_54 		= 0x54


CMD_UNK_80 		= 0x80
CMD_UNK_81 		= 0x81
CMD_UNK_82 		= 0x82
CMD_UNK_83 		= 0x83

CMD_UNK_90 		= 0x90  #returns tag type
CMD_UNK_91 		= 0x91
CMD_UNK_92 		= 0x92
CMD_UNK_94 		= 0x94

CMD_UNK_c0 		= 0xc0
CMD_UNK_c1 		= 0xc1
CMD_UNK_c2 		= 0xc2
CMD_UNK_c3 		= 0xc3

CMD_UNK_d0 		= 0xd0 #returns tag type
CMD_UNK_d1 		= 0xd1
CMD_UNK_d2 		= 0xd2
CMD_UNK_d4 		= 0xd4





T5577_CMD_START=0x00
T5577_CMD_UNK1=0x01
T5577_CMD_FINAL=0x02
T5577_CMD_UNK2=0x03
T5577_CMD_WRITE_BLOCK=0x04

EM4305_CMD_LOGIN=0x02



RESPONSE_OK = 0x83
RESPONSE_BYTE = 0x92
RESPONSE_WORD = 0x93
RESPONSE_DWORD = 0x80
RESPONSE_TAG = 0x90
RESPONSE_ERROR = 0xff





class IDRW203Driver():
	def __init__(self, vid=0x6688, pid=0x6850):
		self.vid = vid
		self.pid = pid
		self.debug = False
		self.connected = False
		
		
	def disconnect(self):
		if self.connected == True:
			self.connected = False
			self.dev.close()

	def connect(self):
		if self.connected == False:
			self.dev = hid.device()
			try:
				self.dev.open(self.vid, self.pid)
				if self.debug:
					print('Connected to dev')
				self.connected = True
			except:
				pass
	
		return self.connected
	
	def calc_checksum(self,buf, crc=0):
		for i in range(len(buf)):
			crc = crc^buf[i];
		return crc
		
	def checksum_packet(self,pkt):
			r = self.calc_checksum(pkt[1:-2])
			if r == pkt[-2] and pkt[-1] == MESSAGE_END_MARKER :
				return(True,r)
			else:
				return(False,r)
			
	def strip_packet(self, pkt):
		return pkt[3:-2]

	def recv_response(self, response_pkt):
		response_pkt = response_pkt[0:response_pkt[2] + 1]
		(isgood, r) = self.checksum_packet(response_pkt)
		if isgood:
			s = self.strip_packet(response_pkt)
			return s
		else:
			return None

	def Em4305_login(self,password=0x00000000):
		return self.send_command(CMD_EM4305, [EM4305_CMD_LOGIN, 1] + list(struct.pack("<I", password)) + [0])  #some guessing here


	def Em4305_write_word(self, idx, word):

		return self.send_command(CMD_T5577, [T5577_CMD_WRITE_BLOCK, page] + list(struct.pack("<I", value)) + [block])


	def T5577_write_block(self,page,block,value):
		return self.send_command(CMD_T5577, [T5577_CMD_WRITE_BLOCK, page] + list(struct.pack("<I", value)) + [block])
	
	def buzzer(self,duration=0x09):
		return self.send_command(CMD_BUZZER,[duration])
		
	def get_support(self):
		return self.send_command(CMD_GET_SUPPORT)
		
	
	def Em4100_read(self):
		return self.send_command(CMD_EM4100_READ)

	def send_command(self, cmd_id, argbuff=[]):
		if self.connected:
			tmpbuff  =   [MESSAGE_START_MARKER, len(argbuff)+5, cmd_id] +  argbuff
			outbuff = [CLIENT_TO_DEVICE_MARKER] + tmpbuff + [self.calc_checksum(tmpbuff)] + [MESSAGE_END_MARKER]
			if(self.debug):
				print(bytes(outbuff))
			self.dev.write(outbuff)
			buf = self.dev.read(1000)
			ret = self.recv_response(buf)
			if ret:
				if ret[0] == RESPONSE_OK:
					return (True,RESPONSE_OK,True)
				elif ret[0] == RESPONSE_ERROR:
					return (True,RESPONSE_ERROR,False)
				elif ret[0] == RESPONSE_BYTE:
					return (True,RESPONSE_BYTE,struct.unpack("b",bytes(ret[1]))[0])
				elif ret[0] == RESPONSE_WORD:
					return (True,RESPONSE_WORD,struct.unpack("<H",bytes(ret[1:]))[0])
				elif ret[0] == RESPONSE_TAG:
					return (True,RESPONSE_TAG,"".join(["%02x"%x for x in ret[2:]]))
				elif ret[0] == RESPONSE_DWORD:
					return (True,RESPONSE_TAG,struct.unpack("<i", bytes(ret[1:]))[0])
				else:
					return (True,hex(ret[0]),ret[1:])
##			else
#				return (False,None)
#			return buf
#		else:
#			raise ValueException
	
if __name__ == '__main__':
	d = IDRW203Driver()
#	d.debug = True
	d.connect() #just using it for emulation for now

#as seen in the usb capture
	(success,vt, tagid) = d.Em4100_read()
	if success:
		d.buzzer(9)
#		print(d.get_support())
		print(d.Em4100_read())
	
#
#	(success,vt, ret) = d.Em4305_login(0x00000000)
#	(success,vt, ret) = d.Em4305_login(0x00000000)
#
#	(success,vt, ret) = d.T5577_write_block(0,1,0x326580ff) #id
#	(success,vt, ret) = d.T5577_write_block(0,2,0xe6c6c754) #id
#	(success,vt, ret) = d.T5577_write_block(0,0,0x41801400) #config infirmation
#
#	(success,vt, tagid)  = d.Em4100_read()
#	if success:
#		d.buzzer(9)




#def column_parity(hex_buf, shift) {
#	int i, p=0;
#
#	for i in range(5):
#		p += (hex_buf[i] >> shift + 4) & 0x01
#		p += (hex_buf[i] >> shift) & 0x01
#	return p&1;
#}
