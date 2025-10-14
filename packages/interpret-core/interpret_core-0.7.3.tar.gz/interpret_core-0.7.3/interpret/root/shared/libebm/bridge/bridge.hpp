// Copyright (c) 2023 The InterpretML Contributors
// Licensed under the MIT license.
// Author: Paul Koch <code@koch.ninja>

#ifndef BRIDGE_CPP_HPP
#define BRIDGE_CPP_HPP

#include "libebm.h" // bridge_c.h depends on libebm.h and we probably will eventually too
#include "logging.h"

#include "bridge.h" // UIntMain
#include "Bin.hpp"

namespace DEFINED_ZONE_NAME {
#ifndef DEFINED_ZONE_NAME
#error DEFINED_ZONE_NAME must be defined
#endif // DEFINED_ZONE_NAME

// This maximum is chosen for 2 reasons:
//   1) We use float32 in many places for speed. float32 values have exact representations for lower integers
//      but this property breaks down at 2^24. If you add 1.0 to a float32 it will stop incrementing at 2^24
//      which is a problem for us when we're adding items in a loop. By breaking the data into larger subsets
//      we can sidestep this problem. If we were only adding 1.0 each time we could go all the way to 2^24 within
//      a subset, but if sample weights are specified we can be adding non-integer values. We don't want to skew
//      our results, so keep the size of the subsets limited such that the later float32 values we add will only
//      get skewed by 1/128.
//   2) We want to store integer counts in uint32_t integers to match the size of our float32 values. uint32 values
//      have a maximum of 2^32, which is much lower than the 2^24/128 that we've set for the float considerations.
static constexpr size_t k_cSubsetSamplesMax = REPRESENTABLE_INT32_AS_FLOAT32_MAX / 128;

static constexpr size_t k_oneScore = 1;
static constexpr size_t k_dynamicScores = 0;

inline constexpr static size_t GetArrayScores(const size_t cScores) noexcept {
   return k_dynamicScores == cScores ? size_t{1} : cScores;
}

// THIS NEEDS TO BE A MACRO AND NOT AN INLINE FUNCTION -> an inline function will cause all the parameters to get
// resolved before calling the function We want any arguments to our macro to not get resolved if they are not needed at
// compile time so that we do less work if it's not needed This will effectively turn the variable into a compile time
// constant if it can be resolved at compile time The caller can put pTargetFeature->m_cBins inside the macro call and
// it will be optimize away if it isn't necessary having compile time counts of the target count of classes should allow
// for loop elimination in most cases and the restoration of SIMD instructions in places where you couldn't do so with
// variable loop iterations
#define GET_COUNT_SCORES(MACRO_cCompilerScores, MACRO_cRuntimeScores)                                                  \
   (k_dynamicScores == (MACRO_cCompilerScores) ? (MACRO_cRuntimeScores) : (MACRO_cCompilerScores))

// THIS NEEDS TO BE A MACRO AND NOT AN INLINE FUNCTION -> an inline function will cause all the parameters to get
// resolved before calling the function We want any arguments to our macro to not get resolved if they are not needed at
// compile time so that we do less work if it's not needed This will effectively turn the variable into a compile time
// constant if it can be resolved at compile time having compile time counts of the target count of classes should allow
// for loop elimination in most cases and the restoration of SIMD instructions in places where you couldn't do so with
// variable loop iterations
// TODO: use this macro more
// TODO: do we really need the static_cast to size_t here?
#define GET_COUNT_DIMENSIONS(MACRO_cCompilerDimensions, MACRO_cRuntimeDimensions)                                      \
   (k_dynamicDimensions == (MACRO_cCompilerDimensions) ? static_cast<size_t>(MACRO_cRuntimeDimensions) :               \
                                                         static_cast<size_t>(MACRO_cCompilerDimensions))

// THIS NEEDS TO BE A MACRO AND NOT AN INLINE FUNCTION -> an inline function will cause all the parameters to get
// resolved before calling the function We want any arguments to our macro to not get resolved if they are not needed at
// compile time so that we do less work if it's not needed This will effectively turn the variable into a compile time
// constant if it can be resolved at compile time having compile time counts of the target count of classes should allow
// for loop elimination in most cases and the restoration of SIMD instructions in places where you couldn't do so with
// variable loop iterations
#define GET_ITEMS_PER_BIT_PACK(MACRO_compilerBitPack, MACRO_runtimeBitPack)                                            \
   (k_cItemsPerBitPackUndefined == (MACRO_compilerBitPack) ? (MACRO_runtimeBitPack) : (MACRO_compilerBitPack))

static constexpr int k_cItemsPerBitPackUndefined = 0;

inline constexpr static bool IsRegressionLink(const LinkEbm link) noexcept {
   return Link_custom_regression == link || Link_power == link || Link_identity == link || Link_log == link ||
         Link_inverse == link || Link_inverse_square == link || Link_sqrt == link;
}
inline constexpr static bool IsClassificationLink(const LinkEbm link) noexcept {
   return Link_monoclassification == link || Link_custom_binary == link || Link_custom_ovr == link ||
         Link_custom_multinomial == link || Link_mlogit == link || Link_vlogit == link || Link_logit == link ||
         Link_probit == link || Link_cloglog == link || Link_loglog == link || Link_cauchit == link;
}
inline constexpr static bool IsRankingLink(const LinkEbm link) noexcept { return Link_custom_ranking == link; }
inline constexpr static TaskEbm IdentifyTask(const LinkEbm link) noexcept {
   return IsClassificationLink(link) ? Task_GeneralClassification :
         IsRegressionLink(link)      ? Task_Regression :
         IsRankingLink(link)         ? Task_Ranking :
                                       Task_Unknown;
}

} // namespace DEFINED_ZONE_NAME

#endif // BRIDGE_CPP_HPP