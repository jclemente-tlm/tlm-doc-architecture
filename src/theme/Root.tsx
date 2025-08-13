import React, { useEffect } from 'react';
import lightGallery from 'lightgallery';

// Plugins
import lgZoom from 'lightgallery/plugins/zoom';
import lgFullscreen from 'lightgallery/plugins/fullscreen';

// Estilos CSS
import 'lightgallery/css/lightgallery.css';
import 'lightgallery/css/lg-zoom.css';
import 'lightgallery/css/lg-fullscreen.css';

import { useLocation } from '@docusaurus/router';

export default function Root({ children }) {
  const location = useLocation();

  useEffect(() => {
    const timeout = setTimeout(() => {
      const markdownContainer = document.querySelector('.markdown');

      if (markdownContainer) {
        // Envolver imágenes en enlaces para que LightGallery las detecte
        const imgs = markdownContainer.querySelectorAll('img');
        imgs.forEach((img) => {
          if (!img.closest('a')) {
            const link = document.createElement('a');
            link.href = img.src;
            img.parentNode?.insertBefore(link, img);
            link.appendChild(img);
          }
        });

        // Inicializar LightGallery
        lightGallery(markdownContainer as HTMLElement, {
          selector:
            'a[href$=".png"], a[href$=".jpg"], a[href$=".jpeg"], a[href$=".gif"], a[href$=".webp"]',
          plugins: [lgZoom, lgFullscreen],
          speed: 300,
          download: true, // activa botón de descarga
        });
      }
    }, 300);

    return () => clearTimeout(timeout);
  }, [location.pathname]);

  return <>{children}</>;
}
