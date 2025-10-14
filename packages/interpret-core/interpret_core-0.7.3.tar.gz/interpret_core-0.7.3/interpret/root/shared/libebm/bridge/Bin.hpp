// Copyright (c) 2023 The InterpretML Contributors
// Licensed under the MIT license.
// Author: Paul Koch <code@koch.ninja>

#ifndef BIN_HPP
#define BIN_HPP

#include <type_traits> // std::is_standard_layout
#include <stddef.h> // size_t, ptrdiff_t
#include <cmath> // abs
#include <string.h> // memcpy

#include "logging.h" // EBM_ASSERT
#include "unzoned.h" // UNUSED

#include "common.hpp"
#include "GradientPair.hpp"

namespace DEFINED_ZONE_NAME {
#ifndef DEFINED_ZONE_NAME
#error DEFINED_ZONE_NAME must be defined
#endif // DEFINED_ZONE_NAME

template<typename TFloat, typename TUInt, bool bCount, bool bWeight, bool bHessian, size_t cCompilerScores = 1>
struct Bin;

struct BinBase {
   BinBase() = default; // preserve our POD status
   ~BinBase() = default; // preserve our POD status
   void* operator new(std::size_t) = delete; // we only use malloc/free in this library
   void operator delete(void*) = delete; // we only use malloc/free in this library

   template<typename TFloat, typename TUInt, bool bCount, bool bWeight, bool bHessian, size_t cCompilerScores = 1>
   GPU_BOTH inline Bin<TFloat, TUInt, bCount, bWeight, bHessian, cCompilerScores>* Specialize() {
      return static_cast<Bin<TFloat, TUInt, bCount, bWeight, bHessian, cCompilerScores>*>(this);
   }
   template<typename TFloat, typename TUInt, bool bCount, bool bWeight, bool bHessian, size_t cCompilerScores = 1>
   GPU_BOTH inline const Bin<TFloat, TUInt, bCount, bWeight, bHessian, cCompilerScores>* Specialize() const {
      return static_cast<const Bin<TFloat, TUInt, bCount, bWeight, bHessian, cCompilerScores>*>(this);
   }

   GPU_BOTH inline void ZeroMem(const size_t cBytesPerBin, const size_t cBins = 1, const size_t iBin = 0) {
      // The C standard guarantees that memset to 0 on integer types is a zero, and IEEE-754 guarantees
      // that mem zeroing a floating point is zero.  Our Bin objects are POD and also only contain floating point
      // and unsigned integer types, so memset is legal. We do not use pointers which would be implementation defined.
      //
      // 6.2.6.2 Integer types -> 5. The values of any padding bits are unspecified.A valid (non - trap)
      // object representation of a signed integer type where the sign bit is zero is a valid object
      // representation of the corresponding unsigned type, and shall represent the same value.For any
      // integer type, the object representation where all the bits are zero shall be a representation
      // of the value zero in that type.

      static_assert(std::numeric_limits<float>::is_iec559, "memset of floats requires IEEE 754 to guarantee zeros");
      memset(IndexByte(this, iBin * cBytesPerBin), 0, cBytesPerBin * cBins);
   }
};
static_assert(std::is_standard_layout<BinBase>::value,
      "We use the struct hack in several places, so disallow non-standard_layout types in general");
static_assert(
      std::is_trivial<BinBase>::value, "We use memcpy in several places, so disallow non-trivial types in general");

template<typename TFloat, typename TUInt, bool bCount, bool bWeight, bool bHessian, size_t cCompilerScores>
struct BinData;

template<typename TFloat, typename TUInt>
static bool IsOverflowBinSize(const bool bCount, const bool bWeight, const bool bHessian, const size_t cScores);
template<typename TFloat, typename TUInt>
GPU_BOTH inline constexpr static size_t GetBinSize(
      const bool bCount, const bool bWeight, const bool bHessian, const size_t cScores);

template<typename TFloat, typename TUInt, bool bHessian, size_t cCompilerScores>
struct BinData<TFloat, TUInt, true, true, bHessian, cCompilerScores> : BinBase {
   friend void ConvertAddBin(const size_t,
         const bool,
         const size_t,
         const bool,
         const bool,
         const bool,
         const bool,
         const void* const,
         const uint64_t* const,
         const double* const,
         const bool,
         const bool,
         void* const);
   template<typename, typename> friend bool IsOverflowBinSize(const bool, const bool, const bool, const size_t);
   template<typename, typename>
   GPU_BOTH friend inline constexpr size_t GetBinSize(const bool, const bool, const bool, const size_t);

