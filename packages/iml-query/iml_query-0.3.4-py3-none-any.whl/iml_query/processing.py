"""Post-processing and manipulation functions for IML queries."""

from typing import Any

from tree_sitter import Node, Tree

from iml_query.queries import (
    DECOMP_QUERY_SRC,
    INSTANCE_QUERY_SRC,
    OPAQUE_QUERY_SRC,
    REC_QUERY_SRC,
    TOP_LEVEL_VALUE_DEFINITION_QUERY_SRC,
    VALUE_DEFINITION_QUERY_SRC,
    VERIFY_QUERY_SRC,
    DecompCapture,
    InstanceCapture,
    RecCapture,
    TopDefCapture,
    VerifyCapture,
)

from .tree_sitter_utils import (
    delete_nodes,
    get_nesting_relationship,
    get_parser,
    insert_lines,
    mk_query,
    run_queries,
    run_query,
    unwrap_bytes,
)


def find_func_definition(tree: Tree, function_name: str) -> Node | None:
    matches = run_query(
        mk_query(VALUE_DEFINITION_QUERY_SRC),
        node=tree.root_node,
    )

    func_def: Node | None = None
    for _, capture in matches:
        function_name_node = capture['function_name'][0]
        function_name_rhs = unwrap_bytes(function_name_node.text).decode(
            'utf-8'
        )
        if function_name_rhs == function_name:
            func_def = capture['function_definition'][0]
            break

    return func_def


def find_nested_measures(root_node: Node) -> list[dict[str, Any]]:
    """Find nested measures.

    Reurns:
        list of dicts with keys:
            function_name: name of top-level function
            level: nesting level of top-level function
            node: top-level function node
            range: range of top-level function node
            nested_measures: list of dicts with keys:
                function_name: name of nested function
                level: nesting level of nested function
                node: nested function node
                range: range of nested function node
    """
    # Query that finds both top-level functions and all functions with a measure
    combined_query = mk_query(r"""
    ; Find top-level functions
    (compilation_unit
        (value_definition
            (let_binding
                pattern: (value_name) @top_func_name
            )
        ) @top_function
    )

    ; Find functions with a measure attribute
    (value_definition
        (let_binding
            pattern: (value_name) @nested_func_name
            (item_attribute
                "[@@"
                (attribute_id) @_measure_id
                (#eq? @_measure_id "measure")
            )
        )
    ) @nested_function
    """)

    matches = run_query(combined_query, node=root_node)

    # Separate top-level functions from nested functions with measures
    top_level_functions: list[dict[str, Any]] = []
    nested_functions_with_measures: list[dict[str, Any]] = []

    for pattern_idx, capture in matches:
        if pattern_idx == 0:  # Top-level function pattern
            func_def = capture['top_function'][0]
            func_name = unwrap_bytes(capture['top_func_name'][0].text).decode(
                'utf-8'
            )
            top_level_functions.append(
                {
                    'name': func_name,
                    'node': func_def,
                    'range': func_def.range,
                }
            )
        elif pattern_idx == 1:  # Nested function with measure pattern
            nested_func = capture['nested_function'][0]
            nested_name = unwrap_bytes(
                capture['nested_func_name'][0].text
            ).decode('utf-8')
            nested_functions_with_measures.append(
                {
                    'name': nested_name,
                    'node': nested_func,
                    'range': nested_func.range,
                }
            )

    # Now match nested functions to their containing top-level functions
    problematic_functions: list[dict[str, Any]] = []

    for top_func_info in top_level_functions:
        top_func_node = top_func_info['node']
        nested_measures: list[dict[str, Any]] = []

        for nested_info in nested_functions_with_measures:
            nested_node = nested_info['node']

            # Get nesting relationship in a single traversal
            nesting_level = get_nesting_relationship(nested_node, top_func_node)

            # Only include if it's truly nested (level > 0)
            if nesting_level > 0:
                nested_measures.append(
                    {
                        'function_name': nested_info['name'],
                        'level': nesting_level,
                        'range': nested_info['range'],
                        'node': nested_node,
                    }
                )

        if nested_measures:
            problematic_functions.append(
                {
                    'top_level_function_name': top_func_info['name'],
                    'node': top_func_info['node'],
                    'range': top_func_info['range'],
                    'nested_measures': nested_measures,
                }
            )

    return problematic_functions


