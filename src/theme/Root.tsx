import React, { useEffect, useRef } from 'react';
import { Fancybox } from '@fancyapps/ui';
import '@fancyapps/ui/dist/fancybox/fancybox.css';
import { useLocation } from '@docusaurus/router';

const IMG_EXT = /\.(png|jpe?g|gif|webp|avif|svg)(\?.*)?$/i;

function enhanceImages(container: HTMLElement) {
  const imgs = Array.from(container.querySelectorAll<HTMLImageElement>('img'));

  imgs.forEach((img) => {
    if (img.closest('[data-fancybox="gallery"]')) return;

    const src = img.currentSrc || img.src;
    if (!src || !IMG_EXT.test(src)) return;

    const filename = decodeURIComponent(src.split('/').pop() || 'image');

    const existingLink = img.closest('a') as HTMLAnchorElement | null;
    if (existingLink && IMG_EXT.test(existingLink.href)) {
      existingLink.setAttribute('data-fancybox', 'gallery');
      existingLink.setAttribute('download', filename);
      existingLink.classList.add('fz-wrap');
      return;
    }

    const a = document.createElement('a');
    a.href = src;
    a.setAttribute('data-fancybox', 'gallery');
    a.setAttribute('download', filename);
    a.classList.add('fz-wrap');

    img.parentNode?.insertBefore(a, img);
    a.appendChild(img);
  });
}

export default function Root({ children }: { children: React.ReactNode }) {
  const location = useLocation();
  const observerRef = useRef<MutationObserver | null>(null);
  const containerRef = useRef<HTMLElement | null>(null);

  useEffect(() => {
    const root = document.getElementById('__docusaurus');
    if (!root) return;

    const applyZoom = () => {
      const container = document.querySelector<HTMLElement>('.markdown');
      if (!container) return;

      enhanceImages(container);

      if (containerRef.current) {
        Fancybox.unbind(containerRef.current);
        Fancybox.close(true);
      }
      Fancybox.bind(container, '[data-fancybox="gallery"]');
      containerRef.current = container;
    };

    applyZoom();

    observerRef.current?.disconnect();
    observerRef.current = new MutationObserver(() => {
      applyZoom();
    });
    observerRef.current.observe(root, { childList: true, subtree: true });

    return () => {
      observerRef.current?.disconnect();
      if (containerRef.current) {
        Fancybox.unbind(containerRef.current);
        Fancybox.close(true);
      }
    };
  }, [location.pathname]);

  return (
    <>
      <style>{`
        .fz-wrap { display: inline-block; line-height: 0; }
        .fz-wrap img { display: block; max-width: 100%; cursor: zoom-in; }
      `}</style>
      {children}
    </>
  );
}
