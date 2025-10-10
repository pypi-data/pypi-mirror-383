import {themes as prismThemes} from 'prism-react-renderer';
import type {Config} from '@docusaurus/types';
import type * as Preset from '@docusaurus/preset-classic';

// This runs in Node.js - Don't use client-side code here (browser APIs, JSX...)

const config: Config = {
  title: 'mem8',
  tagline: 'Context Management for AI Development',
  favicon: 'img/favicon.ico',

  // Future flags, see https://docusaurus.io/docs/api/docusaurus-config#future
  future: {
    v4: true, // Improve compatibility with the upcoming Docusaurus v4
  },

  // Set the production url of your site here
  url: 'https://codebasecontext.org',

  // Note: Workflow titles updated to reflect current m8-* command names
  // Set the /<baseUrl>/ pathname under which your site is served
  baseUrl: '/',

  // Cloudflare Pages deployment
  organizationName: 'killerapp',
  projectName: 'mem8',

  onBrokenLinks: 'throw',

  // Even if you don't use internationalization, you can use this field to set
  // useful metadata like html lang. For example, if your site is Chinese, you
  // may want to replace "en" with "zh-Hans".
  i18n: {
    defaultLocale: 'en',
    locales: ['en'],
  },

  presets: [
    [
      'classic',
      {
        docs: {
          sidebarPath: './sidebars.ts',
          // Please change this to your repo.
          // Remove this to remove the "edit this page" links.
          editUrl:
            'https://github.com/killerapp/mem8/tree/main/documentation/',
        },
        blog: false, // Disable blog for now
        theme: {
          customCss: './src/css/custom.css',
        },
      } satisfies Preset.Options,
    ],
  ],

  plugins: [
    'docusaurus-plugin-llms-txt',
  ],

  themes: [
    '@docusaurus/theme-mermaid',
    '@docusaurus/theme-live-codeblock',
  ],

  markdown: {
    mermaid: true,
  },

  themeConfig: {
    // Social card for sharing
    image: 'img/mem8-social-card.jpg',
    colorMode: {
      defaultMode: 'dark',
      disableSwitch: false,
      respectPrefersColorScheme: false,
    },
    mermaid: {
      theme: {light: 'neutral', dark: 'dark'},
    },
    navbar: {
      logo: {
        alt: 'mem8 Logo',
        src: 'img/logo-navbar.png',
        width: 52,
        height: 48,
      },
      items: [
        {
          type: 'docSidebar',
          sidebarId: 'tutorialSidebar',
          position: 'left',
          label: 'Docs',
        },
        {
          type: 'dropdown',
          label: 'Codebase Context',
          position: 'left',
          items: [
            {
              label: 'Specification (Archived)',
              href: 'https://github.com/killerapp/codebase-context-spec',
            },
            {
              label: 'YouTube Videos',
              href: 'https://www.youtube.com/watch?v=6icquh4thCw',
            },
            {
              label: 'Agentic Insights',
              href: 'https://agenticinsights.substack.com',
            },
          ],
        },
        {
          href: 'https://github.com/killerapp/mem8',
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
              label: 'Getting Started',
              to: '/docs/intro',
            },
            {
              label: 'External Templates',
              to: '/docs/external-templates',
            },
          ],
        },
        {
          title: 'Resources',
          items: [
            {
              label: 'GitHub',
              href: 'https://github.com/killerapp/mem8',
            },
            {
              label: 'Template Repository',
              href: 'https://github.com/killerapp/mem8-templates',
            },
          ],
        },
      ],
      copyright: `Codebase Context - Tools and techniques for managing AI context windows and development workflows`,
    },
    prism: {
      theme: prismThemes.github,
      darkTheme: prismThemes.dracula,
    },
  } satisfies Preset.ThemeConfig,
};

export default config;
