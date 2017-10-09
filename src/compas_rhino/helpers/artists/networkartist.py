import time

from compas.utilities import color_to_colordict
from compas.cad import ArtistInterface

import compas_rhino

try:
    import rhinoscriptsyntax as rs
except ImportError:
    import platform
    if platform.python_implementation() == 'IronPython':
        raise


__author__    = ['Tom Van Mele', ]
__copyright__ = 'Copyright 2016 - Block Research Group, ETH Zurich'
__license__   = 'MIT License'
__email__     = 'vanmelet@ethz.ch'


__all__ = ['NetworkArtist']


class NetworkArtist(ArtistInterface):
    """"""

    def __init__(self, network, layer=None):
        self.network = network
        self.layer = layer
        self.defaults = {
            'color.vertex': (255, 0, 0),
            'color.edge'  : (0, 0, 0),
        }

    # this should be called 'update_view'
    # 'redraw' should draw the network again, with the same settings
    def redraw(self, timeout=None):
        """Redraw the Rhino view."""
        if timeout:
            time.sleep(timeout)
        rs.EnableRedraw(True)
        rs.Redraw()

    def clear_layer(self):
        """Clear the main layer of the artist."""
        if self.layer:
            compas_rhino.clear_layer(self.layer)

    def clear(self):
        self.clear_vertices()
        self.clear_edges()

    def clear_vertices(self, keys=None):
        if not keys:
            name = '{}.vertex.*'.format(self.network.attributes['name'])
            guids = compas_rhino.get_objects(name=name)
        else:
            guids = []
            for key in keys:
                name = '{}.vertex.{}'.format(self.attributes['name'], key)
                guid = compas_rhino.get_object(name=name)
                guids.append(guid)
        compas_rhino.delete_objects(guids)

    def clear_edges(self, keys=None):
        if not keys:
            name = '{}.edge.*'.format(self.network.attributes['name'])
            guids = compas_rhino.get_objects(name=name)
        else:
            guids = []
            for u, v in keys:
                name = '{}.edge.{}-{}'.format(self.attributes['name'], u, v)
                guid = compas_rhino.get_object(name=name)
                guids.append(guid)
        compas_rhino.delete_objects(guids)

    def draw_vertices(self, keys=None, color=None):
        """Draw a selection of vertices of the network.

        Parameters
        ----------
        keys : list
            A list of vertex keys identifying which vertices to draw.
            Default is ``None``, in which case all vertices are drawn.
        color : str, tuple, dict
            The color specififcation for the vertices.
            Colors should be specified in the form of a string (hex colors) or
            as a tuple of RGB components.
            To apply the same color to all vertices, provide a single color
            specification. Individual colors can be assigned using a dictionary
            of key-color pairs. Missing keys will be assigned the default vertex
            color (``self.defaults['color.vertex']``).
            The default is ``None``, in which case all vertices are assigned the
            default vertex color.

        Notes
        -----
        The vertices are named using the following template:
        ``"{}.vertex.{}".format(self.network.attributes['name'], key)``.
        This name is used afterwards to identify vertices of the networkin the Rhino model.

        Examples
        --------
        >>> artist.draw_vertices()
        >>> artist.draw_vertices(color='#ff0000')
        >>> artist.draw_vertices(color=(255, 0, 0))
        >>> artist.draw_vertices(keys=self.network.vertices_on_boundary())
        >>> artist.draw_vertices(color={(u, v): '#00ff00' for u, v in self.network.vertices_on_boundary()})

        """
        keys = keys or list(self.network.vertices())
        colordict = color_to_colordict(color, keys, default=self.defaults['color.vertex'])
        points = []
        for key in keys:
            points.append({
                'pos'  : self.network.vertex_coordinates(key),
                'name' : self.network.vertex_name(key),
                'color': colordict[key]
            })
        return compas_rhino.xdraw_points(points, layer=self.layer, clear=False, redraw=False)

    def draw_edges(self, keys=None, color=None):
        """Draw a selection of edges of the network.

        Parameters
        ----------
        keys : list
            A list of edge keys (as uv pairs) identifying which edges to draw.
            The default is ``None``, in which case all edges are drawn.
        color : str, tuple, dict
            The color specififcation for the edges.
            Colors should be specified in the form of a string (hex colors) or
            as a tuple of RGB components.
            To apply the same color to all faces, provide a single color
            specification. Individual colors can be assigned using a dictionary
            of key-color pairs. Missing keys will be assigned the default face
            color (``self.defaults['face.color']``).
            The default is ``None``, in which case all faces are assigned the
            default vertex color.

        Notes
        -----
        All edges are named using the following template:
        ``"{}.edge.{}-{}".fromat(self.network.attributes['name'], u, v)``.
        This name is used afterwards to identify edges of the network in the Rhino model.

        Examples
        --------
        >>> artist.draw_edges()
        >>> artist.draw_edges(color='#ff0000')
        >>> artist.draw_edges(color=(255, 0, 0))
        >>> artist.draw_edges(keys=self.network.edges_xxx())
        >>> artist.draw_edges(color={(u, v): '#00ff00' for u, v in self.network.edges_xxx()})

        """
        keys = keys or list(self.network.edges())
        colordict = to_valuedict(keys, color, self.defaults['color.edge'])
        lines = []
        for u, v in keys:
            lines.append({
                'start': self.network.vertex_coordinates(u),
                'end'  : self.network.vertex_coordinates(v),
                'color': colordict[(u, v)],
                'name' : self.network.edge_name(u, v)
            })
        return compas_rhino.xdraw_lines(lines, layer=self.layer, clear=False, redraw=False)

    def draw_path(self, path):
        """Draw a path from one vertex to another as a polyline of edges.

        Parameters
        ----------
        path : list
            A list of ordered vertices forming a vaild path on the network.

        Notes
        -----

        Examples
        --------
        >>>

        """
        pass

    def draw_vertexlabels(self, text=None, color=None):
        """Draw labels for selected vertices of the network.

        Parameters
        ----------
        text : dict
            A dictionary of vertex labels as key-text pairs.
            The default value is ``None``, in which case every vertex of the network
            will be labelled with its key.
        color : str, tuple, dict
            The color sepcification of the labels.
            String values are interpreted as hex colors (e.g. ``'#ff0000'`` for red).
            Tuples are interpreted as RGB component specifications (e.g. ``(255, 0, 0) for red``.
            If a dictionary of specififcations is provided, the keys of the
            should refer to vertex keys in the network and the values should be color
            specifications in the form of strings or tuples.
            The default value is ``None``, in which case the labels are assigned
            the default vertex color (``self.defaults['color.vertex']``).

        Notes
        -----
        All labels are assigned a name using the folling template:
        ``"{}.vertex.{}".format(self.network.attributes['name'], key)``.

        Examples
        --------
        >>>

        """
        if text is None:
            textdict = {key: str(key) for key in self.network.vertices()}
        elif isinstance(text, dict):
            textdict = text
        else:
            raise NotImplementedError
        colordict = to_valuedict(list(textdict.keys()), color, self.defaults['color.vertex'])
        labels = []
        for key, text in iter(textdict.items()):
            labels.append({
                'pos'  : self.network.vertex_coordinates(key),
                'name' : self.network.vertex_name(key),
                'color': colordict[key],
                'text' : textdict[key],
            })
        return compas_rhino.xdraw_labels(labels, layer=self.layer, clear=False, redraw=False)

    def draw_edgelabels(self, text=None, color=None):
        """Draw labels for selected edges of the network.

        Parameters
        ----------

        Notes
        -----

        Examples
        --------
        >>>

        """
        if text is None:
            textdict = {(u, v): "{}-{}".format(u, v) for u, v in self.network.edges()}
        elif isinstance(text, dict):
            textdict = text
        else:
            raise NotImplementedError
        colordict = to_valuedict(list(textdict.keys()), color, self.defaults['color.edge'])
        labels = []
        for (u, v), text in iter(textdict.items()):
            labels.append({
                'pos'  : self.network.edge_midpoint(u, v),
                'name' : self.network.edge_name(u, v),
                'color': colordict[(u, v)],
                'text' : textdict[(u, v)],
            })
        return compas_rhino.xdraw_labels(labels, layer=self.layer, clear=False, redraw=False)


# ==============================================================================
# Debugging
# ==============================================================================

if __name__ == "__main__":

    import compas
    from compas.datastructures import Network
    from compas_rhino.helpers.artists.networkartist import NetworkArtist

    network = Network.from_obj(compas.get_data('grid_irregular.obj'))

    artist = NetworkArtist(network, layer='NetworkArtist')

    artist.clear_layer()

    artist.draw_vertices()
    artist.redraw(0.0)

    artist.draw_vertexlabels()
    artist.redraw(1.0)

    artist.draw_edges()
    artist.redraw(1.0)

    artist.draw_edgelabels()
    artist.redraw(1.0)
