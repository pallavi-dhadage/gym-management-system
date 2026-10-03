/**
 * Performance Optimization Utilities for SetFit Gym
 * Lazy loading, image optimization, caching, and monitoring
 */

// ============================================================
// 1. LAZY LOADING
// ============================================================

/**
 * Lazy load background images using Intersection Observer
 */
function lazyLoadBackgrounds() {
  const bgElements = document.querySelectorAll('[data-bg]');
  
  if ('IntersectionObserver' in window) {
    const bgObserver = new IntersectionObserver((entries, observer) => {
      entries.forEach(entry => {
        if (entry.isIntersecting) {
          const elem = entry.target;
          const bgUrl = elem.dataset.bg;
          
          // Preload image
          const img = new Image();
          img.onload = () => {
            elem.style.backgroundImage = `url('${bgUrl}')`;
            elem.classList.add('loaded');
          };
          img.src = bgUrl;
          
          observer.unobserve(elem);
        }
      });
    }, {
      rootMargin: '50px' // Start loading 50px before element enters viewport
    });
    
    bgElements.forEach(elem => bgObserver.observe(elem));
  } else {
    // Fallback for older browsers
    bgElements.forEach(elem => {
      elem.style.backgroundImage = `url('${elem.dataset.bg}')`;
    });
  }
}

/**
 * Lazy load regular images with native loading="lazy"
 */
function lazyLoadImages() {
  const images = document.querySelectorAll('img[data-src]');
  
  if ('loading' in HTMLImageElement.prototype) {
    // Native lazy loading supported
    images.forEach(img => {
      img.src = img.dataset.src;
      if (img.dataset.srcset) {
        img.srcset = img.dataset.srcset;
      }
    });
  } else {
    // Use Intersection Observer for older browsers
    const imgObserver = new IntersectionObserver((entries, observer) => {
      entries.forEach(entry => {
        if (entry.isIntersecting) {
          const img = entry.target;
          img.src = img.dataset.src;
          if (img.dataset.srcset) {
            img.srcset = img.dataset.srcset;
          }
          img.classList.add('loaded');
          observer.unobserve(img);
        }
      });
    });
    
    images.forEach(img => imgObserver.observe(img));
  }
}

// ============================================================
// 2. RESOURCE HINTS & PRELOADING
// ============================================================

/**
 * Preload critical resources
 */
function preloadCriticalResources() {
  const criticalResources = [
    { href: '/static/css/style.css', as: 'style' },
    { href: '/static/js/app.js', as: 'script' },
  ];
  
  criticalResources.forEach(resource => {
    const link = document.createElement('link');
    link.rel = 'preload';
    link.href = resource.href;
    link.as = resource.as;
    document.head.appendChild(link);
  });
}

// ============================================================
// 3. CACHING STRATEGIES
// ============================================================

/**
 * LocalStorage cache with expiry
 */
const CacheManager = {
  set(key, value, ttlMinutes = 60) {
    const item = {
      value: value,
      expiry: Date.now() + (ttlMinutes * 60 * 1000)
    };
    try {
      localStorage.setItem(`setfit_${key}`, JSON.stringify(item));
    } catch (e) {
      console.warn('LocalStorage full or unavailable:', e);
    }
  },
  
  get(key) {
    try {
      const itemStr = localStorage.getItem(`setfit_${key}`);
      if (!itemStr) return null;
      
      const item = JSON.parse(itemStr);
      if (Date.now() > item.expiry) {
        localStorage.removeItem(`setfit_${key}`);
        return null;
      }
      return item.value;
    } catch (e) {
      return null;
    }
  },
  
  remove(key) {
    localStorage.removeItem(`setfit_${key}`);
  },
  
  clear() {
    Object.keys(localStorage)
      .filter(key => key.startsWith('setfit_'))
      .forEach(key => localStorage.removeItem(key));
  }
};

// ============================================================
// 4. DEBOUNCE & THROTTLE
// ============================================================

/**
 * Debounce function calls
 */
function debounce(func, wait = 300) {
  let timeout;
  return function executedFunction(...args) {
    const later = () => {
      clearTimeout(timeout);
      func(...args);
    };
    clearTimeout(timeout);
    timeout = setTimeout(later, wait);
  };
}

/**
 * Throttle function calls
 */
function throttle(func, limit = 300) {
  let inThrottle;
  return function(...args) {
    if (!inThrottle) {
      func.apply(this, args);
      inThrottle = true;
      setTimeout(() => inThrottle = false, limit);
    }
  };
}

// ============================================================
// 5. PERFORMANCE MONITORING
// ============================================================

