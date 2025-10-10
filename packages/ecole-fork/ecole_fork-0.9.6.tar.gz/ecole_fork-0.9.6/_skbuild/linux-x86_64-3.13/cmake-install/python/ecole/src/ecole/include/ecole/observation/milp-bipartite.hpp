#pragma once

#include <optional>

#include <xtensor/xtensor.hpp>

#include "ecole/export.hpp"
#include "ecole/observation/abstract.hpp"
#include "ecole/utility/sparse-matrix.hpp"

namespace ecole::observation {

class ECOLE_EXPORT MilpBipartiteObs {
public:
	using value_type = double;

	static inline std::size_t constexpr n_variable_features = 9;
	enum struct ECOLE_EXPORT VariableFeatures : std::size_t {
		objective = 0,
		is_type_binary,            // One hot encoded
		is_type_integer,           // One hot encoded
		is_type_implicit_integer,  // One hot encoded
		is_type_continuous,        // One hot encoded
		has_lower_bound,
		has_upper_bound,
		lower_bound,
		upper_bound,
	};
	static inline std::size_t constexpr n_constraint_features = 1;
	enum struct ECOLE_EXPORT ConstraintFeatures : std::size_t {
		bias = 0,
	};

	xt::xtensor<value_type, 2> variable_features;
	xt::xtensor<value_type, 2> constraint_features;
	utility::coo_matrix<value_type> edge_features;
};

class ECOLE_EXPORT MilpBipartite {
public:
	MilpBipartite(bool normalize_ = false) : normalize{normalize_} {}

	auto before_reset(scip::Model& /*model*/) -> void {}

	ECOLE_EXPORT auto extract(scip::Model& model, bool done) const -> std::optional<MilpBipartiteObs>;

private:
	bool normalize = false;
};

}  // namespace ecole::observation