   BinData() = default; // preserve our POD status
   ~BinData() = default; // preserve our POD status
   void* operator new(std::size_t) = delete; // we only use malloc/free in this library
   void operator delete(void*) = delete; // we only use malloc/free in this library

   GPU_BOTH inline TUInt GetCountSamples() const { return m_cSamples; }
   GPU_BOTH inline void SetCountSamples(const TUInt cSamples) { m_cSamples = cSamples; }

   GPU_BOTH inline TFloat GetWeight() const { return m_weight; }
   GPU_BOTH inline void SetWeight(const TFloat weight) { m_weight = weight; }

   GPU_BOTH inline const GradientPair<TFloat, bHessian>* GetGradientPairs() const {
      return ArrayToPointer(m_aGradientPairs);
   }
   GPU_BOTH inline GradientPair<TFloat, bHessian>* GetGradientPairs() { return ArrayToPointer(m_aGradientPairs); }

 private:
   TUInt m_cSamples;
   TFloat m_weight;

   // IMPORTANT: m_aGradientPairs must be in the last position for the struct hack and this must be standard layout
   GradientPair<TFloat, bHessian> m_aGradientPairs[cCompilerScores];
};
template<typename TFloat, typename TUInt, bool bHessian, size_t cCompilerScores>
struct BinData<TFloat, TUInt, true, false, bHessian, cCompilerScores> : BinBase {
   friend void ConvertAddBin(const size_t,
         const bool,
         const size_t,
         const bool,
         const bool,
         const bool,
         const bool,
         const void* const,
         const uint64_t* const,
         const double* const,
         const bool,
         const bool,
         void* const);
   template<typename, typename> friend bool IsOverflowBinSize(const bool, const bool, const bool, const size_t);
   template<typename, typename>
   GPU_BOTH friend inline constexpr size_t GetBinSize(const bool, const bool, const bool, const size_t);

   BinData() = default; // preserve our POD status
   ~BinData() = default; // preserve our POD status
   void* operator new(std::size_t) = delete; // we only use malloc/free in this library
   void operator delete(void*) = delete; // we only use malloc/free in this library

   GPU_BOTH inline TUInt GetCountSamples() const { return m_cSamples; }
   GPU_BOTH inline void SetCountSamples(const TUInt cSamples) { m_cSamples = cSamples; }

   GPU_BOTH inline TFloat GetWeight() const { return 0; }
   GPU_BOTH inline void SetWeight(const TFloat) {}

   GPU_BOTH inline const GradientPair<TFloat, bHessian>* GetGradientPairs() const {
      return ArrayToPointer(m_aGradientPairs);
   }
   GPU_BOTH inline GradientPair<TFloat, bHessian>* GetGradientPairs() { return ArrayToPointer(m_aGradientPairs); }

 private:
   TUInt m_cSamples;

   // IMPORTANT: m_aGradientPairs must be in the last position for the struct hack and this must be standard layout
   GradientPair<TFloat, bHessian> m_aGradientPairs[cCompilerScores];
};
template<typename TFloat, typename TUInt, bool bHessian, size_t cCompilerScores>
struct BinData<TFloat, TUInt, false, true, bHessian, cCompilerScores> : BinBase {
   friend void ConvertAddBin(const size_t,
         const bool,
         const size_t,
         const bool,
         const bool,
         const bool,
         const bool,
         const void* const,
         const uint64_t* const,
         const double* const,
         const bool,
         const bool,
         void* const);
   template<typename, typename> friend bool IsOverflowBinSize(const bool, const bool, const bool, const size_t);
   template<typename, typename>
   GPU_BOTH friend inline constexpr size_t GetBinSize(const bool, const bool, const bool, const size_t);

   BinData() = default; // preserve our POD status
   ~BinData() = default; // preserve our POD status
   void* operator new(std::size_t) = delete; // we only use malloc/free in this library
   void operator delete(void*) = delete; // we only use malloc/free in this library

   GPU_BOTH inline TUInt GetCountSamples() const { return 0; }
   GPU_BOTH inline void SetCountSamples(const TUInt) {}

   GPU_BOTH inline TFloat GetWeight() const { return m_weight; }
   GPU_BOTH inline void SetWeight(const TFloat weight) { m_weight = weight; }

   GPU_BOTH inline const GradientPair<TFloat, bHessian>* GetGradientPairs() const {
      return ArrayToPointer(m_aGradientPairs);
   }
   GPU_BOTH inline GradientPair<TFloat, bHessian>* GetGradientPairs() { return ArrayToPointer(m_aGradientPairs); }

