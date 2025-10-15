import itertools
import sys
from collections.abc import Iterable

from plado.datalog.evaluator.compiler import (
    FLUENTS,
    RELATIONS,
    compile_interdepending,
    compile_without_dependencies,
)
from plado.datalog.evaluator.filtering import (
    insert_constraint_predicate,
    insert_filter_predicates,
    insert_projections,
)
from plado.datalog.evaluator.join_graph import construct_join_graph
from plado.datalog.evaluator.planner import GreedyOptimizer
from plado.datalog.evaluator.query_tree import GroundAtomRef, GroundAtomsNode, QNode
from plado.datalog.numeric import NumericConstraint
from plado.datalog.program import Atom, Clause, Constant, DatalogProgram
from plado.utils import Float, tarjan

Table = set[tuple[int]]
Database = list[Table]
FluentsTable = dict[tuple[int], Float]
FluentsDatabase = list[FluentsTable]


def _cost_function(relations, args, join_relation, join_args):
    return -len(join_args)


class NormalizedClause:
    def __init__(
        self,
        head: Atom,
        num_variables: int,
        positive: Iterable[Atom],
        negative: Iterable[Atom],
        ground_positive: Iterable[GroundAtomRef],
        ground_negative: Iterable[GroundAtomRef],
        vars_eq: Iterable[tuple[int, int]],
        vars_neq: Iterable[tuple[int, int]],
        obj_eq: Iterable[tuple[int, int]],
        obj_neq: Iterable[tuple[int, int]],
        constraints: Iterable[NumericConstraint],
    ):
        self.num_variables: int = num_variables
        self.head: Atom = head
        self.positive: tuple[Atom] = tuple(positive)
        self.negative: tuple[Atom] = tuple(negative)
        self.ground_positive: tuple[GroundAtomRef] = tuple(ground_positive)
        self.ground_negative: tuple[GroundAtomRef] = tuple(ground_negative)
        self.vars_eq = tuple(vars_eq)
        self.vars_neq = tuple(vars_neq)
        self.obj_eq = tuple(obj_eq)
        self.obj_neq = tuple(obj_neq)
        self.constraints = tuple(constraints)
        assert all((
            any(varid in atom.get_variables() for atom in self.positive)
            for varid in range(self.num_variables)
        )), "all variables must be positively bounded"

    def __str__(self):
        body = filter(
            lambda x: len(x.strip()) > 0,
            [
                ", ".join((str(a) for a in self.positive)),
                ", ".join(("not " + str(a) for a in self.negative)),
                ", ".join((f"?x{x} = ?x{y}" for x, y in self.vars_eq)),
                ", ".join((f"?x{x} != ?x{y}" for x, y in self.vars_neq)),
                ", ".join((f"?x{x} = {y}" for x, y in self.obj_eq)),
                ", ".join((f"?x{x} != {y}" for x, y in self.obj_neq)),
            ],
        )
        return f"{self.head} =: {', '.join(body)}"


def _generate_query_tree(
    clause: NormalizedClause,
    cost_function=_cost_function,
) -> QNode:
    jg = construct_join_graph(clause.num_variables, clause.positive, clause.negative)
    planner = GreedyOptimizer(cost_function)
    qnode = insert_filter_predicates(
        clause.vars_eq, clause.vars_neq, clause.obj_eq, clause.obj_neq, planner(jg)
    )
    for constraint in clause.constraints:
        qnode = insert_constraint_predicate(constraint, qnode)
    qnode = insert_projections(
        qnode,
        set((arg.id for arg in clause.head.arguments)),
    )
    if len(clause.ground_negative) > 0:
        qnode = GroundAtomsNode(qnode, clause.ground_negative, True)
    if len(clause.ground_positive) > 0:
        qnode = GroundAtomsNode(qnode, clause.ground_positive, False)
    return qnode


def _get_dependency_graph(
    num_relations: int, clauses: Iterable[NormalizedClause]
) -> list[list[int]]:
    dg = [set() for i in range(num_relations)]
    for clause in clauses:
        head = clause.head.relation_id
        for atom in itertools.chain(clause.positive, clause.negative):
            dg[head].add(atom.relation_id)
    return dg


