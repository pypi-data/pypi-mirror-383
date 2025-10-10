# SPDX-FileCopyrightText: 2025 Autodesk, Inc.
# SPDX-License-Identifier: Apache-2.0

"""
Usage:
    MeshEditor Class API Wrapper
"""

# pylint: disable=C0302

from .logger import process_log
from .common import LogMessage
from .ent_list import EntList
from .vector import Vector
from .prop import Property
from .helper import check_type, check_range, check_is_non_negative, coerce_optional_dispatch
from .com_proxy import safe_com


class MeshEditor:
    """
    Wrapper for MeshEditor class of Moldflow Synergy.
    """

    def __init__(self, _mesh_editor):
        """
        Initialize the MeshEditor with a MeshEditor instance from COM.

        Args:
            _mesh_editor: The MeshEditor instance.
        """
        process_log(__name__, LogMessage.CLASS_INIT, locals(), name="MeshEditor")
        self.mesh_editor = safe_com(_mesh_editor)

    def auto_fix(self) -> int:
        """
        Attempts to repair the mesh by automatically removing overlaps and intersections

        Returns:
            int: The number of elements repaired
        """
        process_log(__name__, LogMessage.FUNCTION_CALL, locals(), name="auto_fix")
        return self.mesh_editor.AutoFix

    def purge_nodes(self) -> int:
        """
        Deletes nodes in the model that are not connected to any elements

        Returns:
            int: The number of nodes deleted
        """
        process_log(__name__, LogMessage.FUNCTION_CALL, locals(), name="purge_nodes")
        return self.mesh_editor.PurgeNodes

    def create_entity_list(self) -> EntList:
        """
        Creates a new entity list in the model.
        When using this function, it will first ask for result invalidation.
        If you want to select entities without checking result, use study_doc.create_entity_list().
        Returns:
            The new entity list.
        """
        process_log(__name__, LogMessage.FUNCTION_CALL, locals(), name="create_entity_list")
        result = self.mesh_editor.CreateEntityList
        if result is None:
            return None
        return EntList(result)

    def swap_edge(
        self, tri1: EntList | None, tri2: EntList | None, feat_allow: bool = False
    ) -> bool:
        """
        Swaps the common edge between two triangles

        Args:
            tri1 (EntList | None): EntList object containing the first triangle
            tri2 (EntList | None): EntList object containing the second triangle
            feat_allow (bool): specify True to permit modifications of feature edges
        Returns:
            True if operation is successful; False otherwise
        """
        process_log(__name__, LogMessage.FUNCTION_CALL, locals(), name="swap_edges")
        if tri1 is not None:
            check_type(tri1, EntList)
        if tri2 is not None:
            check_type(tri2, EntList)
        check_type(feat_allow, bool)
        return self.mesh_editor.SwapEdge(
            coerce_optional_dispatch(tri1, "ent_list"),
            coerce_optional_dispatch(tri2, "ent_list"),
            feat_allow,
        )

    def stitch_free_edges(self, nodes: EntList | None, tolerance: float) -> bool:
        """
        Stitches free edges within a given tolerance by providing a set of nodes

        Args:
            nodes (EntList | None): EntList object containing the nodes
            tolerance (float): float Tolerance

        Returns:
            True if successful False otherwise
        """
        process_log(__name__, LogMessage.FUNCTION_CALL, locals(), name="stitch_free_edges")
        check_type(tolerance, float)
        if nodes is not None:
            check_type(nodes, EntList)
        return self.mesh_editor.StitchFreeEdges2(
            coerce_optional_dispatch(nodes, "ent_list"), tolerance
        )

    def insert_node(self, node1: EntList | None, node2: EntList | None) -> EntList:
        """
        Inserts a node between two existing nodes.
        Args:
            node1 (EntList | None): EntList object containing the first node
            node2 (EntList | None): EntList object containing the second node

        Returns:
            The new node.
        """
        process_log(__name__, LogMessage.FUNCTION_CALL, locals(), name="insert_node")
        if node1 is not None:
            check_type(node1, EntList)
        if node2 is not None:
            check_type(node2, EntList)
        result = self.mesh_editor.InsertNode(
            coerce_optional_dispatch(node1, "ent_list"), coerce_optional_dispatch(node2, "ent_list")
        )
        if result is None:
            return None
        return EntList(result)

    def insert_node_in_tri(
        self, node1: EntList | None, node2: EntList | None = None, node3: EntList | None = None
    ) -> EntList:
        """
        Inserts a node in the centroid of a given triangle

        Provide 1 Entlist containing 3 nodes or 3 Entlist containing 1 node each.

        Args:
            node1 (EntList | None): EntList object containing the first node
            node2 (EntList | None): EntList object containing the second node
            node3 (EntList | None): EntList object containing the third node

        Returns:
            The new node at the centroid of triangle.
        """
        process_log(__name__, LogMessage.FUNCTION_CALL, locals(), name="insert_node_in_tri")
        if node1 is not None:
            check_type(node1, EntList)

        if node2 is None and node3 is None:
            check_range(node1.size, 3, 3, True, True)
            result = self.mesh_editor.InsertNodeInTri2(coerce_optional_dispatch(node1, "ent_list"))
            if result is None:
                return None
            return EntList(result)

        if node2 is not None:
            check_type(node2, EntList)
        if node3 is not None:
            check_type(node3, EntList)

        result = self.mesh_editor.InsertNodeInTri(
            coerce_optional_dispatch(node1, "ent_list"),
            coerce_optional_dispatch(node2, "ent_list"),
            coerce_optional_dispatch(node3, "ent_list"),
        )

        if result is None:
            return None
        return EntList(result)

    def insert_node_in_tet(
        self,
        node1: EntList | None,
        node2: EntList | None = None,
        node3: EntList | None = None,
        node4: EntList | None = None,
    ) -> EntList:
        """
        Inserts a node in the centroid of a given tetrahedron

        Provide 1 Entlist containing 4 nodes or 4 Entlist containing 1 node each.

        Args:
            node1 (EntList | None): EntList object containing the first node
            node2 (EntList | None): EntList object containing the second node
            node3 (EntList | None): EntList object containing the third node
            node4 (EntList | None): EntList object containing the fourth node

        Returns:
            The new node at the centroid of tetrahedron.
        """
        process_log(__name__, LogMessage.FUNCTION_CALL, locals(), name="insert_node_in_tet")
        if node1 is not None:
            check_type(node1, EntList)
        if node2 is None or node3 is None or node4 is None:
            check_range(node1.size, 4, 4, True, True)
            result = self.mesh_editor.InsertNodeInTet(coerce_optional_dispatch(node1, "ent_list"))
            if result is None:
                return None
            return EntList(result)
        if node2 is not None:
            check_type(node2, EntList)
        if node3 is not None:
            check_type(node3, EntList)
        if node4 is not None:
            check_type(node4, EntList)
        result = self.mesh_editor.InsertNodeInTetByNodes(
            coerce_optional_dispatch(node1, "ent_list"),
            coerce_optional_dispatch(node2, "ent_list"),
            coerce_optional_dispatch(node3, "ent_list"),
            coerce_optional_dispatch(node4, "ent_list"),
        )
        if result is None:
            return None
        return EntList(result)

    def insert_node_in_tet_by_nodes(
        self,
        node1: EntList | None,
        node2: EntList | None,
        node3: EntList | None,
        node4: EntList | None,
    ) -> EntList:
        """
        DEPRECATED: Use insert_node_in_tet instead.
        Inserts a node in the centroid of a given tetrahedron

        Args:
            node1 (EntList | None): EntList object containing the first node
            node2 (EntList | None): EntList object containing the second node
            node3 (EntList | None): EntList object containing the third node
            node4 (EntList | None): EntList object containing the fourth node

        Returns:
            The new node at the centroid of tetrahedron.
        """
        process_log(
            __name__, LogMessage.FUNCTION_CALL, locals(), name="insert_node_in_tet_by_nodes"
        )
        if node1 is not None:
            check_type(node1, EntList)
        if node2 is not None:
            check_type(node2, EntList)
        if node3 is not None:
            check_type(node3, EntList)
        if node4 is not None:
            check_type(node4, EntList)
        result = self.mesh_editor.InsertNodeInTetByNodes(
            coerce_optional_dispatch(node1, "ent_list"),
            coerce_optional_dispatch(node2, "ent_list"),
            coerce_optional_dispatch(node3, "ent_list"),
            coerce_optional_dispatch(node4, "ent_list"),
        )
        if result is None:
            return None
        return EntList(result)

    def insert_node_on_beam(self, beam: EntList | None, num_div: int = 2) -> EntList:
        """
        Inserts nodes on a beam.
        Args:
            beam (EntList | None): EntList object containing the beam
            num_div (int): Number of divisions to be created along the beam. Default is 2.

        Returns:
            Entlist of the new node.
        """
        process_log(__name__, LogMessage.FUNCTION_CALL, locals(), name="insert_node_on_beam")
        if beam is not None:
            check_type(beam, EntList)
        check_type(num_div, int)
        check_is_non_negative(num_div)
        result = self.mesh_editor.InsertNodeOnBeam(
            coerce_optional_dispatch(beam, "ent_list"), num_div
        )
        if result is None:
            return None
        return EntList(result)

    def move_nodes(self, nodes: EntList | None, vector: Vector | None, loc: bool) -> bool:
        """
        Moves nodes to a new location or by an offset
        Args:
            nodes (EntList | None): EntList object containing the nodes to be moved
            vector (Vector | None): Vector object that specifies the destination location or an
                offset vector
            loc (bool): specify True to specify a location and False to to specify an offset vector
        Returns:
            True if successful; False otherwise.
        """
        process_log(__name__, LogMessage.FUNCTION_CALL, locals(), name="move_nodes")
        if nodes is not None:
            check_type(nodes, EntList)
        if vector is not None:
            check_type(vector, Vector)
        check_type(loc, bool)
        return self.mesh_editor.MoveNodes(
            coerce_optional_dispatch(nodes, "ent_list"),
            coerce_optional_dispatch(vector, "vector"),
            loc,
        )

    def align_nodes(
        self, node1: EntList | None, node2: EntList | None, to_align: EntList | None
    ) -> bool:
        """
        Aligns a set of nodes so that they are collinear with a given pair of nodes

        Args:
            node1 (EntList | None): EntList object containing the first node
            node2 (EntList | None): EntList object containing the second node
            to_align (EntList | None): EntList object containing nodes that are to be
                aligned between node1 and node2

        Returns:
            True if operation is successful; False otherwise
        """
        process_log(__name__, LogMessage.FUNCTION_CALL, locals(), name="align_nodes")
        if node1 is not None:
            check_type(node1, EntList)
        if node2 is not None:
            check_type(node2, EntList)
        if to_align is not None:
            check_type(to_align, EntList)
        return self.mesh_editor.AlignNodes(
            coerce_optional_dispatch(node1, "ent_list"),
            coerce_optional_dispatch(node2, "ent_list"),
            coerce_optional_dispatch(to_align, "ent_list"),
        )

    def smooth_nodes(self, nodes: EntList | None, feat: bool) -> bool:
        """
        Performs Laplacian smoothing on a set of nodes

        Args:
            nodes (EntList | None): EntList object containing the nodes to be smoothed
            feat (bool): specify True to preserve feature edges during smoothing

        Returns:
            True if operation is successful; False otherwise
        """
        process_log(__name__, LogMessage.FUNCTION_CALL, locals(), name="smooth_nodes")
        if nodes is not None:
            check_type(nodes, EntList)
        check_type(feat, bool)
        return self.mesh_editor.SmoothNodes(coerce_optional_dispatch(nodes, "ent_list"), feat)

    def orient(self, fusion: bool) -> bool:
        """
        Orients the mesh

        Args:
            fusion (bool): specify True if the mesh if for a fusion model

        Returns:
            True if operation is successful; False otherwise
        """
        process_log(__name__, LogMessage.FUNCTION_CALL, locals(), name="orient")
        check_type(fusion, bool)
        return self.mesh_editor.Orient(fusion)

    def flip_normals(self, tris: EntList | None) -> bool:
        """
        Flips triangle normals

        Args:
            tris (EntList | None): EntList object containing the triangles whose normals are
                to be flipped

        Returns:
            True if operation is successful; False otherwise
        """
        process_log(__name__, LogMessage.FUNCTION_CALL, locals(), name="flip_normals")
        if tris is not None:
            check_type(tris, EntList)
        return self.mesh_editor.FlipNormals(coerce_optional_dispatch(tris, "ent_list"))

    def align_normals(self, seed_tri: EntList | None, tris: EntList | None) -> int:
        """
        Aligns the normals of a set of triangles to match a seed triangle

        Args:
            seed_tri (EntList | None): EntList object containing the seed triangle
            tris (EntList | None): EntList object containing the triangles whose normals are
                to be aligned

        Returns:
            Number of triangles whose normals were aligned
        """
        process_log(__name__, LogMessage.FUNCTION_CALL, locals(), name="align_normals")
        if seed_tri is not None:
            check_type(seed_tri, EntList)
        if tris is not None:
            check_type(tris, EntList)
        return self.mesh_editor.AlignNormals(
            coerce_optional_dispatch(seed_tri, "ent_list"),
            coerce_optional_dispatch(tris, "ent_list"),
        )

    def fill_hole(self, nodes: EntList | None, fill_type: int | None = None) -> bool:
        """
        Fill a "hole" in the mesh by creating triangles between given nodes
        If fill_type provided, fill a "hole" in the mesh by creating new triangles

        Args:
            nodes (EntList | None): EntList ordered sequence of nodes defining the outer
                boundary of the hole
            fill_type (int, optional): Default is 0, triangles around the hole will be bent.

        Returns:
            True if operation is successful; False otherwise
        """
        process_log(__name__, LogMessage.FUNCTION_CALL, locals(), name="fill_hole")
        if nodes is not None:
            check_type(nodes, EntList)
        if fill_type is None:
            return self.mesh_editor.FillHole(coerce_optional_dispatch(nodes, "ent_list"))
        check_type(fill_type, int)
        return self.mesh_editor.FillHole2(coerce_optional_dispatch(nodes, "ent_list"), fill_type)

    # pylint: disable-next=R0913, R0917
    def create_tet(
        self,
        node1: EntList | None,
        node2: EntList | None,
        node3: EntList | None,
        node4: EntList | None,
        prop: Property | None,
    ) -> EntList:
        """
        Creates a tetrahedron from 4 nodes and a property

        Args:
            node1 (EntList | None): EntList object containing the first node
            node2 (EntList | None): EntList object containing the second node
            node3 (EntList | None): EntList object containing the third node
            node4 (EntList | None): EntList object containing the fourth node
            prop (Property | None): Property object containing the property of the tetrahedron

        Returns:
            The new tetrahedron.
        """
        process_log(__name__, LogMessage.FUNCTION_CALL, locals(), name="create_tet")
        if node1 is not None:
            check_type(node1, EntList)
        if node2 is not None:
            check_type(node2, EntList)
        if node3 is not None:
            check_type(node3, EntList)
        if node4 is not None:
            check_type(node4, EntList)
        if prop is not None:
            check_type(prop, Property)
        prop_disp = coerce_optional_dispatch(prop, "prop")
        result = self.mesh_editor.CreateTet(
            coerce_optional_dispatch(node1, "ent_list"),
            coerce_optional_dispatch(node2, "ent_list"),
            coerce_optional_dispatch(node3, "ent_list"),
            coerce_optional_dispatch(node4, "ent_list"),
            prop_disp,
        )
        if result is None:
            return None
        return EntList(result)

    def create_tri(
        self,
        node1: EntList | None,
        node2: EntList | None,
        node3: EntList | None,
        prop: Property | None,
    ) -> EntList:
        """
        Creates a tetrahedron from 4 nodes and a property

        Args:
            node1 (EntList | None): EntList object containing the first node
            node2 (EntList | None): EntList object containing the second node
            node3 (EntList | None): EntList object containing the third node
            prop (Property | None): Property object containing the property of the triangle

        Returns:
            The new triangle
        """
        process_log(__name__, LogMessage.FUNCTION_CALL, locals(), name="create_tri")
        if node1 is not None:
            check_type(node1, EntList)
        if node2 is not None:
            check_type(node2, EntList)
        if node3 is not None:
            check_type(node3, EntList)
        if prop is not None:
            check_type(prop, Property)
        prop_disp = coerce_optional_dispatch(prop, "prop")
        result = self.mesh_editor.CreateTri(
            coerce_optional_dispatch(node1, "ent_list"),
            coerce_optional_dispatch(node2, "ent_list"),
            coerce_optional_dispatch(node3, "ent_list"),
            prop_disp,
        )
        if result is None:
            return None
        return EntList(result)

    def refine_tetras(
        self, tet_ref_layer: int, num_layer: int, refine_surface: bool, surface_edge_length: float
    ) -> bool:
        """
        Refine selected tetras

        Args:
            tet_ref_layer (int): Layer ID
            num_layer (int): Number of layers
            refine_surface (bool): specify True to refine the surface mesh
            surface_edge_length (float): Length of the edge of the surface mesh

        Returns:
            True if operation is successful; False otherwise
        """
        process_log(__name__, LogMessage.FUNCTION_CALL, locals(), name="refine_tetras")
        check_type(tet_ref_layer, int)
        check_type(num_layer, int)
        check_is_non_negative(num_layer)
        check_is_non_negative(tet_ref_layer)
        check_type(refine_surface, bool)
        check_type(surface_edge_length, (int, float))
        return self.mesh_editor.RefineTetras(
            tet_ref_layer, num_layer, refine_surface, surface_edge_length
        )

    # pylint: disable-next=R0913, R0917
    def refine_tetras_by_labels(
        self,
        nodes: EntList | None,
        num_layer: int,
        isolate_refined_tet: bool,
        refine_surface: bool,
        surface_edge_length: float,
    ) -> bool:
        """
        Refine selected tetras by labels

        Args:
            nodes (EntList | None): EntList object containing the nodes to be refined
            num_layer (int): Number of layers
            isolate_refined_tet (bool): specify True to isolate the refined tetras
            refine_surface (bool): specify True to refine the surface mesh
            surface_edge_length (float): Length of the edge of the surface mesh

        Returns:
            True if operation is successful; False otherwise
        """
        process_log(__name__, LogMessage.FUNCTION_CALL, locals(), name="refine_tetras_by_labels")
        if nodes is not None:
            check_type(nodes, EntList)
        check_type(num_layer, int)
        check_is_non_negative(num_layer)
        check_type(isolate_refined_tet, bool)
        check_type(refine_surface, bool)
        check_type(surface_edge_length, (int, float))
        return self.mesh_editor.RefineTetrasByLabels(
            coerce_optional_dispatch(nodes, "ent_list"),
            num_layer,
            isolate_refined_tet,
            refine_surface,
            surface_edge_length,
        )

    # pylint: disable-next=R0913, R0917
    def create_wedge(
        self,
        node1: EntList | None,
        node2: EntList | None,
        node3: EntList | None,
        node4: EntList | None,
        node5: EntList | None,
        node6: EntList | None,
        prop: Property | None,
    ) -> EntList:
        """
        Creates a wedge from 6 nodes and a property

        Args:
            node1 (EntList | None): EntList object containing the first node
            node2 (EntList | None): EntList object containing the second node
            node3 (EntList | None): EntList object containing the third node
            node4 (EntList | None): EntList object containing the fourth node
            node5 (EntList | None): EntList object containing the fifth node
            node6 (EntList | None): EntList object containing the sixth node
            prop (Property | None): Property object containing the property of the wedge

        Returns:
            The new wedge.
        """
        process_log(__name__, LogMessage.FUNCTION_CALL, locals(), name="create_wedge")
        if node1 is not None:
            check_type(node1, EntList)
        if node2 is not None:
            check_type(node2, EntList)
        if node3 is not None:
            check_type(node3, EntList)
        if node4 is not None:
            check_type(node4, EntList)
        if node5 is not None:
            check_type(node5, EntList)
        if node6 is not None:
            check_type(node6, EntList)
        if prop is not None:
            check_type(prop, Property)
        result = self.mesh_editor.CreateWedge(
            coerce_optional_dispatch(node1, "ent_list"),
            coerce_optional_dispatch(node2, "ent_list"),
            coerce_optional_dispatch(node3, "ent_list"),
            coerce_optional_dispatch(node4, "ent_list"),
            coerce_optional_dispatch(node5, "ent_list"),
            coerce_optional_dispatch(node6, "ent_list"),
            coerce_optional_dispatch(prop, "prop"),
        )

        if result is None:
            return None
        return EntList(result)

    def convert_wedges_to_tetras(self, wedges: EntList | None, num_layer: int) -> bool:
        """
        Converts wedges to tetras

        Args:
            wedges (EntList | None): EntList object containing the wedges to be converted
            num_layer (int): Number of layers

        Returns:
            True if operation is successful; False otherwise
        """
        process_log(__name__, LogMessage.FUNCTION_CALL, locals(), name="convert_wedges_to_tetras")
        if wedges is not None:
            check_type(wedges, EntList)
        check_type(num_layer, int)
        check_is_non_negative(num_layer)
        return self.mesh_editor.ConvertWedgesToTetras(
            coerce_optional_dispatch(wedges, "ent_list"), num_layer
        )

    def create_beams(
        self, node1: EntList | None, node2: EntList | None, num_beams: int, prop: Property | None
    ) -> EntList:
        """
        Creates a beam between two nodes

        Args:
            node1 (EntList | None): EntList object containing the first node
            node2 (EntList | None): EntList object containing the second node
            num_beams (int): Number of beams to be created
            prop (Property | None): Property object containing the property of the beam

        Returns:
            The new beam.
        """
        process_log(__name__, LogMessage.FUNCTION_CALL, locals(), name="create_beams")
        if node1 is not None:
            check_type(node1, EntList)
        if node2 is not None:
            check_type(node2, EntList)
        check_type(num_beams, int)
        check_is_non_negative(num_beams)
        if prop is not None:
            check_type(prop, Property)
        result = self.mesh_editor.CreateBeams(
            coerce_optional_dispatch(node1, "ent_list"),
            coerce_optional_dispatch(node2, "ent_list"),
            num_beams,
            coerce_optional_dispatch(prop, "prop"),
        )

        if result is None:
            return None
        return EntList(result)

    def find_property(self, prop_type: int, prop_id: int) -> Property:
        """
        Finds a property by type and ID

        Args:
            prop_type (int): Property type
            prop_id (int): Property ID

        Returns:
            The Property.
        """
        process_log(__name__, LogMessage.FUNCTION_CALL, locals(), name="find_property")
        check_type(prop_type, int)
        check_type(prop_id, int)
        result = self.mesh_editor.FindProperty(prop_type, prop_id)
        if result is None:
            return None
        return Property(result)

    def delete(self, entities: EntList | None) -> EntList:
        """
        Deletes a set of entities

        Args:
            entities (EntList | None): EntList object containing entities to be deleted

        Returns:
            EntList object containing entities that were not deleted
            If you attempt to delete nodes that are referenced
            by elements or boundary conditions, these will not be deleted.
            You would need to delete the dependent entities first
        """
        process_log(__name__, LogMessage.FUNCTION_CALL, locals(), name="delete")
        if entities is not None:
            check_type(entities, EntList)
        result = self.mesh_editor.Delete(coerce_optional_dispatch(entities, "ent_list"))
        if result is None:
            return None
        return EntList(result)

    def remesh_area(
        self, tris: EntList | None, size: float, imprint: bool = False, smooth: float = 0.0
    ) -> bool:
        """
        Remesh a set of triangles

        Args:
            tris (EntList | None): EntList object containing the triangles to be remeshed
            size (float): Size of the new mesh
            imprint (bool): specify True to imprint the mesh onto the surface mesh
            smooth (float): smoothing factor (0.0 to 1.0)

        Returns:
            True if operation is successful; False otherwise
        """
        process_log(__name__, LogMessage.FUNCTION_CALL, locals(), name="remesh_area")
        if tris is not None:
            check_type(tris, EntList)
        check_type(size, (int, float))
        check_type(imprint, bool)
        check_type(smooth, (int, float))
        check_range(smooth, 0.0, 1.0, True, True)
        return self.mesh_editor.RemeshArea2(
            coerce_optional_dispatch(tris, "ent_list"), size, imprint, smooth
        )

    def match_nodes(self, nodes: EntList | None, tris: EntList | None, layer: str) -> int:
        """
        Matches the nodes of a set of triangles to a set of nodes

        Args:
            nodes (EntList | None): EntList object containing the nodes to be matched
            tris (EntList | None): EntList object containing the triangles to be matched
            layer (str): name of the layer to which newly created nodes will be assigned.
            Specify an empty string ("") to create nodes in the currently active layer.

        Returns:
            Number of nodes affected
        """
        process_log(__name__, LogMessage.FUNCTION_CALL, locals(), name="match_notes")
        if nodes is not None:
            check_type(nodes, EntList)
        if tris is not None:
            check_type(tris, EntList)
        check_type(layer, str)
        return self.mesh_editor.MatchNodes(
            coerce_optional_dispatch(nodes, "ent_list"),
            coerce_optional_dispatch(tris, "ent_list"),
            layer,
        )

    def make_region(
        self, tol: float, is_angular: bool, mesh: bool = True, prop: Property = None
    ) -> int:
        """
        Creates geometric regions from mesh triangle or STL

        Args:
            tol (float): specifies planar or angular tolerance
            is_angular (bool): specify True to check angular tolerance when
                merging triangles and False to specify a planar tolerance
            mesh (bool): specify True to convert mesh to regions and False to convert STL
            prop (Property): property to set the region (for STL only)

        Returns:
            Number of regions created
        """
        process_log(__name__, LogMessage.FUNCTION_CALL, locals(), name="make_region")
        check_type(tol, float)
        check_type(is_angular, bool)
        check_type(mesh, bool)
        if prop is not None:
            check_type(prop, Property)
            return self.mesh_editor.MakeRegion2(
                tol, is_angular, mesh, coerce_optional_dispatch(prop, "prop")
            )
        return self.mesh_editor.MakeRegion(tol, is_angular)

    def move_beam_node(self, moving_node: EntList | None, target: Vector | None) -> bool:
        """
        Moves a beam node

        Args:
            moving_node (EntList | None): EntList object containing the beam node to be moved
            target (Vector | None): Vector object containing the destination point

        Returns:
            True if operation is successful; False otherwise
        """
        process_log(__name__, LogMessage.FUNCTION_CALL, locals(), name="move_beam_node")
        if moving_node is not None:
            check_type(moving_node, EntList)
        if target is not None:
            check_type(target, Vector)
        return self.mesh_editor.MoveBeamNode(
            coerce_optional_dispatch(moving_node, "ent_list"),
            coerce_optional_dispatch(target, "vector"),
        )

    def move_node_to_edge(
        self,
        node: EntList | None,
        edge_node1: EntList | None,
        edge_node2: EntList | None,
        param_loc: float,
    ) -> bool:
        """
        Moves a node to a triangle edge.
        It breaks triangles that share the edge and creates new ones if necessary

        Args:
            node (EntList | None): EntList object containing the node to be moved
            edge_node1 (EntList | None): EntList object containing the first node of the edge
            edge_node2 (EntList | None): EntList object containing the second node of the edge
            param_loc (float): parameter location along the edge (0.0 to 1.0)

        Returns:
            True if operation is successful; False otherwise
        """
        process_log(__name__, LogMessage.FUNCTION_CALL, locals(), name="move_node_to_edge")
        if node is not None:
            check_type(node, EntList)
        if edge_node1 is not None:
            check_type(edge_node1, EntList)
        if edge_node2 is not None:
            check_type(edge_node2, EntList)
        check_type(param_loc, (int, float))
        check_range(param_loc, 0.0, 1.0, True, True)
        return self.mesh_editor.MoveNodeToEdge(
            coerce_optional_dispatch(node, "ent_list"),
            coerce_optional_dispatch(edge_node1, "ent_list"),
            coerce_optional_dispatch(edge_node2, "ent_list"),
            param_loc,
        )

    def create_beams_by_points(
        self, pt1: Vector | None, pt2: Vector | None, num: int, prop: Property | None
    ) -> EntList:
        """
        Creates beams between two points

        Args:
            pt1 (Vector | None): Vector object containing the first point
            pt2 (Vector | None): Vector object containing the second point
            num (int): Number of beams to be created
            prop (Property | None): Property object containing the property of the beam

        Returns:
            The new beam.
        """
        process_log(__name__, LogMessage.FUNCTION_CALL, locals(), name="create_beams_by_points")
        if pt1 is not None:
            check_type(pt1, Vector)
        if pt2 is not None:
            check_type(pt2, Vector)
        check_type(num, int)
        check_is_non_negative(num)
        if prop is not None:
            check_type(prop, Property)
        result = self.mesh_editor.CreateBeamsByPoints(
            coerce_optional_dispatch(pt1, "vector"),
            coerce_optional_dispatch(pt2, "vector"),
            num,
            coerce_optional_dispatch(prop, "prop"),
        )
        if result is None:
            return None
        return EntList(result)

    def project_mesh(self, tris: EntList | None) -> bool:
        """
        Project mesh to geometry

        Args:
            tris (EntList | None): EntList object containing the triangles to be projected

        Returns:
            True if operation is successful; False otherwise
        """
        process_log(__name__, LogMessage.FUNCTION_CALL, locals(), name="project_mesh")
        if tris is not None:
            check_type(tris, EntList)
        return self.mesh_editor.ProjectMesh(coerce_optional_dispatch(tris, "ent_list"))

    def convert_to_beams(
        self, start_node: EntList | None, prop: Property | None, junction: bool, num_branch: int
    ) -> int:
        """
        Converts mesh to beam elements

        Args:
            start_node (EntList | None): EntList object containing the starting node of the beam
            prop (Property | None): Property set for the new beams
            junction (bool): specify True to create junctions
            num_branch (int): Number of branches to be created

        Returns:
            Number of beams created
        """
        process_log(__name__, LogMessage.FUNCTION_CALL, locals(), name="convert_to_beams")
        if start_node is not None:
            check_type(start_node, EntList)
        if prop is not None:
            check_type(prop, Property)
        check_type(junction, bool)
        check_type(num_branch, int)
        check_is_non_negative(num_branch)
        return self.mesh_editor.ConvertToBeams(
            coerce_optional_dispatch(start_node, "ent_list"),
            coerce_optional_dispatch(prop, "prop"),
            junction,
            num_branch,
        )

    def contact_stitch_interface(self, merge_tol: float) -> int:
        """
        Stitches contact interface triangles

        Args:
            merge_tol (float): Merge tolerance

        Returns:
            0 if no contact interfaces are found
            1 if the operation is successful
            2 if the 3D Mold Mesh functionality has not been used
            to prepare the mold internal surface
        """
        process_log(__name__, LogMessage.FUNCTION_CALL, locals(), name="contact_stitch_interface")
        check_type(merge_tol, (int, float))
        return self.mesh_editor.ContactStitchInterface(merge_tol)

    def view_contact_stitch(self, merge_tol: float) -> int:
        """
        Preview the contact surface layer created by the stitch operation

        Args:
            merge_tol (float): Merge tolerance

        Returns:
            0 if no contact interfaces are found
            1 if the operation is successful
            2 if the 3D Mold Mesh funcationality has not been used
            to prepare the mold internal surface
        """
        process_log(__name__, LogMessage.FUNCTION_CALL, locals(), name="view_contact_stitch")
        check_type(merge_tol, (int, float))
        return self.mesh_editor.ViewContactStitch(merge_tol)

    def cut_triangles_by_plane(
        self, plane_normal: Vector | None, ref_point: Vector | None, fill: bool, smooth: bool
    ) -> bool:
        """
        Cut visible triangles by a plane defined by plane normal and a reference point on the plane

        Args:
            plane_normal (Vector | None): Vector object containing normal plane
            ref_point (Vector | None): Vector object containing a reference point on the plane
            fill (bool): whether to fill holes after cut
            smooth (bool): whether to smooth mesh after cut

        Returns:
            True if operation is successful; False otherwise
        """
        process_log(__name__, LogMessage.FUNCTION_CALL, locals(), name="cut_triangles_by_plane")
        if plane_normal is not None:
            check_type(plane_normal, Vector)
        if ref_point is not None:
            check_type(ref_point, Vector)
        check_type(fill, bool)
        check_type(smooth, bool)
        return self.mesh_editor.CutTrianglesByPlane(
            coerce_optional_dispatch(plane_normal, "vector"),
            coerce_optional_dispatch(ref_point, "vector"),
            fill,
            smooth,
        )

    def offset_triangles(
        self, offset_tri: EntList | None, offset_dist: float, falloff_dist: float, smooth_nb: bool
    ) -> bool:
        """
        Offsets triangles by a given distance

        Args:
            offset_tri (EntList | None): EntList object containing the triangles to be offset
            offset_dist (float): Offset distance
            falloff_dist (float): Falloff distance
            smooth_nb (bool): whether to smooth surrounding triangles after offset

        Returns:
            True if operation is successful; False otherwise
        """
        process_log(__name__, LogMessage.FUNCTION_CALL, locals(), name="offset_triangles")
        if offset_tri is not None:
            check_type(offset_tri, EntList)
        check_type(offset_dist, (int, float))
        check_type(falloff_dist, (int, float))
        check_type(smooth_nb, bool)
        return self.mesh_editor.OffsetTriangles(
            coerce_optional_dispatch(offset_tri, "ent_list"), offset_dist, falloff_dist, smooth_nb
        )

    # pylint: disable-next=R0913, R0917
    def extrude_triangles(
        self,
        offset_tri: EntList | None,
        dist: float,
        scale: float,
        smooth_nb: bool,
        create_new_body: bool,
        prop: Property | None,
    ) -> bool:
        """
        Extrude selected triangles in surface normal direction by a specified distance

        Args:
            offset_tri (EntList | None): EntList object containing the triangles to be extruded
            dist (float): Extrusion distance
            scale (float): scale selected triangles
            smooth_nb (bool): whether to smooth surrounding triangles after extrusion
            create_new_body (bool): whether to form a separate body with new triangles
            prop (Property | None): Property object containing the property of the extruded mesh

        Returns:
            True if operation is successful; False otherwise
        """
        process_log(__name__, LogMessage.FUNCTION_CALL, locals(), name="extrude_triangles")
        if offset_tri is not None:
            check_type(offset_tri, EntList)
        check_type(dist, (int, float))
        check_type(scale, (int, float))
        check_type(smooth_nb, bool)
        check_type(create_new_body, bool)
        if prop is not None:
            check_type(prop, Property)
        return self.mesh_editor.ExtrudeTriangles(
            coerce_optional_dispatch(offset_tri, "ent_list"),
            dist,
            scale,
            smooth_nb,
            create_new_body,
            coerce_optional_dispatch(prop, "prop"),
        )

    def imprint_visible_triangles(self) -> bool:
        """
        Align visible nodes and triangles

        Returns:
            True if operation is successful; False otherwise
        """
        process_log(__name__, LogMessage.FUNCTION_CALL, locals(), name="imprint_visible_triangles")
        return self.mesh_editor.ImprintVisibleTriangles

    def imprint_selected_triangles(self, tri: EntList | None) -> bool:
        """
        Align nodes and triangles in selected areas

        Args:
            tri (EntList | None): EntList object containing the triangles to be imprinted

        Returns:
            True if operation is successful; False otherwise
        """
        process_log(__name__, LogMessage.FUNCTION_CALL, locals(), name="imprint_selected_triangles")
        if tri is not None:
            check_type(tri, EntList)
        return self.mesh_editor.ImprintSelectedTriangles(coerce_optional_dispatch(tri, "ent_list"))

    # pylint: disable=R0913, R0917
    def global_merge(
        self,
        tolerance: float,
        fusion: bool,
        bad_tri: bool,
        squeeze: bool = True,
        remove_dup_elements: bool = True,
        merge_dup_nodes: bool = True,
        vis_only: bool = False,
    ) -> int:
        """
        Merges nodes in the model that are within a specified tolerance

        Args:
            tolerance (float): specifies the tolerance for merging nodes
            fusion (bool): specify True to disallow merges between nodes that are not
                on the same element
            bad_tri (bool): specify True to merge bad triangles
            squeeze (bool): specify True to squeeze the mesh
            remove_dup_elements (bool): specify True to remove duplicate elements
            merge_dup_nodes (bool): specify True to merge duplicate nodes
            vis_only (bool): specify True to only merge visible nodes

        Returns:
            number of nodes merged
        """
        process_log(__name__, LogMessage.FUNCTION_CALL, locals(), name="global_merge")
        check_type(tolerance, (int, float))
        check_type(fusion, bool)
        check_type(bad_tri, bool)
        check_type(squeeze, bool)
        check_type(remove_dup_elements, bool)
        check_type(merge_dup_nodes, bool)
        check_type(vis_only, bool)
        return self.mesh_editor.GlobalMerge3(
            tolerance, fusion, bad_tri, squeeze, remove_dup_elements, merge_dup_nodes, vis_only
        )

    def merge_nodes(
        self, target: EntList | None, nodes: EntList | None, fusion: bool, use_mid: bool = False
    ) -> int:
        """
        Merges nodes in the model that are within a specified tolerance

        Args:
            target (EntList | None): EntList object containing the target node
            nodes (EntList | None): EntList object containing the set of nodes to be merged
                to the target node
            fusion (bool): specify True to disallow merges between nodes that are not on
                the same element
            use_mid (bool): specify True to merge nodes to midpoint

        Returns:
            number of nodes merged
        """
        process_log(__name__, LogMessage.FUNCTION_CALL, locals(), name="merge_nodes")
        if target is not None:
            check_type(target, EntList)
        if nodes is not None:
            check_type(nodes, EntList)
        check_type(fusion, bool)
        check_type(use_mid, bool)
        return self.mesh_editor.MergeNodes2(
            coerce_optional_dispatch(target, "ent_list"),
            coerce_optional_dispatch(nodes, "ent_list"),
            fusion,
            use_mid,
        )

    def fix_aspect_ratio(self, target: float) -> int:
        """
        Attempts to reduce triangle aspect ratios in the mesh below a specified value

        Args:
            target (float): target aspect ratio

        Returns:
            number of elements modified to effect aspect ratio reduction
        """
        process_log(__name__, LogMessage.FUNCTION_CALL, locals(), name="fix_aspect_ratio")
        check_type(target, float)
        return self.mesh_editor.FixAspectRatio(target)