 private:
   TFloat m_weight;

   // IMPORTANT: m_aGradientPairs must be in the last position for the struct hack and this must be standard layout
   GradientPair<TFloat, bHessian> m_aGradientPairs[cCompilerScores];
};
template<typename TFloat, typename TUInt, bool bHessian, size_t cCompilerScores>
struct BinData<TFloat, TUInt, false, false, bHessian, cCompilerScores> : BinBase {
   friend void ConvertAddBin(const size_t,
         const bool,
         const size_t,
         const bool,
         const bool,
         const bool,
         const bool,
         const void* const,
         const uint64_t* const,
         const double* const,
         const bool,
         const bool,
         void* const);
   template<typename, typename> friend bool IsOverflowBinSize(const bool, const bool, const bool, const size_t);
   template<typename, typename>
   GPU_BOTH friend inline constexpr size_t GetBinSize(const bool, const bool, const bool, const size_t);

   BinData() = default; // preserve our POD status
   ~BinData() = default; // preserve our POD status
   void* operator new(std::size_t) = delete; // we only use malloc/free in this library
   void operator delete(void*) = delete; // we only use malloc/free in this library

   GPU_BOTH inline TUInt GetCountSamples() const { return 0; }
   GPU_BOTH inline void SetCountSamples(const TUInt) {}

   GPU_BOTH inline TFloat GetWeight() const { return 0; }
   GPU_BOTH inline void SetWeight(const TFloat) {}

   GPU_BOTH inline const GradientPair<TFloat, bHessian>* GetGradientPairs() const {
      return ArrayToPointer(m_aGradientPairs);
   }
   GPU_BOTH inline GradientPair<TFloat, bHessian>* GetGradientPairs() { return ArrayToPointer(m_aGradientPairs); }

 private:
   // IMPORTANT: m_aGradientPairs must be in the last position for the struct hack and this must be standard layout
   GradientPair<TFloat, bHessian> m_aGradientPairs[cCompilerScores];
};

template<typename TFloat, typename TUInt, bool bCount, bool bWeight, bool bHessian, size_t cCompilerScores>
struct Bin final : BinData<TFloat, TUInt, bCount, bWeight, bHessian, cCompilerScores> {
   using TGradInternal = GradientPair<TFloat, bHessian>;
   static constexpr ptrdiff_t k_offsetGrad = offsetof(TGradInternal, m_sumGradients);
   using THessInternal = GradientPair<TFloat, true>;
   static constexpr ptrdiff_t k_offsetHess =
         bHessian ? ptrdiff_t{offsetof(THessInternal, m_sumHessians)} : ptrdiff_t{-1};

   static_assert(std::is_floating_point<TFloat>::value, "TFloat must be a float type");
   static_assert(std::is_integral<TUInt>::value, "TUInt must be an integer type");
   static_assert(std::is_unsigned<TUInt>::value, "TUInt must be unsigned");

 public:
   Bin() = default; // preserve our POD status
   ~Bin() = default; // preserve our POD status
   void* operator new(std::size_t) = delete; // we only use malloc/free in this library
   void operator delete(void*) = delete; // we only use malloc/free in this library

   GPU_BOTH inline const Bin<TFloat, TUInt, bCount, bWeight, bHessian, 1>* Downgrade() const {
      return reinterpret_cast<const Bin<TFloat, TUInt, bCount, bWeight, bHessian, 1>*>(this);
   }
   GPU_BOTH inline Bin<TFloat, TUInt, bCount, bWeight, bHessian, 1>* Downgrade() {
      return reinterpret_cast<Bin<TFloat, TUInt, bCount, bWeight, bHessian, 1>*>(this);
   }

