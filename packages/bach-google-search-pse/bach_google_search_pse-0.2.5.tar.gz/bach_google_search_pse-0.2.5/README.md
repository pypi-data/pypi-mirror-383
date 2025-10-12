# Bach Google Search PSE

Google 可编程搜索引擎 MCP 服务器 - 为 AI 助手提供强大的网页搜索和内容获取能力

## 🌟 功能特性

- 🔍 **关键词搜索**: 通过 Google PSE 进行智能搜索
- 🌐 **网页内容获取**: 提供 URL 链接获取完整网页内容
- 📄 **PDF 解析**: 支持 PDF 链接的内容提取和解析

## 🚀 快速启动（推荐）

### 使用 UVX 一键启动

```bash
uvx bach-google-search-pse
```

### 在 Cursor/Cherry Studio 中配置

```json
{
  "mcpServers": {
    "google-search-pse": {
      "command": "uvx",
      "args": ["bach-google-search-pse"]
    }
  }
}
```

## 📦 安装方式

### 方式一：直接使用 UVX（推荐）

无需安装，直接运行：

```bash
uvx bach-google-search-pse
```

### 方式二：通过 pip 安装

```bash
pip install bach-google-search-pse
bach-google-search-pse
```

## 🛠️ 可用工具

### 1. getContentBySubject

通过关键词搜索获取相关内容

**参数**：

- `subject` (string): 搜索关键词

### 2. getContentByUrl

通过 URL 获取网页内容

**参数**：

- `url` (string): 网页链接地址

### 3. getContentByPdfUrl

通过 PDF URL 获取 PDF 文档内容

**参数**：

- `pdfUrl` (string): PDF 文件链接地址

## 📚 使用示例

在 AI 助手中使用：

```
"帮我搜索最新的人工智能新闻"
"获取这个网页的内容：https://example.com"
"解析这个 PDF 文件：https://example.com/document.pdf"
```

## 🔗 相关链接

- **PyPI 包地址**: https://pypi.org/project/bach-google-search-pse/
- **GitHub 仓库**: https://github.com/BACH-AI-Tools/GoogleSearchPSEMCP
- **问题反馈**: https://github.com/BACH-AI-Tools/GoogleSearchPSEMCP/issues

## 📄 许可证

MIT License

## 👨‍💻 作者

bachstudio
