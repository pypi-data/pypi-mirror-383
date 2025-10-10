#pragma once

#include <string_view>
#include <filesystem>

#include <scip/config.h>

#include "ecole/export.hpp"

namespace ecole::version {

struct ECOLE_EXPORT VersionInfo {
	unsigned int major;
	unsigned int minor;
	unsigned int patch;
	std::string_view revision = "unknown";
	std::string_view build_type = "unknown";
	std::string_view build_os = "unknown";
	std::string_view build_time = "unknown";
	std::string_view build_compiler = "unknown";
};

/**
 * Ecole version, as per header files.
 */
inline constexpr auto get_ecole_header_version() noexcept -> VersionInfo {
	return {
		0,  // NOLINT(readability-magic-numbers)
		9,  // NOLINT(readability-magic-numbers)
		5,  // NOLINT(readability-magic-numbers)
		"59d96f3871c7d91a225e5a086c0ef8814535f1bc",
		"Release",
		"Linux-6.14.0-32-generic",
		"2025-10-10T08:28:36",
		"GNU-14.2.0",
	};
}

/**
 * Ecole version of the library.
 *
 * This is the version of Ecole when compiling it as a library.
 * This is useful for detecting incompatibilities when loading as a dynamic library.
 */
ECOLE_EXPORT auto get_ecole_lib_version() noexcept -> VersionInfo;

/**
 * Path of the libecole shared library when it exists.
 *
 * This is used for Ecole extensions to locate the library.
 */
ECOLE_EXPORT auto get_ecole_lib_path() -> std::filesystem::path;

/**
 * SCIP version, as per current header files.
 */
inline constexpr auto get_scip_header_version() noexcept -> VersionInfo {
	return {SCIP_VERSION_MAJOR, SCIP_VERSION_MINOR, SCIP_VERSION_PATCH};
}

/**
 * SCIP version, as per the (dynamically) loaded library.
 */
ECOLE_EXPORT auto get_scip_lib_version() noexcept -> VersionInfo;

/**
 * Path of the libscip shared library when it exists.
 *
 * This is used for Ecole extensions to locate the library.
 */
ECOLE_EXPORT auto get_scip_lib_path() -> std::filesystem::path;

/**
 * SCIP version used to compile Ecole library.
 */
ECOLE_EXPORT auto get_scip_buildtime_version() noexcept -> VersionInfo;

}  // namespace ecole
