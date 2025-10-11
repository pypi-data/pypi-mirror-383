#include "pauli_term_container.hpp"
#include <pybind11/pybind11.h>
#include <pybind11/stl.h>
#include <pybind11/operators.h>
#include <pybind11/functional.h>

#include <sstream>
#include <memory>
#include <string>
#include <vector>

#include "circuit.hpp"
#include "noise_model.hpp"
#include "observable.hpp"
#include "pauli.hpp"
#include "pauli_term.hpp"
#include "scheduler.hpp"
#include "truncate.hpp"
#include "symbolic/coefficient.hpp"
#include "policy.hpp"

namespace py = pybind11;

using PTC = PauliTermContainer<coeff_t>;

// Define alias for our holder types for clarity
using TruncatorPtr = std::shared_ptr<Truncator<coeff_t>>;
using SchedulingPolicyPtr = std::shared_ptr<SchedulingPolicy>;

// Concrete holder types
using CoeffTruncatorPtr = std::shared_ptr<CoefficientTruncator<coeff_t>>;
using WeightTruncatorPtr = std::shared_ptr<WeightTruncator<coeff_t>>;
using NeverTruncatorPtr = std::shared_ptr<NeverTruncator<coeff_t>>;
using KeepNTruncatorPtr = std::shared_ptr<KeepNTruncator<coeff_t>>;
using NeverPolicyPtr = std::shared_ptr<NeverPolicy>;
using AlwaysBeforePolicyPtr = std::shared_ptr<AlwaysBeforeSplittingPolicy>;
using AlwaysAfterPolicyPtr = std::shared_ptr<AlwaysAfterSplittingPolicy>;

using LambdaPredicate_t = std::function<bool(PauliTermContainer<coeff_t>::NonOwningPauliTermPacked const&)>;
using LambdaTruncator = PredicateTruncator<LambdaPredicate_t>;
using LambdaTruncatorPtr = std::shared_ptr<LambdaTruncator>;

// Symbolic
using SymbolicCoeff_t = SymbolicCoefficient<coeff_t>;
using SymbolicObs_t = Observable<SymbolicCoeff_t>;
using SymbolicCircuit_t = Circuit<SymbolicCoeff_t>;
using SymbolicTruncatorPtr = std::shared_ptr<Truncator<SymbolicCoeff_t>>;
using SymbolicWeightTruncatorPtr = std::shared_ptr<WeightTruncator<SymbolicCoeff_t>>;
using SymbolicNeverTruncatorPtr = std::shared_ptr<NeverTruncator<SymbolicCoeff_t>>;
using SymbolicLambdaPredicate_t = std::function<bool(PauliTermContainer<SymbolicCoeff_t>::NonOwningPauliTermPacked const&)>;
using SymbolicLambdaTruncator = PredicateTruncator<SymbolicLambdaPredicate_t>;
using SymbolicLambdaTruncatorPtr = std::shared_ptr<SymbolicLambdaTruncator>;
using sPTC = PauliTermContainer<SymbolicCoeff_t>;

struct LambdaPolicy : public SchedulingPolicy {
    public:
	using predicate_t = std::function<bool(SimulationState const&, OperationType, Timing)>;
	LambdaPolicy(predicate_t const& pred) : predicate{ pred } {}
	~LambdaPolicy() override {}
	bool should_apply(SimulationState const& state, OperationType op_type, Timing timing) override {
		return predicate(state, op_type, timing);
	}

    private:
	predicate_t predicate;
};

// very very slow. That's why it's not in propauli.
bool operator==(SymbolicCoeff_t const& lhs, SymbolicCoeff_t const& rhs) {
	return lhs.to_string() == rhs.to_string();
}

auto default_runtime = RuntimePolicy{DefaultExecutionPolicy{}};