def _get_dependent_components(dg: list[list[int]]) -> list[list[int]]:
    num_relations = len(dg)
    visited: list[bool] = [False for i in range(num_relations)]
    result: list[list[int]] = []

    def on_scc(scc: list[int]):
        for r in scc:
            visited[r] = True
        result.append(scc)

    def get_successors(r: int) -> list[int]:
        return (rr for rr in dg[r] if not visited[rr])

    for r in range(num_relations):
        if not visited[r]:
            tarjan(r, get_successors, on_scc)

    return result


def _is_stratified(
    num_relations: int, clauses: Iterable[NormalizedClause], components: list[list[int]]
):
    component_idx = [None for i in range(num_relations)]
    for i, c in enumerate(components):
        for r in c:
            component_idx[r] = i
    for clause in clauses:
        for atom in clause.negative:
            if (
                component_idx[atom.relation_id]
                >= component_idx[clause.head.relation_id]
            ):
                return False
    return True


def _get_query_engine_code(
    num_relations: int,
    clauses: list[NormalizedClause],
    cost_function=_cost_function,
):
    dependency_graph = _get_dependency_graph(num_relations, clauses)
    dependent_clauses = _get_dependent_components(dependency_graph)
    assert _is_stratified(num_relations, clauses, dependent_clauses)
    query_trees = list(
        (_generate_query_tree(clause, cost_function) for clause in clauses)
    )
    evaluator_code = [
        f"### num clauses: {len(clauses)}",
        f"### num relations: {num_relations}",
    ] + [
        f"### clause {idx}: {clauses[idx].head} := {tree}"
        for idx, tree in enumerate(query_trees)
    ]
    for group in dependent_clauses:
        clause_idxs = [
            i for i, clause in enumerate(clauses) if clause.head.relation_id in group
        ]
        if len(clause_idxs) == 0:
            continue
        if len(group) > 1 or group[0] in dependency_graph[group[0]]:
            relations = [clauses[idx].head.relation_id for idx in clause_idxs]
            relation_args = [
                tuple((symb.id for symb in clauses[idx].head.arguments))
                for idx in clause_idxs
            ]
            rules = [query_trees[idx] for idx in clause_idxs]
            evaluator_code.extend((
                f"## {clauses[idx].head} := {str(query_trees[idx])}"
                for idx in clause_idxs
            ))
            evaluator_code.append(
                compile_interdepending(relations, relation_args, rules, num_relations)
            )
        else:
            assert len(group) == 1
            for idx in clause_idxs:
                clause = clauses[idx]
                evaluator_code.append(
                    f"## {clauses[idx].head} := {str(query_trees[idx])}"
                )
                evaluator_code.append(
                    compile_without_dependencies(
                        clause.head.relation_id,
                        tuple((arg.id for arg in clause.head.arguments)),
                        query_trees[idx],
                        num_relations,
                    )
                )
    evaluator_code = "\n".join(evaluator_code)
    # print()
    # print()
    # print(evaluator_code)
    # print()
    # print()
    return evaluator_code, compile(evaluator_code, "<string>", "exec")


def _extract_eq_atom(
    source: Iterable[Atom],
    atoms: list[Atom],
    variables: list[tuple[int, int]],
    objs: list[tuple[int, int]],
    eq_relation: int,
):
    for atom in source:
        if atom.relation_id == eq_relation:
            assert len(atom.arguments) == 2
            x = atom.arguments[0]
            y = atom.arguments[1]
            if x.is_variable():
                if y.is_variable():
                    variables.append((min(x.id, y.id), max(x.id, y.id)))
                else:
                    objs.append((x.id, y.id))
            elif y.is_variable():
                objs.append((y.id, x.id))
            else:
                assert False
        else:
            atoms.append(atom)


def _separate_ground_atoms(
    source: Iterable[Atom], bounded_variables: dict[int, int]
) -> tuple[list[Atom], list[GroundAtomRef]]:
    ground_atoms = []
    non_ground_atoms = []
    for atom in source:
        args = []
        for var_id in atom.get_variables():
            args.append(bounded_variables.get(var_id, None))
        if None not in args:
            ground_atoms.append(GroundAtomRef(atom.relation_id, args))
        else:
            non_ground_atoms.append(atom)
    return non_ground_atoms, ground_atoms