def find_nested_rec(iml: str) -> list[dict[str, Any]]:
    """Find nested recursive function definitions in IML code.

    Returns:
        a list of dictionary for the name and location of each function

    """
    tree = get_parser().parse(bytes(iml, 'utf-8'))
    queries = {
        'top_level_functions': TOP_LEVEL_VALUE_DEFINITION_QUERY_SRC,
        'rec_functions': REC_QUERY_SRC,
    }
    captures_map = run_queries(queries, tree.root_node)
    top_captures: list[TopDefCapture] = [
        TopDefCapture.from_ts_capture(capture)
        for capture in captures_map.get('top_level_functions', [])
    ]
    rec_captures: list[RecCapture] = [
        RecCapture.from_ts_capture(capture)
        for capture in captures_map.get('rec_functions', [])
    ]

    #
    nested_rec_caps: list[RecCapture] = []
    top_function_nodes: list[Node] = [c.top_function for c in top_captures]

    for rec_cap in rec_captures:
        rec_function_node = rec_cap.function_definition
        if rec_function_node not in top_function_nodes:
            nested_rec_caps.append(rec_cap)

    nested_rec_dict: list[dict[str, Any]] = []
    for cap in nested_rec_caps:
        d: dict[str, Any] = {
            'name': unwrap_bytes(cap.function_name.text).decode('utf-8')
        }
        func_range = cap.function_definition.range
        start_point, end_point = func_range.start_point, func_range.end_point
        d['start_point'] = (start_point.row, start_point.column)
        d['end_point'] = (end_point.row, end_point.column)
        d['start_byte'] = func_range.start_byte
        d['end_byte'] = func_range.end_byte
        nested_rec_dict.append(d)
    return nested_rec_dict


def verify_capture_to_req(capture: VerifyCapture) -> dict[str, str]:
    """Extract ImandraX request from a verify statement node."""
    node = capture.verify
    req: dict[str, str] = {}
    assert node.type == 'verify_statement', 'not verify_statement'
    assert node.text, 'None text'
    verify_src = (
        unwrap_bytes(node.text)
        .decode('utf-8')
        .strip()
        .removeprefix('verify')
        .strip()
    )
    # Remove parentheses
    if verify_src.startswith('(') and verify_src.endswith(')'):
        verify_src = verify_src[1:-1].strip()

    req['src'] = verify_src
    return req


def instance_capture_to_req(capture: InstanceCapture) -> dict[str, str]:
    """Extract ImandraX request from an instance statement node."""
    node = capture.instance
    req: dict[str, str] = {}
    assert node.type == 'instance_statement', 'not instance_statement'
    assert node.text, 'None text'
    instance_src = (
        unwrap_bytes(node.text)
        .decode('utf-8')
        .strip()
        .removeprefix('instance')
        .strip()
    )
    # Remove parentheses
    if instance_src.startswith('(') and instance_src.endswith(')'):
        instance_src = instance_src[1:-1].strip()
    req['src'] = instance_src
    return req


def eval_node_to_src(node: Node) -> str:
    """Extract str from an eval statement node."""
    assert node.type == 'eval_statement', 'not eval_statement'
    assert node.text, 'None text'
    src = (
        unwrap_bytes(node.text)
        .decode('utf-8')
        .strip()
        .removeprefix('eval')
        .strip()
    )
    # Remove parentheses
    if src.startswith('(') and src.endswith(')'):
        src = src[1:-1].strip()
    return src


class DecompParsingError(Exception):
    """Exception raised when parsing decomp fails."""

    pass


