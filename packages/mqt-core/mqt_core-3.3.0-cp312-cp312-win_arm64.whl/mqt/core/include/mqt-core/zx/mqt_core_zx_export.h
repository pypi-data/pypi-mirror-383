
#ifndef MQT_CORE_ZX_EXPORT_H
#define MQT_CORE_ZX_EXPORT_H

#ifdef MQT_CORE_ZX_STATIC_DEFINE
#  define MQT_CORE_ZX_EXPORT
#  define MQT_CORE_ZX_NO_EXPORT
#else
#  ifndef MQT_CORE_ZX_EXPORT
#    ifdef mqt_core_zx_EXPORTS
        /* We are building this library */
#      define MQT_CORE_ZX_EXPORT __declspec(dllexport)
#    else
        /* We are using this library */
#      define MQT_CORE_ZX_EXPORT __declspec(dllimport)
#    endif
#  endif

#  ifndef MQT_CORE_ZX_NO_EXPORT
#    define MQT_CORE_ZX_NO_EXPORT 
#  endif
#endif

#ifndef MQT_CORE_ZX_DEPRECATED
#  define MQT_CORE_ZX_DEPRECATED __declspec(deprecated)
#endif

#ifndef MQT_CORE_ZX_DEPRECATED_EXPORT
#  define MQT_CORE_ZX_DEPRECATED_EXPORT MQT_CORE_ZX_EXPORT MQT_CORE_ZX_DEPRECATED
#endif

#ifndef MQT_CORE_ZX_DEPRECATED_NO_EXPORT
#  define MQT_CORE_ZX_DEPRECATED_NO_EXPORT MQT_CORE_ZX_NO_EXPORT MQT_CORE_ZX_DEPRECATED
#endif

/* NOLINTNEXTLINE(readability-avoid-unconditional-preprocessor-if) */
#if 0 /* DEFINE_NO_DEPRECATED */
#  ifndef MQT_CORE_ZX_NO_DEPRECATED
#    define MQT_CORE_ZX_NO_DEPRECATED
#  endif
#endif

#endif /* MQT_CORE_ZX_EXPORT_H */
