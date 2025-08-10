import {themes as prismThemes} from 'prism-react-renderer';
import type {Config} from '@docusaurus/types';
import type * as Preset from '@docusaurus/preset-classic';

// This runs in Node.js - Don't use client-side code here (browser APIs, JSX...)

const config: Config = {
  title: 'Talma',
  tagline: 'Documentación de Talma',
  favicon: 'img/favicon.ico',

  // Future flags, see https://docusaurus.io/docs/api/docusaurus-config#future
  future: {
    v4: true, // Improve compatibility with the upcoming Docusaurus v4
  },

  // Set the production url of your site here
  url: 'https://jclemente-tlm.github.io',
  // Set the /<baseUrl>/ pathname under which your site is served
  // For GitHub pages deployment, it is often '/<projectName>/'
  baseUrl: '/',

  // GitHub pages deployment config.
  // If you aren't using GitHub pages, you don't need these.
  organizationName: 'jclemente-tlm', // Nombre de la empresa
  projectName: 'tlm-doc-architecture', // El nombre de tu repositorio
  deploymentBranch: 'docs', // La rama donde se despliega la documentación
  repoUrl: 'git@work.github.com:jclemente-tlm/tlm-doc-architecture.git',
  trailingSlash: false,

  onBrokenLinks: 'throw',
  onBrokenMarkdownLinks: 'warn',

  // Configuración de internacionalización
  i18n: {
    defaultLocale: 'es',
    locales: ['es'],
  },

  presets: [
    [
      'classic',
      {
        docs: {
          sidebarPath: './sidebars.ts',
          // Cambiado para tu repo.
          editUrl:
            'https://github.com/jclemente-tlm/tlm-doc-architecture/edit/main/',
        },
        blog: {
          showReadingTime: true,
          feedOptions: {
            type: ['rss', 'atom'],
            xslt: true,
          },
          // Cambiado para tu repo.
          editUrl:
            'https://github.com/jclemente-tlm/tlm-doc-architecture/edit/main/',
          // Useful options to enforce blogging best practices
          onInlineTags: 'warn',
          onInlineAuthors: 'warn',
          onUntruncatedBlogPosts: 'warn',
        },
        theme: {
          customCss: './src/css/custom.css',
        },
      } satisfies Preset.Options,
    ],
  ],

  themeConfig: {
    // Replace with your project's social card
    image: 'img/docusaurus-social-card.jpg',
    navbar: {
      // title: 'Talma',
      logo: {
        alt: 'Talma Logo',
        src: 'img/logo-talma.png',
      },
      items: [
        {
          type: 'docSidebar',
          sidebarId: 'tutorialSidebar',
          position: 'left',
          label: 'Documentación',
        },
        // {to: '/blog', label: 'Blog', position: 'left'},
        {
          href: 'https://github.com/facebook/docusaurus',
          label: 'GitHub',
          position: 'right',
        },
      ],
    },
    footer: {
      style: 'dark',
      links: [
        {
          title: 'Docs',
          items: [
            {
              label: 'Documentación',
              to: '/docs/intro',
            },
          ],
        },
        {
          title: 'Comunidad',
          items: [
            {
              label: 'LinkedIn',
              href: 'https://pe.linkedin.com/company/talma-servicios-aeroportuarios',
            },
            {
              label: 'YouTube',
              href: 'https://www.youtube.com/channel/UC-LkTBWGU2aSh-00bv83OlA',
            },
            {
              label: 'Facebook',
              href: 'https://www.facebook.com/talmaperu/?ref=br_rs',
            },
          ],
        },
        {
          title: 'Más',
          items: [
            // {
            //   label: 'Blog',
            //   to: '/blog',
            // },
            {
              label: 'GitHub',
              href: 'https://github.com/jclemente-tlm/tlm-doc-architecture',
            },
          ],
        },
      ],
      copyright: `Copyright © ${new Date().getFullYear()} Talma. Documentación construida con Docusaurus.`,
    },
    prism: {
      theme: prismThemes.github,
      darkTheme: prismThemes.dracula,
      additionalLanguages: [
        'java',
        'csharp',
        'php',
        'ruby',
        'go',
        'rust',
        'kotlin',
        'swift',
        'sql',
        'powershell',
        'docker',
        'yaml',
        'json',
        'bash',
        'ini',
        'perl',
        'scala',
        'groovy',
        'graphql',
        'typescript',
        'python',
        'markdown',
      ],
    },
    mermaid: {
      theme: {light: 'neutral', dark: 'dark'},
      options: {
        securityLevel: 'strict',
      },
    },
  } satisfies Preset.ThemeConfig,
  themes: [
    '@docusaurus/theme-mermaid',
  ],
  markdown: {
    mermaid: true,
  },
};

export default config;
