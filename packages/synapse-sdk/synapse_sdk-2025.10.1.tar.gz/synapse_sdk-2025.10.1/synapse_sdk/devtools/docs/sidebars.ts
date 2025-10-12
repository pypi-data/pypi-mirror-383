import type {SidebarsConfig} from '@docusaurus/plugin-content-docs';

// This runs in Node.js - Don't use client-side code here (browser APIs, JSX...)

/**
 * Creating a sidebar enables you to:
 - create an ordered group of docs
 - render a sidebar for each doc of that group
 - provide next/previous navigation

 The sidebars can be generated from the filesystem, or explicitly defined here.

 Create as many sidebars as you want.
 */
const sidebars: SidebarsConfig = {
  tutorialSidebar: [
    'introduction',
    'installation', 
    'quickstart',
    {
      type: 'category',
      label: 'Features',
      items: [
        'features/features',
        'features/converters/converters',
      ],
    },
    {
      type: 'category',
      label: 'Utilities',
      items: [
        'features/utils/file',
        'features/utils/network',
        'features/utils/storage',
        'features/utils/types',
      ],
    },
    {
      type: 'category',
      label: 'Plugin System',
      items: [
        'plugins/plugins',
        'plugins/export-plugins',
        'plugins/upload-plugins',
      ],
    },
    {
      type: 'category',
      label: 'API Reference',
      items: [
        'api/index',
        {
          type: 'category',
          label: 'Clients',
          items: [
            'api/clients/index',
            'api/clients/backend',
            'api/clients/annotation-mixin',
            'api/clients/core-mixin',
            'api/clients/data-collection-mixin',
            'api/clients/hitl-mixin',
            'api/clients/integration-mixin',
            'api/clients/ml-mixin',
            'api/clients/agent',
            'api/clients/ray',
            'api/clients/base',
          ],
        },
        {
          type: 'category',
          label: 'Plugins',
          items: [
            'api/plugins/models',
          ],
        },
      ],
    },
    'configuration',
    'troubleshooting',
    'faq',
    'contributing',
  ],
};

export default sidebars;
