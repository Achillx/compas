from __future__ import print_function
from __future__ import absolute_import
from __future__ import division

import os
import time
import json

try:
    from xmlrpclib import ServerProxy
except ImportError:
    from xmlrpc.client import ServerProxy

from subprocess import Popen

import compas

from compas.utilities import DataEncoder
from compas.utilities import DataDecoder

from compas.rpc import RPCServerError


__all__ = ['Proxy']


class Proxy(object):

    def __init__(self, package=None):
        self._package = package
        self._function = None
        self._process = None
        self._python = 'pythonw'
        self._port = 8888
        self._url = 'http://127.0.0.1'
        self._service = 'default.py'
        self._server = None
        self.profile = None
        self.stop_server()
        self.start_server()

    def __del__(self):
        self.stop_server()

    def start_server(self):
        python = self._python
        script = os.path.join(compas.HOME, 'services', self._service)
        address = "{}:{}".format(self._url, self._port)

        self._process = Popen([python, script])
        self._server = ServerProxy(address)

        success = False
        count = 100
        while count:
            try:
                self._server.ping()
            except:
                time.sleep(0.01)
                count -= 1
            else:
                success = True
                break
        if not success:
            raise RPCServerError("The server is no available.")

    def stop_server(self):
        try:
            self._server.kill()
        except:
            pass
        try:
            self._process.terminate()
        except:
            pass
        try:
            self._process.kill()
        except:
            pass

    def __getattr__(self, name):
        if self._package:
            name = "{}.{}".format(self._package, name)
        try:
            self._function = getattr(self._server, name)
        except:
            raise RPCServerError()
        return self.proxy

    def proxy(self, *args, **kwargs):
        idict = {'args': args, 'kwargs': kwargs}
        istring = json.dumps(idict, cls=DataEncoder)

        # if self.serializer == 'json':
        #     with open(self.ipath, 'w+') as fo:
        #         json.dump(idict, fo, cls=DataEncoder)
        # else:
        #     with open(self.ipath, 'wb+') as fo:
        #         # pickle.dump(idict, fo, protocol=pickle.HIGHEST_PROTOCOL)
        #         pickle.dump(idict, fo, protocol=2)

        try:
            ostring = self._function(istring)
        except:
            self.stop_server()
            raise

        if not ostring:
            raise RPCServerError("No output was generated.")

        result = json.loads(ostring)

        if result['error']:
            raise RPCServerError(result['error'])

        self.profile = result['profile']

        return result['data']


# ==============================================================================
# Main
# ==============================================================================

if __name__ == "__main__":
    
    import compas
    import time

    from compas.datastructures import Mesh
    from compas.plotters import MeshPlotter

    from compas.utilities import print_profile

    from compas.rpc import Proxy

    numerical = Proxy('compas.numerical')
    fd_numpy = print_profile(numerical.fd_numpy)

    mesh = Mesh.from_obj(compas.get('faces_big.obj'))

    # mesh_add_methods(Mesh, Mixin)

    mesh.update_default_vertex_attributes({'px': 0.0, 'py': 0.0, 'pz': 0.0})
    mesh.update_default_edge_attributes({'q': 1.0})

    # to use mesh_fd_numpy
    # set argtypes and rettypes
    # potentially in background

    key_index = mesh.key_index()

    xyz   = mesh.get_vertices_attributes('xyz')
    edges = [(key_index[u], key_index[v]) for u, v in mesh.edges()]
    fixed = [key_index[key] for key in mesh.vertices_where({'vertex_degree': 2})]
    q     = mesh.get_edges_attribute('q', 1.0)
    loads = mesh.get_vertices_attributes(('px', 'py', 'pz'), (0.0, 0.0, 0.0))

    xyz, q, f, l, r = fd_numpy(xyz, edges, fixed, q, loads)

    for key, attr in mesh.vertices(True):
        index = key
        attr['x'] = xyz[index][0]
        attr['y'] = xyz[index][1]
        attr['z'] = xyz[index][2]
        attr['rx'] = r[index][0]
        attr['ry'] = r[index][1]
        attr['rz'] = r[index][2]

    for index, (u, v, attr) in enumerate(mesh.edges(True)):
        attr['f'] = f[index][0]
        attr['l'] = l[index][0]

    artist = MeshPlotter(mesh, figsize=(10, 7))

    artist.draw_vertices()
    artist.draw_faces()

    artist.show()
