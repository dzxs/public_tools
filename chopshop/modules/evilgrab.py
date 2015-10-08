# Copyright (c) 2014 Palo Alto Networks. All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions
# are met:
# 1. Redistributions of source code must retain the above copyright
#    notice, this list of conditions and the following disclaimer.
# 2. Redistributions in binary form must reproduce the above copyright
#    notice, this list of conditions and the following disclaimer in the
#    documentation and/or other materials provided with the distribution.
#
# THIS SOFTWARE IS PROVIDED BY THE AUTHOR AND CONTRIBUTORS ``AS IS'' AND
# ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE
# ARE DISCLAIMED.  IN NO EVENT SHALL THE AUTHOR OR CONTRIBUTORS BE LIABLE
# FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL
# DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS
# OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION)
# HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT
# LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY
# OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF
# SUCH DAMAGE.

"""
Program to parse pcaps generated by Evilgrab samples to determine commands executed

"""
import binascii
import struct

from c2utils import hexdump

moduleName = "evilgrab_V2014-v05"
moduleVersion = "0.1"
minimumChopLib = "4.0"
author = "rfalc @ unit 42"

def command_conversion(command, payload, command_list):
    """
    Convert the command info (if known). See module_data['commands'] and module_data['exfil_types']
    Args:
        dest: a string containing either 'server' or 'client' to dictate which direction the packet is going.
        command: hex string of the command byte
        payload: hex string of the packet payload data
    """
    decoded_text = ''
    
    command_string = binascii.hexlify(command).lower()
    
    if command_list.has_key(command_string):
        decoded_text = command_list[command_string]
    else:
        decoded_text = ''
    
    return decoded_text, payload


def decode_command( dest, command, payload, command_list):
    """
    Print out the command info response from command_conversion.
    Args:
        dest: a string containing either 'server' or 'client' to dictate which direction the packet is going.
        command: hex string of the command byte
        payload: hex string of the packet payload data
    
    """
    
    if (dest == 'server'):

        decoded_text, payload = command_conversion(command, payload, command_list)
        chop.tsprnt('server -> client')
        if decoded_text:
            chop.tsprnt('EvilGrab Command: %s => %s' % (binascii.hexlify(command), decoded_text))
            if payload:
                chop.tsprnt('EvilGrab Command Payload:')
                if len(payload) > 32:
                    chop.tsprnt(hexdump(payload[:16]).strip())
                    chop.tsprnt(hexdump(payload[16:32]).strip())
                else:
                    chop.tsprnt(hexdump(payload).strip())
        else:
            #print the hexdump of non-commands
            chop.tsprnt("Unknown command: %x" % ord(command))

    elif dest == 'client':
        decoded_text, payload = command_conversion(command, payload, command_list)
        chop.tsprnt('client -> server')
        chop.tsprnt('Exfil Type: %s => %s' % (binascii.hexlify(command), decoded_text))
        ## lets check out the initial system data sent
        #chop.tsprnt("%s" % binascii.hexlify(command).lower())
        if binascii.hexlify(command).lower() == "a0" and payload:
           # the data should be pipe delimited, 
           # but its a string so lets split on NULL and write the data portion
           split_payload = payload.split("\x00") 
           chop.tsprnt('%r' % split_payload[0])
        elif payload:
            chop.tsprnt('EvilGrab Exfil Payload: ')
            if len(payload) > 32:
                chop.tsprnt(hexdump(payload[:16]).strip())
                chop.tsprnt(hexdump(payload[16:32]).strip())
            else:
                chop.tsprnt(hexdump(payload).strip())
    else:
        chop.tsprnt('unk -> unk')


def module_info():
    return "A module to make sense of the communications between Evilgrab, specifically version V2014-v05, and its C2 server.\n"


