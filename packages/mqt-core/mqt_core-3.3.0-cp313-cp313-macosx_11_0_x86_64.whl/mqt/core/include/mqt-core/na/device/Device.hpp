/*
 * Copyright (c) 2023 - 2025 Chair for Design Automation, TUM
 * Copyright (c) 2025 Munich Quantum Software Company GmbH
 * All rights reserved.
 *
 * SPDX-License-Identifier: MIT
 *
 * Licensed under the MIT License
 */

#pragma once

/** @file
 * @brief The MQT QDMI device implementation for neutral atom devices.
 */

#include "mqt_na_qdmi/device.h"

#include <algorithm>
#include <cstddef>
#include <cstdint>
#include <memory>
#include <optional>
#include <string>
#include <unordered_map>
#include <utility>
#include <vector>

namespace qdmi {
class Device final {
  /// @brief Provides access to the device name.
  std::string name_;

  /// @brief The number of qubits in the device.
  size_t qubitsNum_ = 0;

  /// @brief A struct representing a unit.
  struct Unit {
    /// @brief The unit used to interpret values.
    std::string unit;
    /**
     * @brief The scale factor of the unit.
     * @details This factor must be multiplied with all values before
     * interpreting them in the unit specified by @ref Unit::unit.
     */
    double scaleFactor = 1.0;
  };
  /// @brief The unit used to interpret length values.
  Unit lengthUnit_;

  /// @brief The unit used to interpret duration values.
  Unit durationUnit_;

  /// @brief The minimum atom distance that must be maintained.
  uint64_t minAtomDistance_;

  /// @brief The list of sites.
  std::vector<std::unique_ptr<MQT_NA_QDMI_Site_impl_d>> sites_;

  /// @brief The list of operations.
  std::vector<std::unique_ptr<MQT_NA_QDMI_Operation_impl_d>> operations_;

  /// @brief The list of device sessions.
  std::unordered_map<MQT_NA_QDMI_Device_Session,
                     std::unique_ptr<MQT_NA_QDMI_Device_Session_impl_d>>
      sessions_;

  /// @brief Private constructor to enforce the singleton pattern.
  Device();

public:
  // Default move constructor and move assignment operator.
  Device(Device&&) = default;
  Device& operator=(Device&&) = default;
  // Delete copy constructor and assignment operator to enforce singleton.
  Device(const Device&) = delete;
  Device& operator=(const Device&) = delete;

  /// @returns the singleton instance of the Device class.
  [[nodiscard]] static Device& get() {
    static Device instance;
    return instance;
  }

  /// @brief Destructor for the Device class.
  ~Device() = default;

  /**
   * @brief Allocates a new device session.
   * @see MQT_NA_QDMI_device_session_alloc
   */
  auto sessionAlloc(MQT_NA_QDMI_Device_Session* session) -> int;

  /**
   * @brief Frees a device session.
   * @see MQT_NA_QDMI_device_session_free
   */
  auto sessionFree(MQT_NA_QDMI_Device_Session session) -> void;

  /**
   * @brief Query a device property.
   * @see MQT_NA_QDMI_device_session_query_device_property
   */
  auto queryProperty(QDMI_Device_Property prop, size_t size, void* value,
                     size_t* sizeRet) -> int;
};
} // namespace qdmi

/**
 * @brief Implementation of the MQT_NA_QDMI_Device_Session structure.
 */
struct MQT_NA_QDMI_Device_Session_impl_d {
private:
  /// The status of the session.
  enum class Status : uint8_t {
    ALLOCATED,   ///< The session has been allocated but not initialized
    INITIALIZED, ///< The session has been initialized and is ready for use
  };
  /// @brief The current status of the session.
  Status status_ = Status::ALLOCATED;
  /// @brief The device jobs associated with this session.
  std::unordered_map<MQT_NA_QDMI_Device_Job,
                     std::unique_ptr<MQT_NA_QDMI_Device_Job_impl_d>>
      jobs_;

public:
  /**
   * @brief Initializes the device session.
   * @see MQT_NA_QDMI_device_session_init
   */
  auto init() -> int;

