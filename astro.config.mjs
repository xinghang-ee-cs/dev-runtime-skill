import { defineConfig } from 'astro/config';
import starlight from '@astrojs/starlight';

export default defineConfig({
  site: 'https://xinghang-ee-cs.github.io',
  base: '/dev-runtime-skill',
  integrations: [
    starlight({
      title: 'Runtime Skills 教程',
      description: '面向 Codex 的规划、开发、测试与代码检查 Skill 教程。',
      favicon: '/favicon.svg',
      defaultLocale: 'root',
      locales: {
        root: {
          label: '简体中文',
          lang: 'zh-CN',
        },
      },
      social: [
        {
          icon: 'github',
          label: 'GitHub',
          href: 'https://github.com/xinghang-ee-cs/dev-runtime-skill',
        },
      ],
      editLink: {
        baseUrl: 'https://github.com/xinghang-ee-cs/dev-runtime-skill/edit/main/',
      },
      customCss: ['./src/styles/custom.css'],
      sidebar: [
        {
          label: '开始使用',
          items: [
            { label: '教程首页', slug: 'index' },
            { label: '安装 Runtime Skills', slug: 'tutorials/getting-started' },
            { label: '选择正确的 Skill', slug: 'tutorials/choosing-a-skill' },
          ],
        },
        {
          label: '工作流教程',
          items: [
            { label: '完整开发流程', slug: 'tutorials/full-workflow' },
          ],
        },
        {
          label: '参考',
          items: [
            { label: 'Skill 目录', slug: 'reference/skill-catalog' },
            { label: '编写新教程', slug: 'authoring/writing-tutorials' },
          ],
        },
      ],
    }),
  ],
});
