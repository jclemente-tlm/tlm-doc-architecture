import {themes as prismThemes} from 'prism-react-renderer';
import type {Config} from '@docusaurus/types';
import type * as Preset from '@docusaurus/preset-classic';

// This runs in Node.js - Don't use client-side code here (browser APIs, JSX...)

const config: Config = {
  title: 'Talma',
  tagline: 'Documentación de Talma',
  favicon: 'img/favicon.ico',

  future: {
    v4: true,
  },

  url: 'https://jclemente-tlm.github.io',
  baseUrl: '/tlm-doc-architecture/',
  organizationName: 'jclemente-tlm',
  projectName: 'tlm-doc-architecture',
  deploymentBranch: 'docs',
  trailingSlash: false,

  onBrokenLinks: 'throw',
  onBrokenMarkdownLinks: 'warn',

  i18n: {
    defaultLocale: 'es',
    locales: ['es'],
  },

  presets: [
    [
      'classic',
      {
        docs: {
          sidebarPath: require.resolve('./sidebars.ts'), // <- aquí se resuelve correctamente TS
          editUrl:
            'https://github.com/jclemente-tlm/tlm-doc-architecture/edit/main/',
        },
        blog: {
          showReadingTime: true,
          feedOptions: { type: ['rss', 'atom'], xslt: true },
          editUrl:
            'https://github.com/jclemente-tlm/tlm-doc-architecture/edit/main/',
          onInlineTags: 'warn',
          onInlineAuthors: 'warn',
          onUntruncatedBlogPosts: 'warn',
        },
        theme: { customCss: './src/css/custom.css' },
      } satisfies Preset.Options,
    ],
  ],

  themeConfig: {
    image: 'img/docusaurus-social-card.jpg',
    navbar: {
      logo: { alt: 'Talma Logo', src: 'img/logo-talma.png' },
      items: [
        {
          type: 'docSidebar',
          sidebarId: 'tutorialSidebar',
          position: 'left',
          label: 'Documentación',
        },
        {
          href: 'https://github.com/jclemente-tlm/tlm-doc-architecture',
          position: 'right',
          className: 'header--github-link',
          'aria-label': 'GitHub repository',
        },
      ],
    },
    docs: {
      sidebar: {
        autoCollapseCategories: true,
      },
    },
    footer: {
      style: 'dark',
      links: [
        {
          title: 'Docs',
          items: [{ label: 'Documentación', to: '/docs/intro' }],
        },
        {
          title: 'Comunidad',
          items: [
            { label: 'LinkedIn', href: 'https://pe.linkedin.com/company/talma-servicios-aeroportuarios' },
            { label: 'YouTube', href: 'https://www.youtube.com/channel/UC-LkTBWGU2aSh-00bv83OlA' },
            { label: 'Facebook', href: 'https://www.facebook.com/talmaperu/?ref=br_rs' },
          ],
        },
        {
          title: 'Más',
          items: [{ label: 'GitHub', href: 'https://github.com/jclemente-tlm/tlm-doc-architecture' }],
        },
      ],
      copyright: `Copyright © ${new Date().getFullYear()} Talma. Documentación construida con Docusaurus.`,
    },
    prism: {
      // theme: prismThemes.github,
      // darkTheme: prismThemes.dracula,
      theme: prismThemes.vsLight,   // tema para modo claro
      darkTheme: prismThemes.vsDark, // tema para modo oscuro
      additionalLanguages: [
        'java','csharp','php','ruby','go','rust','kotlin','swift','sql','powershell',
        'docker','yaml','json','bash','ini','perl','scala','groovy','graphql','typescript','python','markdown',
      ],
    },
    mermaid: {
      theme: { light: 'neutral', dark: 'dark' },
      options: { securityLevel: 'strict' },
    },
  } satisfies Preset.ThemeConfig,
  themes: ['@docusaurus/theme-mermaid'],
  markdown: { mermaid: true },
};

export default config;