def init(module_data):
    module_options = { 'proto': [{'tcp': ''}] }
    module_data['commands'] = {
        "78" : "Turns on the QQ Memory Scraper and Keylogger",
        "79" : "Kills the QQ Memory Scraper and Keylogger functionality",
        "7a" : "Sets flags within the class. One of the flags is the hexadecimal value in the initial data sent from the host, specifically the 13th element of the pipe-delimited string",
        "7b" : "Uploads a specified file from the system to the C2 server",
        "7c" : "Creates a file with a specified name.",
        "7d" : "Sends the flags that indicate whether the QQ Memory Scraper and Keylogger are running",
        "7e" : "Sets a boolean value within the ActiveSettings. Unknown reason, but operators may use it to note if they have been there or not.",
        "82" : "Enumerate mounted volumes of storage and their type. The drive type prefixes the volume label, and the drive type prefixes sent within the response to the C2 are: R-removable F-fixed N-remote (network) C-cdrom D-ramdisk",
        "83" : "List contents of a folder, or file, along with each files last modification time, filename and file attributes",
        "84" : "Check to see if a specific file exists.",
        "85" : "Receive a file from the C2 and Execute it",
        "86" : "Creates a file and sets the file pointer ",
        "87" : "Close handles to files created in command 85",
        "88" : "Loads a DLL using ShellExecuteW using the open verb.",
        "89" : "Creates a directory with a specified name",
        "8a" : "Delete a specified file",
        "8b" : "Delete a directory and its contents.",
        "8c" : "Obtains the creation, modification and access times of a file and sends them to the C2",
        "8e" : "Executes a file using Explorer's token or runs a DLL using ShellExecuteW and the open verb.",
        "8f" : "Move a specified file to a specified location",
        "90" : "Steal credentials from Window's Protected Storage (PStore)",
        "92" : "Create a reverse shell",
        "93" : "Write string to file for an unknown purpose.",
        "94" : "Sets flag v2 + 19",
        "98" : "Enumerates visible Windows and reports the process names to the C2",
        "99" : "Sends the WM_DESTROY message to a specific Window to close it",
        "9a" : "Show a specified Window and set it as the foreground",
        "9b" : "Show a specified Window",
        "9c" : "Set the title of a Window",
        "9d" : "Interact with open window by issuing keystrokes.",
        "9f" : "Issue keystroke",
        "b0" : "Compares the length of v2 + B2 with the specified value.",
        "b1" : "Set a specified registry value",
        "b2" : "Delete a specified registry value",
        "b3" : "Enumerates the values within a specified registry key",
        "b4" : "Rename a specific registry key to another value",
        "b5" : "Create a specific registry key",
        "b6" : "Set a specific registry key value",
        "b7" : "Deletes a specified key",
        "b8" : "Echoes the message b8 back to the C2 ",
        "b9" : "List services and each service's status and boot method",
        "ba" : "Start or stop a service. ",
        "bb" : "Modify the configuration of a service.",
        "bc" : "Creates a service using specified name, description and binary path",
        "bd" : "Determines available network locations (TCP and UDP) by calling the GetExtendedTcpTable and GetExtendedUdpTable API functions ",
        "be" : "List running processes.",
        "bf" : "Terminate a specified process",
        "c0" : "Gathers system information, such as operating system version, CPU name and speed, physical memory and amount available, current process ID, as well as data saved to the clipboard.",
        "c1" : "Uninstall Evilgrab.",
        "c2" : "Stop Evilgrab's main thread, effectively killing Evilgrab until next reboot",
        "c3" : "Same as c2 command",
        "c5" : "Create a temporary file.",
        "e0" : "Closes an open TCP connection that matches a specified network location. This command uses the SetTcpEntry function to close a connection.",
        "e1" : "Take a single screenshot",
        "e2" : "Take a single screenshot",
        "e3" : "Starts video capture using single screenshots.",
        "e4" : "Echoes the message e4 back to the C2",
        "e5" : "Starts video capture using single screenshots.",
        "e6" : "List contents of a folder.",
        "e9" : "Sets up proxy communication point between the C2 and another specified network location over a specified TCP port.",
        "ea" : "Closes the thread responsible for the proxy communications set up in the e9 command",
        "ec" : "Sets up the VideoInputDeviceCategory class for video capture",
        "ed" : "Closes a Window, appears to stop the video capture using VideoInputDeviceCategory",
        "ee" : "Starts video capture using the VideoInputDeviceCategory class",
        "f0" : "Starts audio capture that it sends directly to the C2",
        "f1" : "Appears to stop the audio capture",
        "f2" : "Search for specific files and exfiltrate their contents.",
        "f5" : "Stops the thread that was created in command f2 to exfiltrate files by setting a specific flag (mainDataStructure[800])"
}

    module_data['exfil_types'] = {
        "20" : "Initial beacon using fake HTTP request",
        "a0" : "initial exfil after the fake HTTP request", 
        "a2" : "Notification that a removable drive is connected (0 for no 1 for yes)",
        "5c" : "Exfiltration of system information",
        "50" : "Exfiltration of clipboard data",
        "51" : "Exfiltration of a single file",
        "e7" : "Folder from list files and folders command",
        "e8" : "File from list files and folders command",
        "f4" : "Start or finish of file exfiltration",
        "2e" : "Reverse Shell 30 = Failed. 31 = Success. 32 = Closed",
        "2f" : "Output from reverse shell",
        "ae" : "Service related tasks succeeded or failed",
        "ad" : "Queried service status or type",
        "af" : "System idle time",
        "34" : "Listed processes and modules"
}
    return module_options

