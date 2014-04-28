__author__ = 'efimovau'

__all__ = [
    'basePath',
    'baseOID',
    'commands',
    'mapping',
    'healStatusCmd',
    'updateInterval'
]

baseOID = '.1.3.6.1.4.1.2312.11'
updateInterval = 10

basePath = '.'

commands = [
    '/usr/sbin/gluster peer status --xml',
    '/usr/sbin/gluster volume info all --xml',
    '/usr/sbin/gluster volume status all detail --xml',
    '/usr/sbin/gluster volume list --xml',
    #'cat ' + basePath + '/peer_status.xml',
    #'cat ' + basePath + '/vol_info.xml',
    #'cat ' + basePath + '/vol_status.xml',
    #'cat ' + basePath + '/vol_list.xml'
]

mapping = {
    'type': 'subtree',
    'path': [],
    1: {'type': 'subtree',
        1: {'path': ['peerStatus', 'peer'], 'type': 'count'},
        2: {'type': 'subtree',
            1: {
                'type': 'table',
                'path': ['peerStatus', 'peer'],
                1: {'path': [], 'type': 'index'},
                2: {'path': ['hostname'], 'type': 'STRING'},
                3: {'path': ['uuid'], 'type': 'STRING'},
                4: {'path': ['connected'], 'type': 'INTEGER'},
                5: {'path': ['state'], 'type': 'INTEGER'}
            }
        }
    },
    2: {'type': 'subtree',
        1: {'path': ['volInfo', 'volumes', 'volume'], 'type': 'count'},
        2: {'type': 'subtree',
            1: {
                'type': 'table',
                'path': ['volInfo', 'volumes', 'volume'],
                1: {'path': [], 'type': 'index'},
                2: {'path': ['name'], 'type': 'STRING'},
                3: {'path': ['type'], 'type': 'INTEGER'},
                4: {'path': ['status'], 'type': 'INTEGER'},
                5: {'path': ['brickCount'], 'type': 'INTEGER'},
                6: {'path': ['distCount'], 'type': 'INTEGER'},
                7: {'path': ['stripeCount'], 'type': 'INTEGER'},
                8: {'path': ['replicaCount'], 'type': 'INTEGER'}
            }
        }
    },
    3: {'type': 'subtree',
        1: {'path': ['volStatus', 'volumes', 'volume', 'node'], 'type': 'count'},
        2: {'type': 'subtree',
            1: {
                'type': 'table',
                'path': ['volStatus', 'volumes', 'volume', 'node'],
                1: {'path': [], 'type': 'index'},
                2: {'path': ['hostname'], 'type': 'STRING'},
                3: {'path': ['path'], 'type': 'STRING'},
                4: {'path': ['status'], 'type': 'INTEGER'},
                5: {'path': ['device'], 'type': 'STRING'},
                6: {'path': ['fsName'], 'type': 'STRING'},
                7: {'path': ['sizeTotal'], 'type': 'Counter64'},
                8: {'path': ['sizeFree'], 'type': 'Counter64'},
                9: {'path': ['blockSize'], 'type': 'Counter32'}
                #10: {'path': ['volName'], 'type': 'STRING'}
            }
        }
    }
}


healStatusCmd = '/usr/sbin/gluster volume heal %(volume)s status'
#healStatusCmd = 'cat ' + basePath + '/heal_status.txt'