  /**
   * @brief Sets a parameter for the device session.
   * @see MQT_NA_QDMI_device_session_set_parameter
   */
  auto setParameter(QDMI_Device_Session_Parameter param, size_t size,
                    const void* value) const -> int;

  /**
   * @brief Create a new device job.
   * @see MQT_NA_QDMI_device_session_create_device_job
   */
  auto createDeviceJob(MQT_NA_QDMI_Device_Job* job) -> int;

  /**
   * @brief Frees the device job.
   * @see MQT_NA_QDMI_device_job_free
   */
  auto freeDeviceJob(MQT_NA_QDMI_Device_Job job) -> void;

  /**
   * @brief Forwards a query of a device property to the device.
   * @see MQT_NA_QDMI_device_session_query_device_property
   */
  auto queryDeviceProperty(QDMI_Device_Property prop, size_t size, void* value,
                           size_t* sizeRet) const -> int;

  /**
   * @brief Forwards a query of a site property to the site.
   * @see MQT_NA_QDMI_device_session_query_site_property
   */
  auto querySiteProperty(MQT_NA_QDMI_Site site, QDMI_Site_Property prop,
                         size_t size, void* value, size_t* sizeRet) const
      -> int;

  /**
   * @brief Forwards a query of an operation property to the operation.
   * @see MQT_NA_QDMI_device_session_query_operation_property
   */
  auto queryOperationProperty(MQT_NA_QDMI_Operation operation, size_t numSites,
                              const MQT_NA_QDMI_Site* sites, size_t numParams,
                              const double* params,
                              QDMI_Operation_Property prop, size_t size,
                              void* value, size_t* sizeRet) const -> int;
};

/**
 * @brief Implementation of the MQT_NA_QDMI_Device_Job structure.
 */
struct MQT_NA_QDMI_Device_Job_impl_d {
private:
  /// @brief The device session associated with the job.
  MQT_NA_QDMI_Device_Session_impl_d* session_;

public:
  /// @brief Constructor for the MQT_NA_QDMI_Device_Job_impl_d.
  explicit MQT_NA_QDMI_Device_Job_impl_d(
      MQT_NA_QDMI_Device_Session_impl_d* session)
      : session_(session) {}
  /**
   * @brief Frees the device job.
   * @note This function just forwards to the session's @ref freeDeviceJob
   * function. This function is needed because the interface only provides the
   * job handle to the @ref QDMI_job_free function and the job's session handle
   * is private.
   * @see QDMI_job_free
   */
  auto free() -> void;

  /**
   * @brief Sets a parameter for the job.
   * @see MQT_NA_QDMI_device_job_set_parameter
   */
  static auto setParameter(QDMI_Device_Job_Parameter param, size_t size,
                           const void* value) -> int;

  /**
   * @brief Queries a property of the job.
   * @see MQT_NA_QDMI_device_job_query_property
   */
  static auto queryProperty(QDMI_Device_Job_Property prop, size_t size,
                            void* value, size_t* sizeRet) -> int;

  /**
   * @brief Submits the job to the device.
   * @see MQT_NA_QDMI_device_job_submit
   */
  static auto submit() -> int;

  /**
   * @brief Cancels the job.
   * @see MQT_NA_QDMI_device_job_cancel
   */
  static auto cancel() -> int;

  /**
   * @brief Checks the status of the job.
   * @see MQT_NA_QDMI_device_job_check
   */
  static auto check(QDMI_Job_Status* status) -> int;

  /**
   * @brief Waits for the job to complete but at most for the specified timeout.
   * @see MQT_NA_QDMI_device_job_wait
   */
  static auto wait(size_t timeout) -> int;

  /**
   * @brief Gets the results of the job.
   * @see MQT_NA_QDMI_device_job_get_results
   */
  static auto getResults(QDMI_Job_Result result, size_t size, void* data,
                         [[maybe_unused]] size_t* sizeRet) -> int;
};

/**
 * @brief Implementation of the MQT_NA_QDMI_Device_Site structure.
 */