def top_application_to_decomp(node: Node) -> dict[str, Any]:
    """Extract Decomp request request from a top application node."""
    assert node.type == 'application_expression'

    extract_top_arg_query = mk_query(r"""
    (application_expression
        (value_path
            (value_name) @top
            (#eq? @top "top")
        )
        (labeled_argument
            (label_name) @label
        ) @arg
        (unit)
    )
    """)

    matches = run_query(query=extract_top_arg_query, node=node)
    # print(f'Found {len(matches)} labeled arguments')

    # print(f'Matches: \\n{matches}')

    res: dict[str, Any] = {}

    # Process each labeled argument based on its label
    for _, capture in matches:
        label_name_b = capture['label'][0].text
        assert label_name_b, 'Never: no label'
        label_name = label_name_b.decode('utf-8')
        arg_node = capture['arg'][0]

        match label_name:
            case 'assuming':
                # Parse assuming: ~assuming:[%id simple_branch]
                assuming_query = mk_query(r"""
                (extension
                    "[%"
                    (attribute_id) @attr_id
                    (attribute_payload) @payload
                    (#eq? @attr_id "id")
                )
                """)
                assuming_matches = run_query(
                    query=assuming_query, node=arg_node
                )
                if assuming_matches:
                    payload_text = assuming_matches[0][1]['payload'][0].text
                    assert payload_text, 'Never: no assuming payload'
                    res['assuming'] = payload_text.decode('utf-8')

            case 'basis' | 'rule_specs':
                # Query each extension separately to get all identifiers
                extension_query = mk_query(r"""
                (extension
                    "[%"
                    (attribute_id)
                    (attribute_payload
                        (expression_item
                            (value_path
                                (value_name) @id
                            )
                        )
                    )
                )
                """)
                extension_matches = run_query(
                    query=extension_query, node=arg_node
                )
                if extension_matches:
                    ids: list[str] = []
                    for match in extension_matches:
                        id_node = match[1]['id'][0]
                        id_text = id_node.text
                        assert id_text, f'Never: no {label_name} id text'
                        ids.append(id_text.decode('utf-8'))
                    res[label_name] = ids

            case 'prune' | 'ctx_simp':
                # Parse boolean: ~prune:true
                bool_query = mk_query(r"""
                (boolean) @bool_val
                """)
                bool_matches = run_query(query=bool_query, node=arg_node)
                if bool_matches:
                    bool_text = bool_matches[0][1]['bool_val'][0].text
                    assert bool_text, f'Never: no {label_name} boolean text'
                    res[label_name] = bool_text.decode('utf-8') == 'true'

            case 'lift_bool':
                # Parse constructor: ~lift_bool:Default
                constructor_query = mk_query(r"""
                (constructor_path
                    (constructor_name) @constructor
                )
                """)
                constructor_matches = run_query(
                    query=constructor_query, node=arg_node
                )
                if constructor_matches:
                    constructor_text = constructor_matches[0][1]['constructor'][
                        0
                    ].text
                    assert constructor_text, (
                        'Never: no lift_bool constructor text'
                    )
                    lift_bool_value = constructor_text.decode('utf-8')
                    lift_bool_enum = [
                        'Default',
                        'Nested_equalities',
                        'Equalities',
                        'All',
                    ]
                    if lift_bool_value not in lift_bool_enum:
                        raise DecompParsingError(
                            f'Invalid lift_bool value: {lift_bool_value}',
                            f'should be one of {lift_bool_enum}',
                        )
                    res['lift_bool'] = lift_bool_value
            case _:
                assert 'False', 'Never'

    default_res: dict[str, Any] = {
        'basis': [],
        'rule_specs': [],
        'prune': False,
    }

    res = default_res | res

    return res


def decomp_req_to_top_appl_text(req: dict[str, Any]) -> str:
    """Convert a decomp request to a top application source string."""

    def mk_id(identifier_name: str) -> str:
        return f'[%id {identifier_name}]'

    labels: list[str] = []
    for k, v in req.items():
        if k == 'assuming':
            if v is None:
                continue
            labels.append(f'~assuming:{mk_id(v[0])}')
        if k == 'basis':
            if len(v) == 0:
                continue
            s = '~basis:'
            items_str = ' ; '.join(map(mk_id, v))
            s += f'[{items_str}]'
            labels.append(s)
        if k == 'rule_specs':
            if len(v) == 0:
                continue
            s = '~rule_specs:'
            items_str = ' ; '.join(map(mk_id, v))
            s += f'[{items_str}]'
            labels.append(s)
        if k == 'prune':
            if v:
                labels.append(f'~prune:{"true" if v else "false"}')
        if k == 'ctx_simp':
            labels.append(f'~ctx_simp:{"true" if v else "false"}')
        if k == 'lift_bool':
            if v is None:
                continue
            s = '~lift_bool:'
            s += f'{v} ()'

    return f'top {" ".join(labels) + " "}()'


def decomp_attribute_payload_to_decomp_req_labels(node: Node) -> dict[str, Any]:
    assert node.type == 'attribute_payload'

    expect_appl = node.children[0].children[0]
    if expect_appl.type != 'application_expression':
        raise NotImplementedError('Composition operators are not supported yet')

    return top_application_to_decomp(expect_appl)


def decomp_capture_to_req(capture: DecompCapture) -> dict[str, Any]:
    req: dict[str, Any] = {}
    req['name'] = unwrap_bytes(capture.decomposed_func_name.text).decode('utf8')
    req_labels = decomp_attribute_payload_to_decomp_req_labels(
        capture.decomp_payload
    )
    req |= req_labels
    return req


def extract_opaque_function_names(iml: str) -> list[str]:
    opaque_functions: list[str] = []
    matches = run_query(
        mk_query(OPAQUE_QUERY_SRC),
        code=iml,
    )
    for _, capture in matches:
        value_name_node = capture['function_name'][0]
        func_name = unwrap_bytes(value_name_node.text).decode('utf-8')
        opaque_functions.append(func_name)

    return opaque_functions


def remove_verify_reqs(
    iml: str,
    tree: Tree,
    captures: list[VerifyCapture],
) -> tuple[str, Tree]:
    """Remove verify requests from IML code."""
    verify_nodes = [capture.verify for capture in captures]
    new_iml, new_tree = delete_nodes(iml, tree, nodes=verify_nodes)
    return new_iml, new_tree