/**
 * Monitor Core Web Vitals
 */
const PerformanceMonitor = {
  // Largest Contentful Paint
  measureLCP() {
    if ('PerformanceObserver' in window) {
      try {
        const observer = new PerformanceObserver((list) => {
          const entries = list.getEntries();
          const lastEntry = entries[entries.length - 1];
          console.log('LCP:', lastEntry.renderTime || lastEntry.loadTime);
        });
        observer.observe({ entryTypes: ['largest-contentful-paint'] });
      } catch (e) {
        // Ignore if not supported
      }
    }
  },
  
  // First Input Delay
  measureFID() {
    if ('PerformanceObserver' in window) {
      try {
        const observer = new PerformanceObserver((list) => {
          const entries = list.getEntries();
          entries.forEach(entry => {
            console.log('FID:', entry.processingStart - entry.startTime);
          });
        });
        observer.observe({ entryTypes: ['first-input'] });
      } catch (e) {
        // Ignore if not supported
      }
    }
  },
  
  // Cumulative Layout Shift
  measureCLS() {
    if ('PerformanceObserver' in window) {
      try {
        let clsValue = 0;
        const observer = new PerformanceObserver((list) => {
          list.getEntries().forEach(entry => {
            if (!entry.hadRecentInput) {
              clsValue += entry.value;
              console.log('CLS:', clsValue);
            }
          });
        });
        observer.observe({ entryTypes: ['layout-shift'] });
      } catch (e) {
        // Ignore if not supported
      }
    }
  },
  
  // Page Load Time
  measurePageLoad() {
    if (window.performance && window.performance.timing) {
      window.addEventListener('load', () => {
        setTimeout(() => {
          const perfData = window.performance.timing;
          const pageLoadTime = perfData.loadEventEnd - perfData.navigationStart;
          console.log('Page Load Time:', pageLoadTime + 'ms');
        }, 0);
      });
    }
  },
  
  // Initialize all monitoring
  init() {
    this.measureLCP();
    this.measureFID();
    this.measureCLS();
    this.measurePageLoad();
  }
};

// ============================================================
// 6. IMAGE OPTIMIZATION HELPERS
// ============================================================

/**
 * Generate responsive image srcset
 */
function generateSrcset(baseUrl, widths = [640, 768, 1024, 1280, 1920]) {
  return widths.map(w => `${baseUrl}?w=${w} ${w}w`).join(', ');
}

/**
 * Detect WebP support
 */
function supportsWebP() {
  const elem = document.createElement('canvas');
  if (elem.getContext && elem.getContext('2d')) {
    return elem.toDataURL('image/webp').indexOf('data:image/webp') === 0;
  }
  return false;
}

// ============================================================
// 7. NETWORK DETECTION
// ============================================================

/**
 * Detect slow network connection
 */
function isSlowConnection() {
  if ('connection' in navigator) {
    const conn = navigator.connection || navigator.mozConnection || navigator.webkitConnection;
    // Slow if 2G or slow-2g or saveData enabled
    return conn.effectiveType === 'slow-2g' || 
           conn.effectiveType === '2g' || 
           conn.saveData === true;
  }
  return false;
}

/**
 * Adjust quality based on connection
 */
function getOptimalImageQuality() {
  if (isSlowConnection()) {
    return 60; // Lower quality for slow connections
  }
  return 80; // Normal quality
}

// ============================================================
// 8. INITIALIZATION
// ============================================================

/**
 * Initialize all performance optimizations
 */
function initPerformanceOptimizations() {
  // Lazy load images and backgrounds
  lazyLoadBackgrounds();
  lazyLoadImages();
  
  // Start performance monitoring in development
  if (window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1') {
    PerformanceMonitor.init();
  }
  
  // Add connection quality indicator
  if (isSlowConnection()) {
    console.log('Slow connection detected - optimizing resources');
    document.body.classList.add('slow-connection');
  }
  
  // Check WebP support
  if (supportsWebP()) {
    document.documentElement.classList.add('webp');
  } else {
    document.documentElement.classList.add('no-webp');
  }
}

// Run on DOM ready
if (document.readyState === 'loading') {
  document.addEventListener('DOMContentLoaded', initPerformanceOptimizations);
} else {
  initPerformanceOptimizations();
}

// ============================================================
// 9. EXPORT FOR EXTERNAL USE
// ============================================================

window.SetFitPerf = {
  CacheManager,
  debounce,
  throttle,
  lazyLoadBackgrounds,
  lazyLoadImages,
  isSlowConnection,
  getOptimalImageQuality,
  supportsWebP
};