   GPU_BOTH inline void Add(const size_t cScores,
         const Bin& other,
         const GradientPair<TFloat, bHessian>* const aOtherGradientPairs,
         GradientPair<TFloat, bHessian>* const aThisGradientPairs) {
#ifndef GPU_COMPILE
      EBM_ASSERT(1 == cCompilerScores || cScores == cCompilerScores);
      EBM_ASSERT(cScores != cCompilerScores || aOtherGradientPairs == other.GetGradientPairs());
      EBM_ASSERT(cScores != cCompilerScores || aThisGradientPairs == this->GetGradientPairs());
      EBM_ASSERT(1 <= cScores);
#endif // GPU_COMPILE

      this->SetCountSamples(this->GetCountSamples() + other.GetCountSamples());
      this->SetWeight(this->GetWeight() + other.GetWeight());

      size_t iScore = 0;
      do {
         aThisGradientPairs[iScore] += aOtherGradientPairs[iScore];
         ++iScore;
      } while(cScores != iScore);
   }
   GPU_BOTH inline void Add(
         const size_t cScores, const Bin& other, const GradientPair<TFloat, bHessian>* const aOtherGradientPairs) {
      Add(cScores, other, aOtherGradientPairs, this->GetGradientPairs());
   }
   GPU_BOTH inline void Add(const size_t cScores, const Bin& other) {
      Add(cScores, other, other.GetGradientPairs(), this->GetGradientPairs());
   }

   GPU_BOTH inline void Subtract(const size_t cScores,
         const Bin& other,
         const GradientPair<TFloat, bHessian>* const aOtherGradientPairs,
         GradientPair<TFloat, bHessian>* const aThisGradientPairs) {
#ifndef GPU_COMPILE
      EBM_ASSERT(1 == cCompilerScores || cScores == cCompilerScores);
      EBM_ASSERT(cScores != cCompilerScores || aOtherGradientPairs == other.GetGradientPairs());
      EBM_ASSERT(cScores != cCompilerScores || aThisGradientPairs == this->GetGradientPairs());
      EBM_ASSERT(1 <= cScores);
#endif // GPU_COMPILE

      this->SetCountSamples(this->GetCountSamples() - other.GetCountSamples());
      this->SetWeight(this->GetWeight() - other.GetWeight());

      size_t iScore = 0;
      do {
         aThisGradientPairs[iScore] -= aOtherGradientPairs[iScore];
         ++iScore;
      } while(cScores != iScore);
   }
   GPU_BOTH inline void Subtract(
         const size_t cScores, const Bin& other, const GradientPair<TFloat, bHessian>* const aOtherGradientPairs) {
      Subtract(cScores, other, aOtherGradientPairs, this->GetGradientPairs());
   }
   GPU_BOTH inline void Subtract(const size_t cScores, const Bin& other) {
      Subtract(cScores, other, other.GetGradientPairs(), this->GetGradientPairs());
   }

   GPU_BOTH inline void Copy(const size_t cScores,
         const Bin& other,
         const GradientPair<TFloat, bHessian>* const aOtherGradientPairs,
         GradientPair<TFloat, bHessian>* const aThisGradientPairs) {
#ifndef GPU_COMPILE
      EBM_ASSERT(1 == cCompilerScores || cScores == cCompilerScores);
      EBM_ASSERT(cScores != cCompilerScores || aOtherGradientPairs == other.GetGradientPairs());
      EBM_ASSERT(cScores != cCompilerScores || aThisGradientPairs == this->GetGradientPairs());
      EBM_ASSERT(1 <= cScores);
#endif // GPU_COMPILE

      this->SetCountSamples(other.GetCountSamples());
      this->SetWeight(other.GetWeight());

      size_t iScore = 0;
      do {
         aThisGradientPairs[iScore] = aOtherGradientPairs[iScore];
         ++iScore;
      } while(cScores != iScore);
   }
   GPU_BOTH inline void Copy(
         const size_t cScores, const Bin& other, const GradientPair<TFloat, bHessian>* const aOtherGradientPairs) {
      Copy(cScores, other, aOtherGradientPairs, this->GetGradientPairs());
   }
   GPU_BOTH inline void Copy(const size_t cScores, const Bin& other) {
      Copy(cScores, other, other.GetGradientPairs(), this->GetGradientPairs());
   }

   GPU_BOTH inline void Zero(const size_t cScores, GradientPair<TFloat, bHessian>* const aThisGradientPairs) {
#ifndef GPU_COMPILE
      EBM_ASSERT(1 == cCompilerScores || cScores == cCompilerScores);
      EBM_ASSERT(cScores != cCompilerScores || aThisGradientPairs == this->GetGradientPairs());
#endif // GPU_COMPILE

      this->SetCountSamples(0);
      this->SetWeight(0);
      ZeroGradientPairs(aThisGradientPairs, cScores);
   }
   GPU_BOTH inline void Zero(const size_t cScores) { Zero(cScores, this->GetGradientPairs()); }