PYBIND11_MODULE(_core, m) {
	m.doc() = "Core C++ functionality for pyrauli, wrapped with pybind11";

	py::class_<SequentialPolicy>(m, "SequentialPolicy", "Sequential runtime");
	#if defined(_OPENMP)
		py::class_<OpenMPPolicy>(m, "ParallelPolicy", "OpenMP Parallel runtime");
	#endif
	py::class_<RuntimePolicy>(m, "RuntimePolicy", "Runtime execution policy.")
		.def(py::init([] () { return default_runtime; }));
	m.attr("seq") = py::cast(RuntimePolicy{seq});
	#if defined(_OPENMP)
		m.attr("par") = py::cast(RuntimePolicy{par});
	#endif

	// Enums
	py::enum_<Pauli_enum>(m, "PauliEnum", "Enumeration for single Pauli operators (I, X, Y, Z).")
		.value("I", Pauli_enum::I)
		.value("X", Pauli_enum::X)
		.value("Y", Pauli_enum::Y)
		.value("Z", Pauli_enum::Z);
	py::enum_<Pauli_gates>(m, "PauliGate", "Enumeration for single-qubit Pauli gates (I, X, Y, Z).")
		.value("I", Pauli_gates::I)
		.value("X", Pauli_gates::X)
		.value("Y", Pauli_gates::Y)
		.value("Z", Pauli_gates::Z);
	py::enum_<Clifford_Gates_1Q>(m, "CliffordGate", "Enumeration for single-qubit Clifford gates.")
		.value("H", Clifford_Gates_1Q::H, "Hadamard gate.");
	py::enum_<UnitalNoise>(m, "UnitalNoise", "Enumeration for unital noise channels.")
		.value("Depolarizing", UnitalNoise::Depolarizing, "Depolarizing noise channel.")
		.value("Dephasing", UnitalNoise::Dephasing, "Dephasing noise channel.");
	py::enum_<QGate>(m, "QGate", "Enumeration for all supported quantum gates and noise channels.")
		.value("I", QGate::I)
		.value("X", QGate::X)
		.value("Y", QGate::Y)
		.value("Z", QGate::Z)
		.value("H", QGate::H)
		.value("Rz", QGate::Rz)
		.value("Cx", QGate::Cx)
		.value("AmplitudeDamping", QGate::AmplitudeDamping)
		.value("Depolarizing", QGate::Depolarizing)
		.value("Dephasing", QGate::Dephasing);

	// Pauli class
	py::class_<Pauli>(m, "Pauli", "Represents a single Pauli operator (I, X, Y, or Z).")
		.def(py::init<Pauli_enum>(), "Constructs from a PauliEnum.")
		.def(py::init<char>(), "Constructs from a character ('I', 'X', 'Y', or 'Z').")
		.def(py::init<std::string_view>(), "Constructs from a single-character string.")
		.def("commutes_with", &Pauli::commutes_with, "Checks if this Pauli operator commutes with another.")
		.def("weight", &Pauli::weight, "Calculates the Pauli weight (1 if not Identity, 0 otherwise).")
		.def("apply_pauli", &Pauli::apply_pauli,
		     "Applies a Pauli gate to this operator (in the Heisenberg picture).")
		.def("apply_unital_noise", &Pauli::apply_unital_noise<coeff_t>,
		     "Applies a unital noise channel to this operator.")
		.def("apply_unital_noise", &Pauli::apply_unital_noise<SymbolicCoeff_t>,
		     "Applies a unital noise channel to this operator.")
		.def("apply_clifford", &Pauli::apply_clifford,
		     "Applies a single-qubit Clifford gate to this operator, modifying it in place.")
		.def("apply_cx", &Pauli::apply_cx,
		     "Applies the control part of a CNOT gate to this operator, modifying it and the target in place.")
		.def(py::self == py::self)
		.def(py::self != py::self)
		.def("__repr__", [](const Pauli& p) {
			std::stringstream ss;
			ss << p;
			return ss.str();
		});

	// PauliTerm class
	py::class_<PauliTerm<coeff_t>>(
		m, "PauliTerm",
		"Represents a single term in an observable, consisting of a Pauli string and a coefficient.")
		.def(py::init<std::string_view, coeff_t>(), py::arg("pauli_string"), py::arg("coefficient") = 1.0,
		     "Constructs from a string representation and a coefficient.")
		.def("apply_pauli", &PauliTerm<coeff_t>::apply_pauli,
		     "Applies a Pauli gate to a specific qubit of the term.")
		.def("apply_clifford", &PauliTerm<coeff_t>::apply_clifford,
		     "Applies a Clifford gate to a specific qubit of the term.")
		.def("apply_unital_noise", &PauliTerm<coeff_t>::apply_unital_noise,
		     "Applies a unital noise channel to a specific qubit of the term.")
		.def("apply_cx", &PauliTerm<coeff_t>::apply_cx, "Applies a CNOT gate to the term.")
		.def("apply_rz", &PauliTerm<coeff_t>::apply_rz, "Applies an Rz gate, potentially splitting the term.")
		.def("apply_amplitude_damping_xy", &PauliTerm<coeff_t>::apply_amplitude_damping_xy,
		     "Applies the X/Y part of the amplitude damping channel.")
		.def("apply_amplitude_damping_z", &PauliTerm<coeff_t>::apply_amplitude_damping_z,
		     "Applies the Z part of the amplitude damping channel, splitting the term.")
		.def("expectation_value", &PauliTerm<coeff_t>::expectation_value,
		     "Calculates the expectation value of this single term.")
		.def("pauli_weight", &PauliTerm<coeff_t>::pauli_weight,
		     "Calculates the Pauli weight (number of non-identity operators).")
		.def_property_readonly("coefficient", &PauliTerm<coeff_t>::coefficient, "The coefficient of the term.")
		.def("__getitem__", [](const PauliTerm<coeff_t>& pt, size_t i) { return pt[i]; })
		.def("__setitem__", [](PauliTerm<coeff_t>& pt, size_t i, const Pauli& p) { pt[i] = p; })
		.def("__len__", &PauliTerm<coeff_t>::size)
		.def(py::self == py::self)
		.def(py::self != py::self)
		.def("__repr__", [](const PauliTerm<coeff_t>& pt) {
			std::stringstream ss;
			ss << pt;
			return ss.str();
		});

	// Observable class
	py::class_<Observable<coeff_t>>(m, "Observable",
					"Represents a quantum observable as a linear combination of Pauli strings.")
		.def(py::init<std::string_view, coeff_t>(), py::arg("pauli_string"), py::arg("coeff") = 1.0,
		     "Constructs an observable from a single Pauli string.")
		.def(py::init<std::initializer_list<std::string_view>>(),
		     "Constructs an observable from an initializer_list of Pauli strings.")
		// Use a lambda to correctly initialize from a list of PauliTerm objects
		.def(py::init([](const std::vector<PauliTerm<coeff_t>>& paulis) {
			     return Observable<coeff_t>(paulis.begin(), paulis.end());
		     }),
		     "Constructs an observable from a list of PauliTerm objects.")
		.def(py::init([](const std::vector<std::string>& paulis) {
			     return Observable<coeff_t>(paulis.begin(), paulis.end());
		     }),
		     "Constructs an observable from a list of Pauli strings.")
		.def("apply_pauli", &Observable<coeff_t>::apply_pauli<RuntimePolicy>,
		     "Applies a single-qubit Pauli gate to the observable.", py::arg("pauli_gate"), py::arg("qubit"), py::arg("runtime") = default_runtime)
		.def("apply_clifford", &Observable<coeff_t>::apply_clifford<RuntimePolicy>,
		     "Applies a single-qubit Clifford gate to the observable.", py::arg("clifford_gate"), py::arg("qubit"), py::arg("runtime") = default_runtime)
		.def("apply_unital_noise", &Observable<coeff_t>::apply_unital_noise<RuntimePolicy>,
		     "Applies a single-qubit unital noise channel.", py::arg("unital_noise_type"), py::arg("qubit"), py::arg("noise_strength"), py::arg("runtime") = default_runtime)
		.def("apply_cx", &Observable<coeff_t>::apply_cx<RuntimePolicy>, "Applies a CNOT (CX) gate to the observable.", py::arg("qubit_control"), py::arg("qubit_target"), py::arg("runtime") = default_runtime)
		.def("apply_rz", &Observable<coeff_t>::apply_rz<RuntimePolicy>,
		     "Applies a single-qubit Rz rotation gate to the observable.", py::arg("qubit"), py::arg("theta"), py::arg("runtime") = default_runtime)
		.def("apply_amplitude_damping", &Observable<coeff_t>::apply_amplitude_damping<RuntimePolicy>,
		     "Applies an amplitude damping noise channel.", py::arg("qubit"), py::arg("noise_strength"), py::arg("runtime") = default_runtime)
		.def("expectation_value", &Observable<coeff_t>::expectation_value<RuntimePolicy>,
		     "Calculates the expectation value of the observable.", py::arg("runtime") = default_runtime)
		.def("merge", &Observable<coeff_t>::merge<RuntimePolicy>, "Merges Pauli terms with identical Pauli strings.", py::arg("runtime") = default_runtime)
		.def("size", &Observable<coeff_t>::size, "Gets the number of Pauli terms in the observable.")
		.def("truncate", [](Observable<coeff_t>& obs, TruncatorPtr ptr) { return obs.truncate(*ptr); },
			"Truncates the observable based on a given truncation strategy.")
		.def(py::self == py::self)
		.def(py::self != py::self)
		.def("__getitem__", [](const Observable<coeff_t>& obs, size_t i) { return obs[i]; })
		.def("__len__", &Observable<coeff_t>::size)
		.def(
			"__iter__",
			[](const Observable<coeff_t>& obs) { return py::make_iterator(obs.begin(), obs.end()); },
			py::keep_alive<0, 1>())
		.def("__repr__", [](const Observable<coeff_t>& obs) {
			std::stringstream ss;
			ss << obs;
			return ss.str();
		});

	// NoiseModel class
	py::class_<Noise<coeff_t>>(m, "Noise", "Defines the strengths of different noise channels.")
		.def(py::init<>())
		.def_readwrite("depolarizing_strength", &Noise<coeff_t>::depolarizing_strength)
		.def_readwrite("dephasing_strength", &Noise<coeff_t>::dephasing_strength)
		.def_readwrite("amplitude_damping_strength", &Noise<coeff_t>::amplitude_damping_strength);
	py::class_<NoiseModel<coeff_t>>(m, "NoiseModel", "A model for applying noise to quantum gates.")
		.def(py::init<>())
		.def("add_unital_noise_on_gate", &NoiseModel<coeff_t>::add_unital_noise_on_gate,
		     "Adds a unital noise channel to be applied after a specific gate type.")
		.def("add_amplitude_damping_on_gate", &NoiseModel<coeff_t>::add_amplitude_damping_on_gate,
		     "Adds an amplitude damping channel to be applied after a specific gate type.");

	// Truncators (using shared_ptr holder for polymorphism)
	py::class_<Truncator<coeff_t>, TruncatorPtr>(m, "Truncator",
						     "Abstract base class for defining truncation strategies.");
	py::class_<CoefficientTruncator<coeff_t>, Truncator<coeff_t>, CoeffTruncatorPtr>(
		m, "CoefficientTruncator", "Truncator that removes Pauli terms with small coefficients.")
		.def(py::init<coeff_t>());
	py::class_<WeightTruncator<coeff_t>, Truncator<coeff_t>, WeightTruncatorPtr>(
		m, "WeightTruncator", "Truncator that removes Pauli terms with high Pauli weight.")
		.def(py::init<size_t>());
	py::class_<NeverTruncator<coeff_t>, Truncator<coeff_t>, NeverTruncatorPtr>(
		m, "NeverTruncator", "A truncator that never removes any terms.")
		.def(py::init<>());
	py::class_<KeepNTruncator<coeff_t>, Truncator<coeff_t>, KeepNTruncatorPtr>(
		m, "KeepNTruncator",
		"A truncator that removes least significant Pauli Terms, when their numbers is above a threshold.")
		.def(py::init<std::size_t>());
	py::class_<LambdaTruncator, Truncator<coeff_t>, LambdaTruncatorPtr>(
		m, "LambdaTruncator", "A truncator that uses a Python function as a predicate.")
		.def(py::init<LambdaPredicate_t>());
	py::class_<RuntimeMultiTruncators<coeff_t>, Truncator<coeff_t>,
		   std::shared_ptr<RuntimeMultiTruncators<coeff_t>>>(
		m, "MultiTruncator", "A truncator that combines multiple truncators at runtime.")
		.def(py::init<const std::vector<TruncatorPtr>&>());

	py::enum_<OperationType>(m, "OperationType", "Type of operation in the simulation.")
		.value("BasicGate", OperationType::BasicGate)
		.value("SplittingGate", OperationType::SplittingGate)
		.value("Merge", OperationType::Merge)
		.value("Truncate", OperationType::Truncate);

	py::enum_<Timing>(m, "Timing", "Timing of a policy application relative to an operation.")
		.value("Before", Timing::Before)
		.value("After", Timing::After);

	py::class_<CompressionResult>(m, "CompressionResult",
				      "Stores the result of a compression (merge or truncate) operation.")
		.def_readonly("nb_terms_before", &CompressionResult::nb_terms_before,
			      "Number of terms before compression.")
		.def_readonly("nb_terms_merged", &CompressionResult::nb_terms_merged, "Number of terms removed/merged.")
		.def("nb_terms_after", &CompressionResult::nb_terms_after, "Number of terms after compression.")
		.def("__repr__", [](const CompressionResult& cr) {
			return "<CompressionResult: " + std::to_string(cr.nb_terms_before) + " -> " +
			       std::to_string(cr.nb_terms_after()) + ">";
		});

	py::class_<SimulationState>(m, "SimulationState", "Holds the state of the simulation at a given point in time.")
		.def_property_readonly("nb_gates_applied", &SimulationState::get_nb_gates_applied,
				       "Total number of gates applied so far.")
		.def_property_readonly("nb_splitting_gates_applied", &SimulationState::get_nb_splitting_gates_applied,
				       "Number of splitting gates applied so far.")
		.def_property_readonly("nb_splitting_gates_left", &SimulationState::get_nb_splitting_gates_left,
				       "Number of splitting gates remaining in the circuit.")
		// Add the history getters
		.def_property_readonly("terms_history", &SimulationState::get_terms_history,
				       "History of observable sizes after each operation.")
		.def_property_readonly("merge_history", &SimulationState::get_merge_history,
				       "History of merge operations.")
		.def_property_readonly("truncate_history", &SimulationState::get_truncate_history,
				       "History of truncate operations.")
		.def("__repr__", [](const SimulationState& s) {
			return "<SimulationState: " + std::to_string(s.get_nb_gates_applied()) + " gates applied>";
		});
	// Scheduling Policies (using shared_ptr holder for polymorphism)
	py::class_<SchedulingPolicy, SchedulingPolicyPtr>(m, "SchedulingPolicy",
							  "Abstract base class for defining scheduling policies.");
	py::class_<NeverPolicy, SchedulingPolicy, NeverPolicyPtr>(m, "NeverPolicy",
								  "A policy that never applies an optimization.")
		.def(py::init<>());
	py::class_<AlwaysBeforeSplittingPolicy, SchedulingPolicy, AlwaysBeforePolicyPtr>(
		m, "AlwaysBeforeSplittingPolicy",
		"A policy that applies an optimization just before every splitting gate.")
		.def(py::init<>());
	py::class_<AlwaysAfterSplittingPolicy, SchedulingPolicy, AlwaysAfterPolicyPtr>(
		m, "AlwaysAfterSplittingPolicy",
		"A policy that applies an optimization just after every splitting gate.")
		.def(py::init<>());
	py::class_<LambdaPolicy, SchedulingPolicy, std::shared_ptr<LambdaPolicy>>(
		m, "LambdaPolicy", "A policy that uses a Python function to determine when to apply optimizations.")
		.def(py::init<LambdaPolicy::predicate_t>());

	// Circuit class
	py::class_<Circuit<coeff_t>>(m, "Circuit",
				     "Represents a quantum circuit and provides a high-level simulation interface.")
		.def(py::init<unsigned, std::shared_ptr<Truncator<coeff_t>>, const NoiseModel<coeff_t>&,
			      std::shared_ptr<SchedulingPolicy>, std::shared_ptr<SchedulingPolicy>>(),
		     py::arg("nb_qubits"), py::arg("truncator") = std::make_shared<NeverTruncator<coeff_t>>(),
		     py::arg("noise_model") = NoiseModel<coeff_t>(),
		     py::arg("merge_policy") = std::make_shared<AlwaysAfterSplittingPolicy>(),
		     py::arg("truncate_policy") = std::make_shared<AlwaysAfterSplittingPolicy>())
		.def("nb_qubits", &Circuit<coeff_t>::nb_qubits, "Gets the number of qubits in the circuit.")
		// Use lambdas to resolve templated overloads
		.def(
			"add_operation",
			[](Circuit<coeff_t>& self, std::string op, unsigned q1) { self.add_operation(op, q1); },
			"Adds a single-qubit gate.", py::arg("op"), py::arg("qubit"))
		.def(
			"add_operation",
			[](Circuit<coeff_t>& self, std::string op, unsigned q1, coeff_t p) {
				self.add_operation(op, q1, p);
			},
			"Adds a single-qubit gate with a parameter.", py::arg("op"), py::arg("qubit"), py::arg("param"))
		.def(
			"add_operation",
			[](Circuit<coeff_t>& self, std::string op, unsigned q1, unsigned q2) {
				self.add_operation(op, q1, q2);
			},
			"Adds a two-qubit gate.", py::arg("op"), py::arg("control"), py::arg("target"))
		.def("run", &Circuit<coeff_t>::run<Observable<coeff_t> const&, RuntimePolicy>, "Simulate one observable on the circuit and return its evolved self.", py::arg("target_observable"), py::arg("runtime") = default_runtime)
		.def("run", &Circuit<coeff_t>::run<std::vector<Observable<coeff_t>> const&, RuntimePolicy>, "Simulate a batch of observable and returns each of them.", py::arg("target_observables"), py::arg("runtime") = default_runtime)
		.def("expectation_value", &Circuit<coeff_t>::expectation_value<Observable<coeff_t> const&, RuntimePolicy>, "Simulate one observable on the circuit and return only its expectation value.", py::arg("target_observable"), py::arg("runtime") = default_runtime)
		.def("expectation_value", &Circuit<coeff_t>::expectation_value<std::vector<Observable<coeff_t>> const&, RuntimePolicy>, "Simulate a batch of observable and returns each of their expectation values.", py::arg("target_observables"), py::arg("runtime") = default_runtime)
		.def("reset", &Circuit<coeff_t>::reset, "Clears all operations from the circuit.")
		.def("set_truncator", &Circuit<coeff_t>::set_truncator, "Sets a new truncator for the circuit.")
		.def("set_merge_policy", &Circuit<coeff_t>::set_merge_policy,
		     "Sets a new policy for when to merge Pauli terms.")
		.def("set_truncate_policy", &Circuit<coeff_t>::set_truncate_policy,
		     "Sets a new policy for when to truncate the observable.");


	py::class_<PTC::ReadOnlyNonOwningPauliTermPacked>(m, "ReadOnlyPackedPauliTermView",
							  "A read-only, non-owning view of a packed Pauli term.")
		.def_property_readonly("coefficient", &PTC::ReadOnlyNonOwningPauliTermPacked::coefficient,
				       "The coefficient of the term.")
		.def_property_readonly("nb_qubits", &PTC::ReadOnlyNonOwningPauliTermPacked::size,
				       "The number of qubits in the term.")
		.def("pauli_weight", &PTC::ReadOnlyNonOwningPauliTermPacked::pauli_weight,
		     "Calculates the Pauli weight (number of non-identity operators).")
		.def("expectation_value", &PTC::ReadOnlyNonOwningPauliTermPacked::expectation_value,
		     "Calculates the expectation value of this single term.")
		.def(
			"to_pauli_term",
			[](const PTC::ReadOnlyNonOwningPauliTermPacked& self) {
				return static_cast<PauliTerm<coeff_t>>(self);
			},
			"Creates an owning PauliTerm copy from this view.")
		.def("__len__", &PTC::ReadOnlyNonOwningPauliTermPacked::size)
		.def("__getitem__", &PTC::ReadOnlyNonOwningPauliTermPacked::get_pauli,
		     "Gets the Pauli operator at a specific qubit index.")
		.def(py::self == py::self)
		.def(
			"__eq__",
			[](const PTC::ReadOnlyNonOwningPauliTermPacked& self, const PauliTerm<coeff_t>& other) {
				return self == other;
			},
			"Compares this view with an owning PauliTerm object.")
		.def("__repr__", [](const PTC::ReadOnlyNonOwningPauliTermPacked& pt) {
			std::stringstream ss;
			ss << pt;
			return ss.str();
		});

	py::class_<PTC::NonOwningPauliTermPacked>(m, "PackedPauliTermView",
						  "A mutable, non-owning view of a packed Pauli term.")
		.def_property("coefficient", &PTC::NonOwningPauliTermPacked::coefficient,
			      &PTC::NonOwningPauliTermPacked::set_coefficient,
			      "The coefficient of the term (read/write).")
		.def_property_readonly("nb_qubits", &PTC::NonOwningPauliTermPacked::size,
				       "The number of qubits in the term.")
		.def("pauli_weight", &PTC::NonOwningPauliTermPacked::pauli_weight,
		     "Calculates the Pauli weight (number of non-identity operators).")
		.def("expectation_value", &PTC::NonOwningPauliTermPacked::expectation_value,
		     "Calculates the expectation value of this single term.")
		.def(
			"to_pauli_term",
			[](const PTC::NonOwningPauliTermPacked& self) { return static_cast<PauliTerm<coeff_t>>(self); },
			"Creates an owning PauliTerm copy from this view.")
		.def("add_coeff", &PTC::NonOwningPauliTermPacked::add_coeff, "Adds a value to the term's coefficient.")
		.def("__len__", &PTC::NonOwningPauliTermPacked::size)
		.def("__getitem__", &PTC::NonOwningPauliTermPacked::get_pauli,
		     "Gets the Pauli operator at a specific qubit index.")
		.def("__setitem__", &PTC::NonOwningPauliTermPacked::set_pauli,
		     "Sets the Pauli operator at a specific qubit index.")
		.def(py::self == py::self)
		.def(
			"__eq__",
			[](const PTC::NonOwningPauliTermPacked& self, const PauliTerm<coeff_t>& other) {
				return self == other;
			},
			"Compares this view with an owning PauliTerm object.")
		.def("__repr__", [](const PTC::NonOwningPauliTermPacked& pt) {
			std::stringstream ss;
			ss << pt;
			return ss.str();
		});

	// Symbolic 
	py::class_<Variable>(m, "Variable", "Symbolic string variable")
		.def(py::init<std::string>());

	py::class_<SymbolicCoeff_t>(m, "SymbolicCoefficient", "An easy to use symbolic coefficient.")
		.def(py::init<coeff_t>(), "Construct from a constant value.")
		.def(py::init<std::string>(), "Construct from a variable name (string).")
		.def(py::init<Variable>(), "Construct from a variable.")
		.def("to_string", &SymbolicCoeff_t::to_string, "Convert to string using a formatting for real.", py::arg("format") = "{:.3f}")
		.def("evaluate", &SymbolicCoeff_t::evaluate, "Evaluate into a real by replacing variables.", py::arg("variables") = std::unordered_map<std::string, SymbolicCoeff_t>{})
		.def("symbolic_evaluate", &SymbolicCoeff_t::symbolic_evaluate, "Evaluate into another symbolic coefficient by replacing some variables.", py::arg("variables") = std::unordered_map<std::string, SymbolicCoeff_t>{})
		.def("simplified", &SymbolicCoeff_t::simplified, "Returns simplified symbolic coefficient using arithmetic rules.")
		.def("optimize", &SymbolicCoeff_t::optimize, "Returns a simplified and compiled symbolic coefficient.")
		.def("compile", &SymbolicCoeff_t::compile, "Returns a fast compiled symbolic coefficient for faster evaluation.")
       		.def("__repr__", [](SymbolicCoeff_t const& coeff) { return coeff.to_string(); })
	      	.def(py::self *= py::self)
	      	.def(py::self += py::self)
	      	.def(py::self /= py::self)
	      	.def(py::self -= py::self)
	     	.def(-py::self)
	    	.def(py::self + py::self)
	    	.def(py::self * py::self)
	    	.def(py::self / py::self)
	    	.def(py::self - py::self)
		.def(py::self *= float())
	      	.def(py::self += float())
	      	.def(py::self /= float())
	      	.def(py::self -= float())
	    	.def(py::self + float())
	    	.def(py::self * float())
	    	.def(py::self / float())
	    	.def(py::self - float())
	    	.def(float() + py::self)
	    	.def(float() * py::self)
	    	.def(float() / py::self)
	    	.def(float() - py::self)
	   	.def("cos", &SymbolicCoeff_t::cos, "Apply cosinus")
	   	.def("sin", &SymbolicCoeff_t::sin, "Apply sinus")
	   	.def("sqrt", &SymbolicCoeff_t::sqrt, "Apply sqrt");

	py::class_<CompiledExpression<coeff_t>>(m, "CompiledExpression", "A very fast static symbolic expression, optimized for evaluation.")
		.def("evaluate", &CompiledExpression<coeff_t>::evaluate, "Evaluate the compîled expressions with the provided variables.");

	py::class_<PauliTerm<SymbolicCoeff_t>>(
		m, "SymbolicPauliTerm",
		"Represents a single term in an observable, consisting of a Pauli string and a coefficient.")
		.def(py::init<std::string_view, SymbolicCoeff_t>(), py::arg("pauli_string"), py::arg("coefficient") = SymbolicCoeff_t{1.0f},
		     "Constructs from a string representation and a coefficient.")
		.def(py::init([](std::string_view sv, std::string  const& variable_name) {
			return PauliTerm<SymbolicCoeff_t>{sv, SymbolicCoeff_t{Variable{variable_name}}};
		     }),
		     "Constructs from a string representation and a coefficient.")
		.def(py::init([](std::string_view sv, coeff_t coeff) {
			     return PauliTerm<SymbolicCoeff_t>{sv, SymbolicCoeff_t{coeff}};
		     }), "Construct from a constant coefficient")
		.def("apply_pauli", &PauliTerm<SymbolicCoeff_t>::apply_pauli,
		     "Applies a Pauli gate to a specific qubit of the term.")
		.def("apply_clifford", &PauliTerm<SymbolicCoeff_t>::apply_clifford,
		     "Applies a Clifford gate to a specific qubit of the term.")
		.def("apply_unital_noise", &PauliTerm<SymbolicCoeff_t>::apply_unital_noise,
		     "Applies a unital noise channel to a specific qubit of the term.")
		.def("apply_cx", &PauliTerm<SymbolicCoeff_t>::apply_cx, "Applies a CNOT gate to the term.")
		.def("apply_rz", &PauliTerm<SymbolicCoeff_t>::apply_rz, "Applies an Rz gate, potentially splitting the term.")
		.def("apply_amplitude_damping_xy", &PauliTerm<SymbolicCoeff_t>::apply_amplitude_damping_xy,
		     "Applies the X/Y part of the amplitude damping channel.")
		.def("apply_amplitude_damping_z", &PauliTerm<SymbolicCoeff_t>::apply_amplitude_damping_z,
		     "Applies the Z part of the amplitude damping channel, splitting the term.")
		.def("expectation_value", &PauliTerm<SymbolicCoeff_t>::expectation_value,
		     "Calculates the expectation value of this single term.")
		.def("pauli_weight", &PauliTerm<SymbolicCoeff_t>::pauli_weight,
		     "Calculates the Pauli weight (number of non-identity operators).")
		.def_property_readonly("coefficient", &PauliTerm<SymbolicCoeff_t>::coefficient, "The coefficient of the term.")
		.def("__getitem__", [](const PauliTerm<SymbolicCoeff_t>& pt, size_t i) { return pt[i]; })
		.def("__setitem__", [](PauliTerm<SymbolicCoeff_t>& pt, size_t i, const Pauli& p) { pt[i] = p; })
		.def("__len__", &PauliTerm<SymbolicCoeff_t>::size)
		.def(py::self == py::self)
		.def(py::self != py::self)
		.def("__repr__", [](const PauliTerm<SymbolicCoeff_t>& pt) {
			std::stringstream ss;
			ss << pt;
			return ss.str();
		});

	
	py::class_<SymbolicObs_t>(m, "SymbolicObservable",
					"Represents a quantum observable symbolically, as a linear combination of Pauli strings.")
		.def(py::init<std::string_view, SymbolicCoeff_t>(), py::arg("pauli_string"), py::arg("coeff") = SymbolicCoeff_t{1.f},
		     "Constructs an observable from a single Pauli string.")
		.def(py::init([](std::string_view sv, std::string const& variable_name) {
			     return Observable<SymbolicCoeff_t>{sv, SymbolicCoeff_t{Variable{variable_name}}};
		     }), "Construct from a variable coefficient")
		.def(py::init([](std::string_view sv, coeff_t coeff) {
			     return Observable<SymbolicCoeff_t>{sv, SymbolicCoeff_t{coeff}};
		     }), "Construct from a constant coefficient")
		.def(py::init<std::initializer_list<std::string_view>>(),
		     "Constructs an observable from an initializer_list of Pauli strings.")
		// Use a lambda to correctly initialize from a list of PauliTerm objects
		.def(py::init([](const std::vector<PauliTerm<SymbolicCoeff_t>>& paulis) {
			     return Observable<SymbolicCoeff_t>(paulis.begin(), paulis.end());
		     }),
		     "Constructs an observable from a list of PauliTerm objects.")
		.def(py::init([](const std::vector<std::string>& paulis) {
			     return Observable<SymbolicCoeff_t>(paulis.begin(), paulis.end());
		     }),
		     "Constructs an observable from a list of Pauli strings.")
		.def("apply_pauli", &Observable<SymbolicCoeff_t>::apply_pauli<RuntimePolicy>,
		     "Applies a single-qubit Pauli gate to the observable.", py::arg("pauli_gate"), py::arg("qubit"), py::arg("runtime") = default_runtime)
		.def("apply_clifford", &Observable<SymbolicCoeff_t>::apply_clifford<RuntimePolicy>,
		     "Applies a single-qubit Clifford gate to the observable.", py::arg("clifford_gate"), py::arg("qubit"), py::arg("runtime") = default_runtime)
		.def("apply_unital_noise", &Observable<SymbolicCoeff_t>::apply_unital_noise<RuntimePolicy>,
		     "Applies a single-qubit unital noise channel.", py::arg("unital_noise_type"), py::arg("qubit"), py::arg("noise_strength"), py::arg("runtime") = default_runtime)
		.def("apply_cx", &Observable<SymbolicCoeff_t>::apply_cx<RuntimePolicy>, "Applies a CNOT (CX) gate to the observable.", py::arg("qubit_control"), py::arg("qubit_target"), py::arg("runtime") = default_runtime)
		.def("apply_rz", &Observable<SymbolicCoeff_t>::apply_rz<RuntimePolicy>,
		     "Applies a single-qubit Rz rotation gate to the observable.", py::arg("qubit"), py::arg("noise_strength"), py::arg("runtime") = default_runtime)
		.def("apply_amplitude_damping", &Observable<SymbolicCoeff_t>::apply_amplitude_damping<RuntimePolicy>,
		     "Applies an amplitude damping noise channel.", py::arg("qubit"), py::arg("noise_strength"), py::arg("runtime") = default_runtime)
		.def("expectation_value", &Observable<SymbolicCoeff_t>::expectation_value<RuntimePolicy>,
		     "Calculates the expectation value of the observable.", py::arg("runtime") = default_runtime)
		.def("merge", &Observable<SymbolicCoeff_t>::merge<RuntimePolicy>, "Merges Pauli terms with identical Pauli strings.", py::arg("runtime") = default_runtime)
		.def("size", &Observable<SymbolicCoeff_t>::size, "Gets the number of Pauli terms in the observable.")
		.def("simplify", &Observable<SymbolicCoeff_t>::simplify<SymbolicCoeff_t>, py::arg("variable_map") = std::unordered_map<std::string, coeff_t>{}, "Simplify the observable coefficient and replace variables.")
		.def(
			"truncate", [](Observable<SymbolicCoeff_t>& obs, SymbolicTruncatorPtr ptr) { return obs.truncate(*ptr); },
			"Truncates the observable based on a given truncation strategy.")
		.def(py::self == py::self)
		.def(py::self != py::self)
		.def("__getitem__", [](const Observable<SymbolicCoeff_t>& obs, size_t i) { return obs[i]; })
		.def("__len__", &Observable<SymbolicCoeff_t>::size)
		.def(
			"__iter__",
			[](const Observable<SymbolicCoeff_t>& obs) { return py::make_iterator(obs.begin(), obs.end()); },
			py::keep_alive<0, 1>())
		.def("__repr__", [](const Observable<SymbolicCoeff_t>& obs) {
			std::stringstream ss;
			ss << obs;
			return ss.str();
		});

	py::class_<Noise<SymbolicCoeff_t>>(m, "SymbolicNoise", "Defines the strengths of different noise channels.")
		.def(py::init<>())
		.def_readwrite("depolarizing_strength", &Noise<SymbolicCoeff_t>::depolarizing_strength)
		.def_readwrite("dephasing_strength", &Noise<SymbolicCoeff_t>::dephasing_strength)
		.def_readwrite("amplitude_damping_strength", &Noise<SymbolicCoeff_t>::amplitude_damping_strength);

	py::class_<NoiseModel<SymbolicCoeff_t>>(m, "SymbolicNoiseModel", "A model for applying noise to quantum gates.")
		.def(py::init<>())
		.def("add_unital_noise_on_gate",
			     &NoiseModel<SymbolicCoeff_t>::add_unital_noise_on_gate,
		     "Adds a unital noise channel to be applied after a specific gate type.")
		.def(
			"add_unital_noise_on_gate",
			[](NoiseModel<SymbolicCoeff_t>& self, QGate gate, UnitalNoise noise, std::string const& strength) {
				self.add_unital_noise_on_gate(gate, noise, SymbolicCoeff_t(Variable{strength}));
			},
			"Adds a unital noise channel to be applied after a specific gate type, using a variable name for strength.")
		.def("add_amplitude_damping_on_gate",
			     &NoiseModel<SymbolicCoeff_t>::add_amplitude_damping_on_gate,
		     "Adds an amplitude damping channel to be applied after a specific gate type.")
		.def(
			"add_amplitude_damping_on_gate",
			[](NoiseModel<SymbolicCoeff_t>& self, QGate gate, std::string const& strength) {
				self.add_amplitude_damping_on_gate(gate, SymbolicCoeff_t(Variable{strength}));
			},
			"Adds an amplitude damping channel to be applied after a specific gate type, using a variable name for strength.");
	// symbolic truncators
	py::class_<Truncator<SymbolicCoeff_t>, SymbolicTruncatorPtr>(m, "SymbolicTruncator",
						     "Abstract base class for defining truncation strategies.");
	py::class_<WeightTruncator<SymbolicCoeff_t>, Truncator<SymbolicCoeff_t>, SymbolicWeightTruncatorPtr>(
		m, "SymbolicWeightTruncator", "Truncator that removes Pauli terms with high Pauli weight.")
		.def(py::init<size_t>());
	py::class_<NeverTruncator<SymbolicCoeff_t>, Truncator<SymbolicCoeff_t>, SymbolicNeverTruncatorPtr>(
		m, "SymbolicNeverTruncator", "A truncator that never removes any terms.")
		.def(py::init<>());
	//py::class_<PredicateTruncator<SymbolicCoeff_t>, Truncator<SymbolicCoeff_t>, std::shared_ptr<PredicateTruncator<SymbolicLambdaPredicate_t>>>(
	//	m, "SymbolicLambdaTruncator", "A truncator that uses a Python function as a predicate.")
	//	.def(py::init<SymbolicLambdaPredicate_t>());
	py::class_<RuntimeMultiTruncators<SymbolicCoeff_t>, Truncator<SymbolicCoeff_t>,
		   std::shared_ptr<RuntimeMultiTruncators<SymbolicCoeff_t>>>(
		m, "SymbolicMultiTruncator", "A truncator that combines multiple truncators at runtime.")
		.def(py::init<const std::vector<SymbolicTruncatorPtr>&>());

	py::class_<Circuit<SymbolicCoeff_t>>(m, "SymbolicCircuit",
				     "Represents a quantum circuit and provides a high-level simulation interface.")
		.def(py::init<unsigned, std::shared_ptr<Truncator<SymbolicCoeff_t>>, const NoiseModel<SymbolicCoeff_t>&,
			      std::shared_ptr<SchedulingPolicy>, std::shared_ptr<SchedulingPolicy>>(),
		     py::arg("nb_qubits"), py::arg("truncator") = std::make_shared<NeverTruncator<SymbolicCoeff_t>>(),
		     py::arg("noise_model") = NoiseModel<SymbolicCoeff_t>(),
		     py::arg("merge_policy") = std::make_shared<AlwaysAfterSplittingPolicy>(),
		     py::arg("truncate_policy") = std::make_shared<AlwaysAfterSplittingPolicy>())
		.def("nb_qubits", &Circuit<SymbolicCoeff_t>::nb_qubits, "Gets the number of qubits in the circuit.")
		// Use lambdas to resolve templated overloads
		.def(
			"add_operation",
			[](Circuit<SymbolicCoeff_t>& self, std::string op, unsigned q1) { self.add_operation(op, q1); },
			"Adds a single-qubit gate.", py::arg("op"), py::arg("qubit"))
		.def(
			"add_operation",
			[](Circuit<SymbolicCoeff_t>& self, std::string op, unsigned q1, SymbolicCoeff_t p) {
				self.add_operation(op, q1, p);
			},
			"Adds a single-qubit gate with a parameter.", py::arg("op"), py::arg("qubit"), py::arg("param"))
		.def(
			"add_operation",
			[](Circuit<SymbolicCoeff_t>& self, std::string op, unsigned q1, std::string const& p) {
				self.add_operation(op, q1, SymbolicCoeff_t(Variable(p)));
			},
			"Adds a single-qubit gate with a parameter.", py::arg("op"), py::arg("qubit"), py::arg("param"))
		.def(
			"add_operation",
			[](Circuit<SymbolicCoeff_t>& self, std::string op, unsigned q1, unsigned q2) {
				self.add_operation(op, q1, q2);
			},
			"Adds a two-qubit gate.", py::arg("op"), py::arg("control"), py::arg("target"))
		.def("run", &Circuit<SymbolicCoeff_t>::run<Observable<SymbolicCoeff_t> const&, RuntimePolicy>, "Simulate one observable on the circuit and return its evolved self.", py::arg("target_observable"), py::arg("runtime") = default_runtime)
		.def("run", &Circuit<SymbolicCoeff_t>::run<std::vector<Observable<SymbolicCoeff_t>> const&, RuntimePolicy>, "Simulate a batch of observable and returns each of them.", py::arg("target_observables"), py::arg("runtime") = default_runtime)
		.def("expectation_value", &Circuit<SymbolicCoeff_t>::expectation_value<Observable<SymbolicCoeff_t> const&, RuntimePolicy>, "Simulate one observable on the circuit and return only its expectation value.", py::arg("target_observable"), py::arg("runtime") = default_runtime)
		.def("expectation_value", &Circuit<SymbolicCoeff_t>::expectation_value<std::vector<Observable<SymbolicCoeff_t>> const&, RuntimePolicy>, "Simulate a batch of observable and returns each of their expectation values.", py::arg("target_observables"), py::arg("runtime") = default_runtime)
		.def("reset", &Circuit<SymbolicCoeff_t>::reset, "Clears all operations from the circuit.")
		.def("set_truncator", &Circuit<SymbolicCoeff_t>::set_truncator, "Sets a new truncator for the circuit.")
		.def("set_merge_policy", &Circuit<SymbolicCoeff_t>::set_merge_policy,
		     "Sets a new policy for when to merge Pauli terms.")
		.def("set_truncate_policy", &Circuit<SymbolicCoeff_t>::set_truncate_policy,
		     "Sets a new policy for when to truncate the observable.");

	py::class_<sPTC::ReadOnlyNonOwningPauliTermPacked>(m, "SymbolicReadOnlyPackedPauliTermView",
							  "A read-only, non-owning view of a packed Pauli term.")
		.def_property_readonly("coefficient", &sPTC::ReadOnlyNonOwningPauliTermPacked::coefficient,
				       "The coefficient of the term.")
		.def_property_readonly("nb_qubits", &sPTC::ReadOnlyNonOwningPauliTermPacked::size,
				       "The number of qubits in the term.")
		.def("pauli_weight", &sPTC::ReadOnlyNonOwningPauliTermPacked::pauli_weight,
		     "Calculates the Pauli weight (number of non-identity operators).")
		.def("expectation_value", &sPTC::ReadOnlyNonOwningPauliTermPacked::expectation_value,
		     "Calculates the expectation value of this single term.")
		.def(
			"to_pauli_term",
			[](const sPTC::ReadOnlyNonOwningPauliTermPacked& self) {
				return static_cast<PauliTerm<SymbolicCoeff_t>>(self);
			},
			"Creates an owning PauliTerm copy from this view.")
		.def("__len__", &sPTC::ReadOnlyNonOwningPauliTermPacked::size)
		.def("__getitem__", &sPTC::ReadOnlyNonOwningPauliTermPacked::get_pauli,
		     "Gets the Pauli operator at a specific qubit index.")
		.def(py::self == py::self)
		.def(
			"__eq__",
			[](const sPTC::ReadOnlyNonOwningPauliTermPacked& self, const PauliTerm<SymbolicCoeff_t>& other) {
				return self == other;
			},
			"Compares this view with an owning PauliTerm object.")
		.def("__repr__", [](const sPTC::ReadOnlyNonOwningPauliTermPacked& pt) {
			std::stringstream ss;
			ss << pt;
			return ss.str();
		});

	py::class_<sPTC::NonOwningPauliTermPacked>(m, "SymbolicPackedPauliTermView",
						  "A mutable, non-owning view of a packed Pauli term.")
		.def_property("coefficient", &sPTC::NonOwningPauliTermPacked::coefficient,
			      &sPTC::NonOwningPauliTermPacked::set_coefficient,
			      "The coefficient of the term (read/write).")
		.def_property_readonly("nb_qubits", &sPTC::NonOwningPauliTermPacked::size,
				       "The number of qubits in the term.")
		.def("pauli_weight", &sPTC::NonOwningPauliTermPacked::pauli_weight,
		     "Calculates the Pauli weight (number of non-identity operators).")
		.def("expectation_value", &sPTC::NonOwningPauliTermPacked::expectation_value,
		     "Calculates the expectation value of this single term.")
		.def(
			"to_pauli_term",
			[](const sPTC::NonOwningPauliTermPacked& self) { return static_cast<PauliTerm<SymbolicCoeff_t>>(self); },
			"Creates an owning PauliTerm copy from this view.")
		.def("add_coeff", &sPTC::NonOwningPauliTermPacked::add_coeff, "Adds a value to the term's coefficient.") 
		.def("simplify", &sPTC::NonOwningPauliTermPacked::simplify<SymbolicCoeff_t>, "Simplify (in-place) a symbolic pauli term coefficient and replace variables.")
		.def("__len__", &sPTC::NonOwningPauliTermPacked::size)
		.def("__getitem__", &sPTC::NonOwningPauliTermPacked::get_pauli,
		     "Gets the Pauli operator at a specific qubit index.")
		.def("__setitem__", &sPTC::NonOwningPauliTermPacked::set_pauli,
		     "Sets the Pauli operator at a specific qubit index.")
		.def(py::self == py::self)
		.def(
			"__eq__",
			[](const sPTC::NonOwningPauliTermPacked& self, const PauliTerm<SymbolicCoeff_t>& other) {
				return self == other;
			},
			"Compares this view with an owning PauliTerm object.")
		.def("__repr__", [](const sPTC::NonOwningPauliTermPacked& pt) {
			std::stringstream ss;
			ss << pt;
			return ss.str();
		});
}