struct MQT_NA_QDMI_Site_impl_d {
  friend MQT_NA_QDMI_Operation_impl_d;

private:
  uint64_t id_ = 0;       ///< Unique identifier of the site
  uint64_t moduleId_ = 0; ///< Identifier of the module the site belongs to
  /// Identifier of the submodule the site belongs to
  uint64_t subModuleId_ = 0;
  int64_t x_ = 0;        ///< X coordinate of the site in the lattice
  int64_t y_ = 0;        ///< Y coordinate of the site in the lattice
  uint64_t xExtent_ = 0; ///< Width of the site in the lattice (for zone sites)
  uint64_t yExtent_ = 0; ///< Height of the site in the lattice (for zone sites)
  /// @brief Collects decoherence times for the device.
  struct DecoherenceTimes {
    uint64_t t1_ = 0; ///< T1 time
    uint64_t t2_ = 0; ///< T2 time
  };
  /// @brief The decoherence times of the device.
  DecoherenceTimes decoherenceTimes_{};
  bool isZone = false; ///< Indicates if the site is a zone site

  /// @brief Constructor for regular sites.
  MQT_NA_QDMI_Site_impl_d(uint64_t id, uint64_t moduleId, uint64_t subModuleId,
                          int64_t x, int64_t y);
  /// @brief Constructor for zone sites.
  MQT_NA_QDMI_Site_impl_d(uint64_t id, int64_t x, int64_t y, uint64_t width,
                          uint64_t height);

public:
  /// @brief Factory function for regular sites.
  [[nodiscard]] static auto makeUniqueSite(uint64_t id, uint64_t moduleId,
                                           uint64_t subModuleId, int64_t x,
                                           int64_t y)
      -> std::unique_ptr<MQT_NA_QDMI_Site_impl_d>;
  /// @brief Factory function for zone sites.
  [[nodiscard]] static auto makeUniqueZone(uint64_t id, int64_t x, int64_t y,
                                           uint64_t width, uint64_t height)
      -> std::unique_ptr<MQT_NA_QDMI_Site_impl_d>;
  /**
   * @brief Queries a property of the site.
   * @see MQT_NA_QDMI_device_session_query_site_property
   */
  auto queryProperty(QDMI_Site_Property prop, size_t size, void* value,
                     size_t* sizeRet) const -> int;
};

/**
 * @brief Implementation of the MQT_NA_QDMI_Device_Operation structure.
 */
struct MQT_NA_QDMI_Operation_impl_d {
private:
  std::string name_;     ///< Name of the operation
  size_t numParameters_; ///< Number of parameters for the operation
  /**
   * @brief Number of qubits involved in the operation
   * @note This number is only valid if the operation is a multi-qubit
   * operation.
   */
  std::optional<size_t> numQubits_ = std::nullopt;
  /// Duration of the operation
  std::optional<uint64_t> duration_ = std::nullopt;
  std::optional<double> fidelity_ = std::nullopt; ///< Fidelity of the operation
  /// Interaction radius for multi-qubit operations
  std::optional<uint64_t> interactionRadius_ = std::nullopt;
  /// Blocking radius for multi-qubit operations
  std::optional<uint64_t> blockingRadius_ = std::nullopt;
  /// Mean shuttling speed
  std::optional<uint64_t> meanShuttlingSpeed_ = std::nullopt;
  /// Idling fidelity
  std::optional<double> idlingFidelity_ = std::nullopt;
  /// The operation's supported sites
  std::vector<MQT_NA_QDMI_Site> supportedSites_;
  /// Indicates if this operation is zoned (global)
  bool isZoned_ = false;