def extract_verify_reqs(
    iml: str, tree: Tree
) -> tuple[str, Tree, list[dict[str, Any]]]:
    root = tree.root_node
    matches = run_query(
        mk_query(VERIFY_QUERY_SRC),
        node=root,
    )

    verify_captures = [
        VerifyCapture.from_ts_capture(capture) for _, capture in matches
    ]
    reqs: list[dict[str, Any]] = [
        verify_capture_to_req(capture) for capture in verify_captures
    ]
    new_iml, new_tree = remove_verify_reqs(iml, tree, verify_captures)
    return new_iml, new_tree, reqs


def remove_instance_reqs(
    iml: str,
    tree: Tree,
    captures: list[InstanceCapture],
) -> tuple[str, Tree]:
    """Remove instance requests from IML code."""
    instance_nodes = [capture.instance for capture in captures]
    new_iml, new_tree = delete_nodes(iml, tree, nodes=instance_nodes)
    return new_iml, new_tree


def extract_instance_reqs(
    iml: str, tree: Tree
) -> tuple[str, Tree, list[dict[str, Any]]]:
    root = tree.root_node
    matches = run_query(
        mk_query(INSTANCE_QUERY_SRC),
        node=root,
    )

    instance_captures = [
        InstanceCapture.from_ts_capture(capture) for _, capture in matches
    ]

    reqs: list[dict[str, Any]] = [
        instance_capture_to_req(capture) for capture in instance_captures
    ]
    new_iml, new_tree = remove_instance_reqs(iml, tree, instance_captures)
    return new_iml, new_tree, reqs


def remove_decomp_reqs(
    iml: str,
    tree: Tree,
    captures: list[DecompCapture],
) -> tuple[str, Tree]:
    """Remove decomp requests from IML code."""
    decomp_attr_nodes = [capture.decomp_attr for capture in captures]
    new_iml, new_tree = delete_nodes(iml, tree, nodes=decomp_attr_nodes)
    return new_iml, new_tree


def extract_decomp_reqs(
    iml: str, tree: Tree
) -> tuple[str, Tree, list[dict[str, Any]]]:
    root = tree.root_node
    matches = run_query(
        mk_query(DECOMP_QUERY_SRC),
        node=root,
    )

    decomp_captures = [
        DecompCapture.from_ts_capture(capture) for _, capture in matches
    ]

    reqs = [decomp_capture_to_req(capture) for capture in decomp_captures]
    new_iml, new_tree = remove_decomp_reqs(iml, tree, decomp_captures)
    return new_iml, new_tree, reqs


def iml_outline(iml: str) -> dict[str, Any]:
    outline: dict[str, Any] = {}
    tree = get_parser().parse(bytes(iml, encoding='utf8'))
    outline['verify_req'] = extract_verify_reqs(iml, tree)[2]
    outline['instance_req'] = extract_instance_reqs(iml, tree)[2]
    outline['decompose_req'] = extract_decomp_reqs(iml, tree)[2]
    outline['opaque_function'] = extract_opaque_function_names(iml)
    return outline


def insert_decomp_req(
    iml: str,
    tree: Tree,
    req: dict[str, Any],
) -> tuple[str, Tree]:
    func_def_node = find_func_definition(tree, req['name'])
    if func_def_node is None:
        raise ValueError(f'Function {req["name"]} not found in syntax tree')

    func_def_end_row = func_def_node.end_point[0]

    top_appl_text = decomp_req_to_top_appl_text(req)
    to_insert = f'[@@decomp {top_appl_text}]'

    new_iml, new_tree = insert_lines(
        iml,
        tree,
        lines=[to_insert],
        insert_after=func_def_end_row,
    )
    return new_iml, new_tree


def insert_verify_req(
    iml: str,
    tree: Tree,
    verify_src: str,
) -> tuple[str, Tree]:
    if not (verify_src.startswith('(') and verify_src.endswith(')')):
        verify_src = f'({verify_src})'
    to_insert = f'verify {verify_src}'

    file_end_row = tree.root_node.end_point[0]

    new_iml, new_tree = insert_lines(
        iml,
        tree,
        lines=[to_insert],
        insert_after=file_end_row,
    )
    return new_iml, new_tree


def insert_instance_req(
    iml: str,
    tree: Tree,
    instance_src: str,
) -> tuple[str, Tree]:
    if not (instance_src.startswith('(') and instance_src.endswith(')')):
        instance_src = f'({instance_src})'
    to_insert = f'instance {instance_src}'

    file_end_row = tree.root_node.end_point[0]

    new_iml, new_tree = insert_lines(
        iml,
        tree,
        lines=[to_insert],
        insert_after=file_end_row,
    )
    return new_iml, new_tree