   GPU_BOTH inline void AssertZero(
         const size_t cScores, const GradientPair<TFloat, bHessian>* const aThisGradientPairs) const {
      UNUSED(cScores);
      UNUSED(aThisGradientPairs);
#ifndef GPU_COMPILE
#ifndef NDEBUG
      EBM_ASSERT(1 == cCompilerScores || cScores == cCompilerScores);
      EBM_ASSERT(cScores != cCompilerScores || aThisGradientPairs == this->GetGradientPairs());

      EBM_ASSERT(0 == this->GetCountSamples());
      EBM_ASSERT(0 == this->GetWeight());

      EBM_ASSERT(1 <= cScores);
      size_t iScore = 0;
      do {
         aThisGradientPairs[iScore].AssertZero();
         ++iScore;
      } while(cScores != iScore);
#endif // NDEBUG
#endif // GPU_COMPILE
   }
   GPU_BOTH inline void AssertZero(const size_t cScores) const { AssertZero(cScores, this->GetGradientPairs()); }
};
static_assert(std::is_standard_layout<Bin<float, uint32_t, true, true, true>>::value,
      "We use the struct hack in several places, so disallow non-standard_layout types in general");
static_assert(std::is_trivial<Bin<float, uint32_t, true, true, true>>::value,
      "We use memcpy in several places, so disallow non-trivial types in general");

static_assert(std::is_standard_layout<Bin<double, uint64_t, false, false, false>>::value,
      "We use the struct hack in several places, so disallow non-standard_layout types in general");
static_assert(std::is_trivial<Bin<double, uint64_t, false, false, false>>::value,
      "We use memcpy in several places, so disallow non-trivial types in general");

template<typename TFloat, typename TUInt>
inline static bool IsOverflowBinSize(const bool bCount, const bool bWeight, const bool bHessian, const size_t cScores) {
   const size_t cBytesPerGradientPair = GetGradientPairSize<TFloat>(bHessian);

   if(UNLIKELY(IsMultiplyError(cBytesPerGradientPair, cScores))) {
      return true;
   }

   size_t cBytesBinComponent;

   if(bCount) {
      if(bWeight) {
         if(bHessian) {
            typedef Bin<TFloat, TUInt, true, true, true> OffsetType;
            cBytesBinComponent = offsetof(OffsetType, m_aGradientPairs);
         } else {
            typedef Bin<TFloat, TUInt, true, true, false> OffsetType;
            cBytesBinComponent = offsetof(OffsetType, m_aGradientPairs);
         }
      } else {
         if(bHessian) {
            typedef Bin<TFloat, TUInt, true, false, true> OffsetType;
            cBytesBinComponent = offsetof(OffsetType, m_aGradientPairs);
         } else {
            typedef Bin<TFloat, TUInt, true, false, false> OffsetType;
            cBytesBinComponent = offsetof(OffsetType, m_aGradientPairs);
         }
      }
   } else {
      if(bWeight) {
         if(bHessian) {
            typedef Bin<TFloat, TUInt, false, true, true> OffsetType;
            cBytesBinComponent = offsetof(OffsetType, m_aGradientPairs);
         } else {
            typedef Bin<TFloat, TUInt, false, true, false> OffsetType;
            cBytesBinComponent = offsetof(OffsetType, m_aGradientPairs);
         }
      } else {
         if(bHessian) {
            typedef Bin<TFloat, TUInt, false, false, true> OffsetType;
            cBytesBinComponent = offsetof(OffsetType, m_aGradientPairs);
         } else {
            typedef Bin<TFloat, TUInt, false, false, false> OffsetType;
            cBytesBinComponent = offsetof(OffsetType, m_aGradientPairs);
         }
      }
   }

   if(UNLIKELY(IsAddError(cBytesBinComponent, cBytesPerGradientPair * cScores))) {
      return true;
   }

   return false;
}

template<typename TFloat, typename TUInt>
GPU_BOTH inline constexpr static size_t GetBinSize(
      const bool bCount, const bool bWeight, const bool bHessian, const size_t cScores) {
   typedef Bin<TFloat, TUInt, true, true, true> OffsetTypeHttt;
   typedef Bin<TFloat, TUInt, true, true, false> OffsetTypeHttf;
   typedef Bin<TFloat, TUInt, true, false, true> OffsetTypeHtft;
   typedef Bin<TFloat, TUInt, true, false, false> OffsetTypeHtff;
   typedef Bin<TFloat, TUInt, false, true, true> OffsetTypeHftt;
   typedef Bin<TFloat, TUInt, false, true, false> OffsetTypeHftf;
   typedef Bin<TFloat, TUInt, false, false, true> OffsetTypeHfft;
   typedef Bin<TFloat, TUInt, false, false, false> OffsetTypeHfff;

   // TODO: someday try out bin sizes that are a power of two.  This would allow us to use a shift when using bins
   //       instead of using multiplications.  In that version return the number of bits to shift here to make it easy
   //       to get either the shift required for indexing OR the number of bytes (shift 1 << num_bits)

   return (bCount ? bWeight ?
                    bHessian ? offsetof(OffsetTypeHttt, m_aGradientPairs) : offsetof(OffsetTypeHttf, m_aGradientPairs) :
                            bHessian ? offsetof(OffsetTypeHtft, m_aGradientPairs) :
                                       offsetof(OffsetTypeHtff, m_aGradientPairs) :
                      bWeight ?
                    bHessian ? offsetof(OffsetTypeHftt, m_aGradientPairs) : offsetof(OffsetTypeHftf, m_aGradientPairs) :
                      bHessian ? offsetof(OffsetTypeHfft, m_aGradientPairs) :
                                 offsetof(OffsetTypeHfff, m_aGradientPairs)) +
         GetGradientPairSize<TFloat>(bHessian) * cScores;
}

template<typename TFloat, typename TUInt, bool bCount, bool bWeight, bool bHessian, size_t cCompilerScores>
GPU_BOTH inline static Bin<TFloat, TUInt, bCount, bWeight, bHessian, cCompilerScores>* IndexBin(
      Bin<TFloat, TUInt, bCount, bWeight, bHessian, cCompilerScores>* const aBins, const size_t iByte) {
   return IndexByte(aBins, iByte);
}

template<typename TFloat, typename TUInt, bool bCount, bool bWeight, bool bHessian, size_t cCompilerScores>
GPU_BOTH inline static const Bin<TFloat, TUInt, bCount, bWeight, bHessian, cCompilerScores>* IndexBin(
      const Bin<TFloat, TUInt, bCount, bWeight, bHessian, cCompilerScores>* const aBins, const size_t iByte) {
   return IndexByte(aBins, iByte);
}

GPU_BOTH inline static BinBase* IndexBin(BinBase* const aBins, const size_t iByte) { return IndexByte(aBins, iByte); }

GPU_BOTH inline static const BinBase* IndexBin(const BinBase* const aBins, const size_t iByte) {
   return IndexByte(aBins, iByte);
}

template<typename TFloat, typename TUInt, bool bCount, bool bWeight, bool bHessian, size_t cCompilerScores>
GPU_BOTH inline static const Bin<TFloat, TUInt, bCount, bWeight, bHessian, cCompilerScores>* NegativeIndexBin(
      const Bin<TFloat, TUInt, bCount, bWeight, bHessian, cCompilerScores>* const aBins, const size_t iByte) {
   return NegativeIndexByte(aBins, iByte);
}

template<typename TFloat, typename TUInt, bool bCount, bool bWeight, bool bHessian, size_t cCompilerScores>
GPU_BOTH inline static Bin<TFloat, TUInt, bCount, bWeight, bHessian, cCompilerScores>* NegativeIndexBin(
      Bin<TFloat, TUInt, bCount, bWeight, bHessian, cCompilerScores>* const aBins, const size_t iByte) {
   return NegativeIndexByte(aBins, iByte);
}

template<typename TFloat, typename TUInt, bool bCount, bool bWeight, bool bHessian, size_t cCompilerScores>
inline static size_t CountBins(const Bin<TFloat, TUInt, bCount, bWeight, bHessian, cCompilerScores>* const pBinHigh,
      const Bin<TFloat, TUInt, bCount, bWeight, bHessian, cCompilerScores>* const pBinLow,
      const size_t cBytesPerBin) {
   const size_t cBytesDiff = CountBytes(pBinHigh, pBinLow);
#ifndef GPU_COMPILE
   EBM_ASSERT(0 == cBytesDiff % cBytesPerBin);
#endif // GPU_COMPILE
   return cBytesDiff / cBytesPerBin;
}

// keep this as a MACRO so that we don't materialize any of the parameters on non-debug builds
#define ASSERT_BIN_OK(MACRO_cBytesPerBin, MACRO_pBin, MACRO_pBinsEnd)                                                  \
   (EBM_ASSERT(reinterpret_cast<const BinBase*>(reinterpret_cast<const char*>(MACRO_pBin) +                            \
                     static_cast<size_t>(MACRO_cBytesPerBin)) <= (MACRO_pBinsEnd)))

} // namespace DEFINED_ZONE_NAME

#endif // BIN_HPP