  /// @brief Constructor for the global single-qubit.
  MQT_NA_QDMI_Operation_impl_d(std::string name, size_t numParameters,
                               size_t numQubits, uint64_t duration,
                               double fidelity, MQT_NA_QDMI_Site zone);
  /// @brief Constructor for the global multi-qubit operations.
  MQT_NA_QDMI_Operation_impl_d(std::string name, size_t numParameters,
                               size_t numQubits, uint64_t duration,
                               double fidelity, uint64_t interactionRadius,
                               uint64_t blockingRadius, double idlingFidelity,
                               MQT_NA_QDMI_Site zone);
  /// @brief Constructor for the single-qubit operations.
  MQT_NA_QDMI_Operation_impl_d(std::string name, size_t numParameters,
                               uint64_t duration, double fidelity,
                               const std::vector<MQT_NA_QDMI_Site>& sites);
  /// @brief Constructor for the multi-qubit operations.
  MQT_NA_QDMI_Operation_impl_d(std::string name, size_t numParameters,
                               size_t numQubits, uint64_t duration,
                               double fidelity, uint64_t interactionRadius,
                               uint64_t blockingRadius,
                               const std::vector<MQT_NA_QDMI_Site>& sites);
  /// @brief Constructor for load and store operations.
  MQT_NA_QDMI_Operation_impl_d(std::string name, size_t numParameters,
                               uint64_t duration, double fidelity,
                               MQT_NA_QDMI_Site zone);
  /// @brief Constructor for the shuttling operations.
  MQT_NA_QDMI_Operation_impl_d(std::string name, size_t numParameters,
                               MQT_NA_QDMI_Site zone,
                               uint64_t meanShuttlingSpeed);

  /// @brief Sort the sites such that the occurrence of a given site can be
  /// determined in O(log n) time.
  auto sortSites() -> void;

public:
  /// @brief Factory function for the global single-qubit operations.
  [[nodiscard]] static auto
  makeUniqueGlobalSingleQubit(const std::string& name, size_t numParameters,
                              uint64_t duration, double fidelity,
                              MQT_NA_QDMI_Site zone)
      -> std::unique_ptr<MQT_NA_QDMI_Operation_impl_d>;
  /// @brief Factory function for the global multi-qubit operations.
  [[nodiscard]] static auto makeUniqueGlobalMultiQubit(
      const std::string& name, size_t numParameters, size_t numQubits,
      uint64_t duration, double fidelity, uint64_t interactionRadius,
      uint64_t blockingRadius, double idlingFidelity, MQT_NA_QDMI_Site zone)
      -> std::unique_ptr<MQT_NA_QDMI_Operation_impl_d>;
  /// @brief Factory function for the local single-qubit operations.
  [[nodiscard]] static auto
  makeUniqueLocalSingleQubit(const std::string& name, size_t numParameters,
                             uint64_t duration, double fidelity,
                             const std::vector<MQT_NA_QDMI_Site>& sites)
      -> std::unique_ptr<MQT_NA_QDMI_Operation_impl_d>;
  /// @brief Factory function for the local multi-qubit operations.
  [[nodiscard]] static auto makeUniqueLocalTwoQubit(
      const std::string& name, size_t numParameters, size_t numQubits,
      uint64_t duration, double fidelity, uint64_t interactionRadius,
      uint64_t blockingRadius,
      const std::vector<std::pair<MQT_NA_QDMI_Site, MQT_NA_QDMI_Site>>& sites)
      -> std::unique_ptr<MQT_NA_QDMI_Operation_impl_d>;
  /// @brief Factory function for the shuttling load operations.
  [[nodiscard]] static auto
  makeUniqueShuttlingLoad(const std::string& name, size_t numParameters,
                          uint64_t duration, double fidelity,
                          MQT_NA_QDMI_Site zone)
      -> std::unique_ptr<MQT_NA_QDMI_Operation_impl_d>;
  /// @brief Factory function for the shuttling move operations.
  [[nodiscard]] static auto
  makeUniqueShuttlingMove(const std::string& name, size_t numParameters,
                          MQT_NA_QDMI_Site zone, uint64_t meanShuttlingSpeed)
      -> std::unique_ptr<MQT_NA_QDMI_Operation_impl_d>;
  /// @brief Factory function for the shuttling store operations.
  [[nodiscard]] static auto
  makeUniqueShuttlingStore(const std::string& name, size_t numParameters,
                           uint64_t duration, double fidelity,
                           MQT_NA_QDMI_Site zone)
      -> std::unique_ptr<MQT_NA_QDMI_Operation_impl_d>;

  /**
   * @brief Queries a property of the operation.
   * @see MQT_NA_QDMI_device_session_query_operation_property
   */
  auto queryProperty(size_t numSites, const MQT_NA_QDMI_Site* sites,
                     size_t numParams, const double* params,
                     QDMI_Operation_Property prop, size_t size, void* value,
                     size_t* sizeRet) const -> int;
};
