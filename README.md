# AI 导航站（Apple Style 单页面）

这是一个使用 **HTML5 + Tailwind CSS（CDN）** 搭建的单页面 AI 导航站，具有苹果风极简设计和响应式布局。

## 项目结构

- `index.html`：主页面文件（包含布局、样式和交互逻辑）
- `README.md`：项目说明（本文件）

> 说明：Tailwind 通过 CDN 引入，不需要额外打包或构建工具，直接用浏览器打开即可预览。

## 启动与预览方式

### 方式一：直接用浏览器打开（最简单）

1. 在资源管理器中打开目录：  
   `d:\AI-agent\other-work\prompt_tool\`
2. 双击 `index.html`，用浏览器打开即可查看页面。

> 这种方式足够用于本地查看与调试静态页面。

### 方式二：通过本地静态服务器（推荐，用于后续扩展）

如果你有安装 Python（3.x）：

1. 在该目录打开终端 / PowerShell：

   ```powershell
   cd d:\AI-agent\other-work\prompt_tool
   ```

2. 启动简易 HTTP 服务器：

   ```powershell
   python -m http.server 8080
   ```

3. 打开浏览器访问：

   ```text
   http://localhost:8080/index.html
   ```

### 方式三：使用任意静态服务器工具

如果你有 Node.js，也可以使用 `serve` 等工具：

```bash
npx serve .
```

然后在浏览器中打开提示的本地地址即可。

## 后续如何批量生成卡片

- 在 `index.html` 中找到注释：

  ```html
  <!-- 卡片模板（开始） -->
  ...
  <!-- 卡片模板（结束） -->
  ```

- 这一区域就是 **卡片模板区域**，你可以：
  - 用 Python 读取一个数据源（如 JSON/CSV）
  - 循环生成 `<article class="card-item ...">...</article>` 片段
  - 将生成的 HTML 插入替换这部分内容

页面的整体布局和交互（分类过滤、响应式 Sidebar 等）不需要修改。

