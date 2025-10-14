/*
 * Copyright (c) 2023 - 2025 Chair for Design Automation, TUM
 * Copyright (c) 2025 Munich Quantum Software Company GmbH
 * All rights reserved.
 *
 * SPDX-License-Identifier: MIT
 *
 * Licensed under the MIT License
 */

#include "ir/operations/IfElseOperation.hpp"

#include "ir/Definitions.hpp"
#include "ir/Permutation.hpp"
#include "ir/Register.hpp"
#include "ir/operations/OpType.hpp"
#include "ir/operations/Operation.hpp"

#include <cassert>
#include <cstddef>
#include <cstdint>
#include <functional>
#include <iostream>
#include <memory>
#include <ostream>
#include <stdexcept>
#include <string>
#include <utility>

namespace qc {

ComparisonKind getInvertedComparisonKind(const ComparisonKind kind) {
  switch (kind) {
  case Lt:
    return Geq;
  case Leq:
    return Gt;
  case Gt:
    return Leq;
  case Geq:
    return Lt;
  case Eq:
    return Neq;
  case Neq:
    return Eq;
  }
  unreachable();
}

std::string toString(const ComparisonKind& kind) {
  switch (kind) {
  case Eq:
    return "==";
  case Neq:
    return "!=";
  case Lt:
    return "<";
  case Leq:
    return "<=";
  case Gt:
    return ">";
  case Geq:
    return ">=";
  }
  unreachable();
}

std::ostream& operator<<(std::ostream& os, const ComparisonKind& kind) {
  os << toString(kind);
  return os;
}

IfElseOperation::IfElseOperation(std::unique_ptr<Operation>&& thenOp,
                                 std::unique_ptr<Operation>&& elseOp,
                                 const ClassicalRegister& controlRegister,
                                 const std::uint64_t expectedValue,
                                 const ComparisonKind kind)
    : thenOp(std::move(thenOp)), elseOp(std::move(elseOp)),
      controlRegister(controlRegister), expectedValueRegister(expectedValue),
      comparisonKind(kind) {
  name = "if_else";
  type = IfElse;
  canonicalize();
}

IfElseOperation::IfElseOperation(std::unique_ptr<Operation>&& thenOp,
                                 std::unique_ptr<Operation>&& elseOp,
                                 const Bit controlBit, const bool expectedValue,
                                 const ComparisonKind kind)
    : thenOp(std::move(thenOp)), elseOp(std::move(elseOp)),
      controlBit(controlBit), expectedValueBit(expectedValue),
      comparisonKind(kind) {
  name = "if_else";
  type = IfElse;
  canonicalize();
}

IfElseOperation::IfElseOperation(const IfElseOperation& op)
    : Operation(op), thenOp(op.thenOp ? op.thenOp->clone() : nullptr),
      elseOp(op.elseOp ? op.elseOp->clone() : nullptr),
      controlRegister(op.controlRegister), controlBit(op.controlBit),
      expectedValueRegister(op.expectedValueRegister),
      expectedValueBit(op.expectedValueBit), comparisonKind(op.comparisonKind) {
}

IfElseOperation& IfElseOperation::operator=(const IfElseOperation& op) {
  if (this != &op) {
    Operation::operator=(op);
    thenOp = op.thenOp ? op.thenOp->clone() : nullptr;
    elseOp = op.elseOp ? op.elseOp->clone() : nullptr;
    controlRegister = op.controlRegister;
    controlBit = op.controlBit;
    expectedValueRegister = op.expectedValueRegister;
    expectedValueBit = op.expectedValueBit;
    comparisonKind = op.comparisonKind;
  }
  return *this;
}

void IfElseOperation::apply(const Permutation& permutation) {
  if (thenOp) {
    thenOp->apply(permutation);
  }
  if (elseOp) {
    elseOp->apply(permutation);
  }
}

bool IfElseOperation::equals(const Operation& operation,
                             const Permutation& perm1,
                             const Permutation& perm2) const {
  if (const auto* other = dynamic_cast<const IfElseOperation*>(&operation)) {
    if (controlRegister != other->controlRegister) {
      return false;
    }
    if (controlBit != other->controlBit) {
      return false;
    }
    if (expectedValueRegister != other->expectedValueRegister) {
      return false;
    }
    if (expectedValueBit != other->expectedValueBit) {
      return false;
    }
    if (comparisonKind != other->comparisonKind) {
      return false;
    }
    if (thenOp && other->thenOp) {
      if (!thenOp->equals(*other->thenOp, perm1, perm2)) {
        return false;
      }
    } else if (thenOp || other->thenOp) {
      return false;
    }
    if (elseOp && other->elseOp) {
      if (!elseOp->equals(*other->elseOp, perm1, perm2)) {
        return false;
      }
    } else if (elseOp || other->elseOp) {
      return false;
    }
    return true;
  }
  return false;
}

std::ostream&
IfElseOperation::print(std::ostream& os, const Permutation& permutation,
                       [[maybe_unused]] const std::size_t prefixWidth,
                       const std::size_t nqubits) const {
  const std::string indent(prefixWidth, ' ');

  // print condition header line
  os << indent << "\033[1m\033[35m" << "if (";
  if (controlRegister.has_value()) {
    assert(!controlBit.has_value());
    os << controlRegister->getName() << ' ' << comparisonKind << ' '
       << expectedValueRegister;
  } else if (controlBit.has_value()) {
    assert(!controlRegister.has_value());
    os << (!expectedValueBit ? "!" : "") << "c[" << controlBit.value() << "]";
  }
  os << ") {\033[0m" << '\n'; // cyan brace

  // then-block
  if (thenOp) {
    os << indent;
    thenOp->print(os, permutation, prefixWidth, nqubits);
  }
  os << '\n';

  // else-block (only if present)
  if (elseOp) {
    os << indent << "  \033[1m\033[35m} else {\033[0m" << '\n' << indent;
    elseOp->print(os, permutation, prefixWidth, nqubits);
    os << '\n';
  }

  // closing brace aligned with prefixWidth
  os << indent << "  \033[1m\033[35m}\033[0m";

  return os;
}

void IfElseOperation::dumpOpenQASM(std::ostream& of,
                                   const QubitIndexToRegisterMap& qubitMap,
                                   const BitIndexToRegisterMap& bitMap,
                                   const std::size_t indent,
                                   const bool openQASM3) const {
  of << std::string(indent * OUTPUT_INDENT_SIZE, ' ');
  of << "if (";
  if (controlRegister.has_value()) {
    assert(!controlBit.has_value());
    of << controlRegister->getName() << ' ' << comparisonKind << ' '
       << expectedValueRegister;
  } else if (controlBit.has_value()) {
    of << (!expectedValueBit ? "!" : "") << bitMap.at(*controlBit).second;
  }
  of << ") ";
  of << "{\n";
  if (thenOp) {
    thenOp->dumpOpenQASM(of, qubitMap, bitMap, indent + 1, openQASM3);
  }
  if (!elseOp) {
    of << "}\n";
    return;
  }
  of << "}";
  if (openQASM3) {
    of << " else {\n";
    elseOp->dumpOpenQASM(of, qubitMap, bitMap, indent + 1, openQASM3);
  } else {
    of << '\n' << "if (";
    if (controlRegister.has_value()) {
      assert(!controlBit.has_value());
      of << controlRegister->getName() << ' '
         << getInvertedComparisonKind(comparisonKind) << ' '
         << expectedValueRegister;
    }
    if (controlBit.has_value()) {
      assert(!controlRegister.has_value());
      of << (expectedValueBit ? "!" : "") << bitMap.at(*controlBit).second;
    }
    of << ") ";
    of << "{\n";
    elseOp->dumpOpenQASM(of, qubitMap, bitMap, indent + 1, openQASM3);
  }
  of << "}\n";
}

/**
 * @brief Canonicalizes the IfElseOperation by normalizing its internal
 * representation.
 *
 * This method ensures that the then/else branches and comparison kinds are in a
 * standard form.
 * - If the thenOp is null, swap thenOp and elseOp, and invert the comparison
 * kind.
 * - For single-bit control, only equality comparisons are supported; Neq is
 * converted to Eq with inverted expectedValueBit.
 * - If expectedValueBit is false and elseOp exists, swap thenOp and elseOp, and
 * set expectedValueBit to true.
 *
 * This normalization simplifies further processing and ensures consistent
 * behavior.
 */
void IfElseOperation::canonicalize() {
  // If thenOp is null, swap thenOp and elseOp, and invert the comparison kind.
  if (thenOp == nullptr) {
    std::swap(thenOp, elseOp);
    comparisonKind = getInvertedComparisonKind(comparisonKind);
  }
  // If control is a single bit, only equality comparisons are supported.
  if (controlBit.has_value()) {
    // Convert Neq to Eq by inverting expectedValueBit.
    if (comparisonKind == Neq) {
      comparisonKind = Eq;
      expectedValueBit = !expectedValueBit;
    }
    // Throw if comparison is not Eq (after possible conversion above).
    if (comparisonKind != Eq) {
      throw std::invalid_argument(
          "Inequality comparisons on a single bit are not supported.");
    }
    // If expectedValueBit is false and elseOp exists, swap thenOp and elseOp,
    // and set expectedValueBit to true.
    if (!expectedValueBit && elseOp != nullptr) {
      std::swap(thenOp, elseOp);
      expectedValueBit = true;
    }
  }
}

} // namespace qc

std::size_t std::hash<qc::IfElseOperation>::operator()(
    qc::IfElseOperation const& op) const noexcept {
  std::size_t seed = 0U;
  if (op.getThenOp() != nullptr) {
    qc::hashCombine(seed, std::hash<qc::Operation>{}(*op.getThenOp()));
  }
  if (op.getElseOp() != nullptr) {
    qc::hashCombine(seed, std::hash<qc::Operation>{}(*op.getElseOp()));
  }
  if (const auto& reg = op.getControlRegister(); reg.has_value()) {
    assert(!op.getControlBit().has_value());
    qc::hashCombine(seed, std::hash<qc::ClassicalRegister>{}(reg.value()));
    qc::hashCombine(seed, op.getExpectedValueRegister());
  }
  if (const auto& bit = op.getControlBit(); bit.has_value()) {
    assert(!op.getControlRegister().has_value());
    qc::hashCombine(seed, bit.value());
    qc::hashCombine(seed, static_cast<std::size_t>(op.getExpectedValueBit()));
  }
  qc::hashCombine(seed, op.getComparisonKind());
  return seed;
}