def handleStream(tcp):
  chop.tsprnt('')
  chop.tsprnt('--------------------------------')

  if tcp.client.count_new >= 5:
    chop.tsprnt("%s:%d -> %s:%d" % (tcp.addr[1][0],tcp.addr[1][1],tcp.addr[0][0],tcp.addr[0][1]))

    len_client = struct.unpack('<I', tcp.client.data[0:4])[0]
    if len_client > len(tcp.client.data):
        if tcp.client.data.startswith("HTTP/1.1 301 Moved Permanently\r\nLocation:http://windowsupdate.microsoft.com/\r\nContent-Type: text/html\r\nConnection: Keep-Alive\r\n\r\n<h1>Bad Request (Invalid Verb)</h1>"):
            chop.tsprnt("Server responded with anomalous HTTP 301 message that Evilgrab uses to determine legitimate Evilgrab C2")
            tcp.discard(tcp.client.count_new)
            return
        else:
            chop.tsprnt("Server len of %d greater than data available %d. Returning as its not a command" % (len_client,len(tcp.client.data)))
            tcp.discard(tcp.client.count_new)
            return

    try:
        ## Evilgrab can chain commands together in a session.
        ## lets walk through the the commands
        ## starting after the first one of course
        c = 0
        while c < tcp.client.count_new:
            length = struct.unpack('<I', tcp.client.data[c:c+4])[0]
            command = tcp.client.data[c+4]
            payload = ""
            if length > 1:
                payload = tcp.client.data[c+5:c+5+length-1]
            chop.tsprnt("Server: len %x command %x" % (length,ord(command)))
            decode_command('server', command, payload, tcp.module_data['commands'])
            c += 4+length
    except Exception as e:
        chop.tsprnt("Could not parse additional commands: %s" % e)

  elif tcp.server.count_new >= 5:
    chop.tsprnt("%s:%d -> %s:%d" % (tcp.addr[0][0],tcp.addr[0][1],tcp.addr[1][0],tcp.addr[1][1]))
    len_server = struct.unpack('<I', tcp.server.data[0:4])[0]
    if len_server > len(tcp.server.data):
        chop.tsprnt("Client len of %x greater than data available %d. Returning as its not a command" % (len_server,len(tcp.server.data)))
        tcp.discard(tcp.server.count_new)
        return
    command_server = tcp.server.data[4]
    payload_server = tcp.server.data[5:5+len_server-1]
    #chop.tsprnt("Client: len %x command %x" % (len_server,ord(command_server)))

    decode_command('client', command_server, payload_server, tcp.module_data['exfil_types'])

  else:
    #tcp.discard(tcp.server.count_new)
    return

  return


def shutdown(module_data):
    return


def taste(tcp):
    return True


def teardown(tcp):
    return