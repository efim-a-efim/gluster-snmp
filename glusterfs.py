#!/usr/bin/python -u

import sys
import subprocess, shlex
import StringIO
import ElementTree as ET
from XMLCombiner import XMLCombiner
import snmp_passpersist as snmp
from settings import *


def findAllXml(tree=None, path=[]):
    ret = []
    # Find all entries in path recursively
    l = len(path)

    for el in tree.findall(path[0]):
        if l == 1:
            # final tree element
            ret.append(el)
        else:
            # go deeper into subtree
            ret.extend(findAllXml(el, path[1:]))

    return ret


def formSNMPTable(tree=None, descr={}, baseoid=''):
    ret = {}

    if descr['type'] != 'table':
        return ret
    if 'path' not in descr:
        return ret

    # Get table data recursively by path
    tableData = findAllXml(tree, descr['path'])
    # filter indexes to use in resulting tree
    indexes = [x for x in list(descr.keys()) if type(x).__name__ == 'int']

    for di in xrange(0, len(tableData)):
        # data loop
        for key in indexes:
            newoid = '%(prop)s.%(ent)s' % {'prop': str(key), 'ent': str(di+1)}
            if len(baseoid) > 0:
                newoid = '%(base)s.%(id)s' % {'base': baseoid, 'id': newoid}
            # values loop
            if descr[key]['type'] == 'index':
                # form index
                ret[newoid] = {'type': 'INTEGER', 'value': di+1}
            else:
                # form data value
                ret[newoid] = {'type': descr[key]['type'],
                               'value': findAllXml(tableData[di], descr[key]['path'])[0].text}
    return ret


def formSNMPTree(tree=None, descr={}, baseoid=''):
    ret = {}

    if 'type' not in descr:
        return ret

    if descr['type'] == 'subtree':
        # loop through subtree indexes
        for key in [x for x in list(descr.keys()) if type(x).__name__ == 'int']:
            # form oid
            newoid = '%s.%d' % (baseoid, key)
            if baseoid == '':
                newoid = '%d' % key
            # recursion through tree
            ret.update(formSNMPTree(tree, descr[key], newoid))
    elif descr['type'] == 'table':
        ret.update(formSNMPTable(tree, descr, baseoid))
    elif descr['type'] == 'count':
        if baseoid == '':
            return ret
        ret['%(base)s.0' % {'base': baseoid}] = {
            'type': 'INTEGER',
            'value': len(findAllXml(tree, descr['path']))
        }
    else:
        if baseoid == '':
            return ret
        ret['%(base)s.0' % {'base': baseoid}] = {
            'type': descr['type'],
            'value': findAllXml(tree, descr['path'])[0].text
        }

    return ret


def parseHealStatus(vol='', cmd='/usr/sbin/gluster volume heal %(volume)s status'):
    ret = {}

    # run command
    inp = subprocess.Popen(
        shlex.split(cmd % {'volume': vol}), stdout=subprocess.PIPE, stderr=subprocess.STDOUT
    ).communicate()[0].split("\n")

    # entry index
    currIndex = 1
    #            index,        host,  path,  file,  volume
    (host, brick, path, volume) = ('', '', '', vol)
    for str in inp:
        if str == '':
            # empty string - reset current data
            (host, brick) = ('', '')
        elif str.startswith('Brick '):
            # Brick entry
            (host, brick) = str.split(' ')[1].split(':')
        elif str.startswith('/'):
            # file entry
            ret['1.%d' % currIndex] = {'type': 'INTEGER', 'value': currIndex}
            ret['2.%d' % currIndex] = {'type': 'STRING', 'value': host}
            ret['3.%d' % currIndex] = {'type': 'STRING', 'value': brick}
            ret['4.%d' % currIndex] = {'type': 'STRING', 'value': str}
            ret['5.%d' % currIndex] = {'type': 'STRING', 'value': vol}
            currIndex += 1
    return ret


def updateOIDTree():
    global pp
    global commands, mapping

    inputs = []
    for cmd in commands:
        inputs.append(ET.parse(
            StringIO.StringIO(
                subprocess.Popen(shlex.split(cmd), stdout=subprocess.PIPE, stderr=subprocess.STDOUT).communicate()[0]
            )
        ).getroot()
        )

    xmlData = XMLCombiner(inputs).combine()
    snmpData = formSNMPTree(xmlData, mapping, '')

    # Special processing for heal (it doesn't give XML output)
    healCount = 0
    for vol in xmlData.find('volList').findall('volume'):
        # for each volume try to get heal status
        healSt = parseHealStatus(vol=vol.text, cmd=healStatusCmd)
        healCount += len(healSt)/5
        for oid in healSt:
            snmpData['4.2.1.%(oid)s' % {'oid': oid}] = healSt[oid]
    snmpData['4.1.0'] = { 'type': 'INTEGER', 'value': healCount }

    for oid in snmpData:
        pp.add_oid_entry(oid, snmpData[oid]['type'], snmpData[oid]['value'])

###############################################################################
if __name__ == '__main__':
    pp = snmp.PassPersist(baseOID)
    pp.start(updateOIDTree, updateInterval)
    sys.exit(0)
