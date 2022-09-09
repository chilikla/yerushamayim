import { terser } from 'rollup-plugin-terser';
import { nodeResolve } from '@rollup/plugin-node-resolve';
import commonjs from '@rollup/plugin-commonjs';
import images from '@rollup/plugin-image';

export default [
  {
    input: 'src/card/yerushamayim-card-local.js',
    output: {
      file: 'dist/www/yerushamayim-card-local.js',
      format: 'iife',
      plugins: terser({
        ecma: 2020,
        mangle: { toplevel: true },
        compress: {
          module: true,
          toplevel: true,
          unsafe_arrows: true,
          drop_console: false,
          drop_debugger: true
        },
        output: { quote_style: 1 }
      })
    },
    plugins: [
      nodeResolve(),
      commonjs(),
      images()
    ]
  },
  {
    input: 'src/card/yerushamayim-card.js',
    output: {
      file: 'dist/www/yerushamayim-card.js',
    },
    external: ['https://unpkg.com/lit-element@2.0.1/lit-element.js?module']
  },
  {
    input: 'src/sensor/__init__.py',
    output: {
      file: 'dist/custom_component/yerushamayim/__init__.py',
    }
  },
  {
    input: 'src/sensor/sensor.py',
    output: {
      file: 'dist/custom_component/yerushamayim/sensor.py',
    }
  },
  {
    input: 'src/sensor/manifest.json',
    output: {
      file: 'dist/custom_component/yerushamayim/manifest.json',
    }
  }
];