def _normalize_clause(
    clause: Clause, eq_relation: int, object_relation: int
) -> NormalizedClause:
    positive = []
    vars_eq = []
    objs_eq = []
    _extract_eq_atom(clause.pos_body, positive, vars_eq, objs_eq, eq_relation)

    negative = []
    vars_neq = []
    objs_neq = []
    _extract_eq_atom(clause.neg_body, negative, vars_neq, objs_neq, eq_relation)

    var_to_objs = dict(objs_eq)
    positive, ground_positive = _separate_ground_atoms(positive, var_to_objs)
    negative, ground_negative = _separate_ground_atoms(negative, var_to_objs)

    variables = set()
    for atom in itertools.chain([clause.head], positive, negative):
        variables = variables | set(atom.get_variables())
    for constr in clause.constraints:
        variables = variables | set(constr.expr.get_variables())
    variables = dict(
        (var, Constant(i, True)) for i, var in enumerate(sorted(variables))
    )

    assert all(((x in variables) == (y in variables) for x, y in vars_eq))
    assert all(((x in variables) == (y in variables) for x, y in vars_neq))
    assert all((x in variables) for x, _ in objs_neq)

    head = clause.head.substitute_(variables)
    positive = [atom.substitute_(variables) for atom in positive]
    negative = [atom.substitute_(variables) for atom in negative]
    vars_eq = [
        (variables[x].id, variables[y].id) for (x, y) in vars_eq if x in variables
    ]
    vars_neq = [
        (variables[x].id, variables[y].id) for (x, y) in vars_neq if x in variables
    ]
    objs_eq = [(variables[x].id, y) for (x, y) in objs_eq if x in variables]
    objs_neq = [(variables[x].id, y) for (x, y) in objs_neq]

    for varid in range(len(variables)):
        if not any((varid in atom.get_variables() for atom in positive)):
            positive.append(Atom(object_relation, [Constant(varid, True)]))

    return NormalizedClause(
        head,
        len(variables),
        positive,
        negative,
        ground_positive,
        ground_negative,
        vars_eq,
        vars_neq,
        objs_eq,
        objs_neq,
        clause.constraints,
    )


class DatalogEngine:
    def __init__(
        self,
        program: DatalogProgram,
        num_objects: int,
        cost_function=_cost_function,
    ):
        self.num_relations = program.num_relations() + 1
        self.object_relation = program.num_relations()
        self.code, self.bin = _get_query_engine_code(
            self.num_relations,
            list(
                _normalize_clause(
                    clause, program.equality_relation, self.object_relation
                )
                for clause in program.clauses
            ),
            cost_function,
        )

        indented_code = '\n'.join('    ' + line for line in self.code.split('\n'))
        function_source = f"""
def generated_datalog_engine(env):
    RELATIONS = "relations"
    FLUENTS = "fluents"
    relations = env[RELATIONS]
    fluents = env[FLUENTS]
{indented_code}
"""

        namespace = {}
        exec(compile(function_source, "<string>", "exec"), namespace)
        self.execute_datalog_engine = namespace['generated_datalog_engine']

        self.static_atoms = list(program.trivial_clauses)
        self.static_atoms.extend([
            Atom(self.object_relation, [Constant(obj, False)])
            for obj in range(num_objects)
        ])
        self.static_atom_tuples = [
            (atom.relation_id, tuple(arg.id for arg in atom.arguments))
            for atom in self.static_atoms
        ]

    def __call__(
        self, facts: Database, fluents: FluentsDatabase | None = None
    ) -> Database:
        env = {FLUENTS: fluents, RELATIONS: [set(r) for r in facts]}
        env[RELATIONS].append(set())

        for relation_id, args_tuple in self.static_atom_tuples:
            env[RELATIONS][relation_id].add(args_tuple)

        self.execute_datalog_engine(env)
        del env[RELATIONS][self.object_relation]
        return env[RELATIONS]
